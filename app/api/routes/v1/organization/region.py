from fastapi import APIRouter, Query, Path, status
from typing import List, Optional, Dict, Any

from app.utils.parse_sort_clause import parse_sort

from app.schemas.organization.location import (
    RegionCreate, RegionUpdate, RegionResponse
)
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


# GET /regions/?skip=0&limit=20&include_deleted=false&name=East%20Region
# &search_name=Reg&exact_match=false&sort=name,-code

@router.get(
    "/",
    response_model=List[RegionResponse],
    summary="List regions with optional filters and sorting",
)
async def get_regions_route(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    include_deleted: bool = Query(
        False, description="Include soft-deleted regions"
    ),
    name: Optional[str] = Query(None, description="Exact match on name"),
    code: Optional[str] = Query(None, description="Exact match on code"),
    created_by: Optional[str] = Query(None),
    updated_by: Optional[str] = Query(None),
    sort: Optional[str] = Query(
        None,
        description="Comma-separated fields to sort by; prefix '-' for DESC. E.g. `sort=name,-code`"
    ),

    # Search filters (pattern or exact based on flag)
    search_name: Optional[str] = Query(None, description="Search term for name"),
    search_code: Optional[str] = Query(None, description="Search term for code"),
    exact_match: bool = Query(
        True, description="Flag to require exact match (true) vs pattern search (false)"
    ),
):
    sort_params = parse_sort(sort)

    # Build filters dict
    filters: Dict[str, Any] = {}
    if name is not None:
        filters["name"] = name
    if created_by is not None:
        filters["created_by"] = created_by
    if code is not None:
        filters["code"] = code
    if updated_by is not None:
        filters["updated_by"] = updated_by

    # Build search dict
    search: Dict[str, str] = {}
    if search_name:
        search["name"] = search_name
    if search_code:
        search["code"] = search_code

    return await list_regions(
        skip=skip,
        limit=limit,
        include_deleted=include_deleted,
        filters=filters or None,
        search=search or None,
        exact_match=exact_match,
        sort_order=sort_params or None,
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
    payload: RegionUpdate = ...,
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