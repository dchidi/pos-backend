from fastapi import APIRouter, Query, Path, status
from typing import List, Optional

from app.schemas.inventory.brand import BrandCreate, BrandUpdate, BrandResponse
from app.services.inventory.brand import (
    create_brand,
    get_brand,
    list_brands,
    update_brand,
    delete_brand,
    restore_brand,
    disable_brand,
    activate_brand
)
# from app.api.routes.v1.handle_errors import handle_service_errors


router = APIRouter()


@router.post(
    "/",
    response_model=BrandResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new brand",
)
async def create_brand_route(payload: BrandCreate):
    return await create_brand(payload)


@router.get(
    "/",
    response_model=List[BrandResponse],
    summary="List brands with optional filters",
)
async def get_brands_route(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    include_deleted: bool = Query(
        False, description="Include soft-deleted brands"
    ),
    name: Optional[str] = Query(
        None, description="Exact match on brand name"
    ),
    company_id: Optional[str] = Query(
        None, description="Filter by owning company ID"
    ),
    category_id: Optional[str] = Query(
        None, description="Filter by associated category ID"
    ),
):
    return await list_brands(
        skip,
        limit,
        include_deleted,
        name,
        company_id,
        category_id,
    )


@router.get(
    "/{brand_id}",
    response_model=BrandResponse,
    summary="Get a single brand by ID",
)
async def get_brand_route(
    brand_id: str = Path(..., description="Brand ObjectId"),
    include_deleted: bool = Query(
        False, description="Include if the brand is soft-deleted"
    ),
):
    return await get_brand(brand_id, include_deleted)


@router.put(
    "/{brand_id}",
    response_model=BrandResponse,
    summary="Update an existing brand",
)
async def update_brand_route(
    brand_id: str = Path(..., description="Brand ObjectId"),
    payload: BrandUpdate = ...,
):
    return await update_brand(brand_id, payload)


@router.delete(
    "/{brand_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft-delete a brand",
)
async def delete_brand_route(
    brand_id: str = Path(..., description="Brand ObjectId"),
):
    await delete_brand(brand_id)


@router.patch(
    "/{brand_id}/restore",
    response_model=BrandResponse,
    summary="Restore a soft-deleted brand",
)
async def restore_brand_route(
    brand_id: str = Path(..., description="Brand ObjectId"),
):
    return await restore_brand(brand_id)


@router.patch(
    "/{brand_id}/disable",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deactivate a brand",
)
async def disable_brand_route(
    brand_id: str = Path(..., description="Brand ObjectId"),
):
    await disable_brand(brand_id)


@router.patch(
    "/{brand_id}/activate",
    response_model=BrandResponse,
    summary="Activate a disabled brand",
)
async def restore_brand_route(
    brand_id: str = Path(..., description="Brand ObjectId"),
):
    return await activate_brand(brand_id)