from fastapi import APIRouter, Query, Path, status
from typing import List, Optional

from app.schemas.organization.location import RegionCreate, LocationUpdate, RegionResponse
from app.services.organization.region import (
    create_region,
    get_region,
    list_regions,
    update_region,
    delete_region,
    restore_region,
    disable_region,
    activate_region
)
# from app.api.routes.v1.handle_errors import handle_service_errors


router = APIRouter()


@router.post(
    "/",
    response_model=RegionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new region",
)
async def create_region_route(payload: RegionCreate):
    return await create_region(payload)


@router.get(
    "/",
    response_model=List[RegionResponse],
    summary="List regions with optional filters",
)
async def get_regions_route(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    include_deleted: bool = Query(
        False, description="Include soft-deleted regions"
    ),
    name: Optional[str] = Query(
        None, description="Exact match on region name"
    ),
    company_id: Optional[str] = Query(
        None, description="Filter by owning company ID"
    ),
    category_id: Optional[str] = Query(
        None, description="Filter by associated category ID"
    ),
):
    return await list_regions(
        skip,
        limit,
        include_deleted,
        name,
        company_id,
        category_id,
    )


@router.get(
    "/{region_id}",
    response_model=RegionResponse,
    summary="Get a single region by ID",
)
async def get_region_route(
    region_id: str = Path(..., description="Brand ObjectId"),
    include_deleted: bool = Query(
        False, description="Include if the region is soft-deleted"
    ),
):
    return await get_region(region_id, include_deleted)


@router.put(
    "/{region_id}",
    response_model=RegionResponse,
    summary="Update an existing region",
)
async def update_region_route(
    region_id: str = Path(..., description="Brand ObjectId"),
    payload: LocationUpdate = ...,
):
    return await update_region(region_id, payload)


@router.delete(
    "/{region_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft-delete a region",
)
async def delete_region_route(
    region_id: str = Path(..., description="Brand ObjectId"),
):
    await delete_region(region_id)


@router.patch(
    "/{region_id}/restore",
    response_model=RegionResponse,
    summary="Restore a soft-deleted region",
)
async def restore_region_route(
    region_id: str = Path(..., description="Brand ObjectId"),
):
    return await restore_region(region_id)


@router.patch(
    "/{region_id}/disable",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deactivate a region",
)
async def disable_region_route(
    region_id: str = Path(..., description="Brand ObjectId"),
):
    await disable_region(region_id)


@router.patch(
    "/{region_id}/activate",
    response_model=RegionResponse,
    summary="Activate a disabled region",
)
async def restore_region_route(
    region_id: str = Path(..., description="Brand ObjectId"),
):
    return await activate_region(region_id)