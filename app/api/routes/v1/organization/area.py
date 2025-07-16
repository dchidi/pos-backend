from fastapi import APIRouter, Query, Path, status
from typing import List, Optional

from app.schemas.organization.location import AreaCreate, LocationUpdate, AreaResponse
from app.services.organization.area import (
    create_area,
    get_area,
    list_areas,
    update_area,
    delete_area,
    restore_area,
    disable_area,
    activate_area
)
# from app.api.routes.v1.handle_errors import handle_service_errors


router = APIRouter()


@router.post(
    "/",
    response_model=AreaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new area",
)
async def create_area_route(payload: AreaCreate):
    return await create_area(payload)


@router.get(
    "/",
    response_model=List[AreaResponse],
    summary="List areas with optional filters",
)
async def get_areas_route(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    include_deleted: bool = Query(
        False, description="Include soft-deleted areas"
    ),
    name: Optional[str] = Query(
        None, description="Exact match on area name"
    ),
    company_id: Optional[str] = Query(
        None, description="Filter by owning company ID"
    ),
    category_id: Optional[str] = Query(
        None, description="Filter by associated category ID"
    ),
):
    return await list_areas(
        skip,
        limit,
        include_deleted,
        name,
        company_id,
        category_id,
    )


@router.get(
    "/{area_id}",
    response_model=AreaResponse,
    summary="Get a single area by ID",
)
async def get_area_route(
    area_id: str = Path(..., description="Brand ObjectId"),
    include_deleted: bool = Query(
        False, description="Include if the area is soft-deleted"
    ),
):
    return await get_area(area_id, include_deleted)


@router.put(
    "/{area_id}",
    response_model=AreaResponse,
    summary="Update an existing area",
)
async def update_area_route(
    area_id: str = Path(..., description="Brand ObjectId"),
    payload: LocationUpdate = ...,
):
    return await update_area(area_id, payload)


@router.delete(
    "/{area_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft-delete a area",
)
async def delete_area_route(
    area_id: str = Path(..., description="Brand ObjectId"),
):
    await delete_area(area_id)


@router.patch(
    "/{area_id}/restore",
    response_model=AreaResponse,
    summary="Restore a soft-deleted area",
)
async def restore_area_route(
    area_id: str = Path(..., description="Brand ObjectId"),
):
    return await restore_area(area_id)


@router.patch(
    "/{area_id}/disable",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deactivate a area",
)
async def disable_area_route(
    area_id: str = Path(..., description="Brand ObjectId"),
):
    await disable_area(area_id)


@router.patch(
    "/{area_id}/activate",
    response_model=AreaResponse,
    summary="Activate a disabled area",
)
async def restore_area_route(
    area_id: str = Path(..., description="Brand ObjectId"),
):
    return await activate_area(area_id)