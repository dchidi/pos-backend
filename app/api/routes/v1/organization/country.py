from fastapi import APIRouter, Query, Path, status
from typing import List, Optional

from app.schemas.organization.location import (
    CountryCreate, CountryUpdate, CountryResponse
)
from app.services.organization.country import (
    create_country, get_country, list_countries,
    update_country, delete_country, restore_country,
    disable_country, activate_country
)

router = APIRouter()


@router.post(
    "/",
    response_model=CountryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new country",
)
async def create_country_route(payload: CountryCreate):
    return await create_country(payload)


@router.get(
    "/",
    response_model=List[CountryResponse],
    summary="List countrys with optional filters",
)
async def get_countrys_route(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    include_deleted: bool = Query(
        False, description="Include soft-deleted countrys"
    ),
    name: Optional[str] = Query(
        None, description="Exact match on country name"
    ),
    company_id: Optional[str] = Query(
        None, description="Filter by owning company ID"
    ),
    category_id: Optional[str] = Query(
        None, description="Filter by associated category ID"
    ),
):
    return await list_countries(
        skip,
        limit,
        include_deleted,
        name,
        company_id,
        category_id,
    )


@router.get(
    "/{country_id}",
    response_model=CountryResponse,
    summary="Get a single country by ID",
)
async def get_country_route(
    country_id: str = Path(..., description="Country ObjectId"),
    include_deleted: bool = Query(
        False, description="Include if the country is soft-deleted"
    ),
):
    return await get_country(country_id, include_deleted)


@router.put(
    "/{country_id}",
    response_model=CountryResponse,
    summary="Update an existing country",
)
async def update_country_route(
    country_id: str = Path(..., description="Country ObjectId"),
    payload: CountryUpdate = ...,
):
    return await update_country(country_id, payload)


@router.delete(
    "/{country_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft-delete a country",
)
async def delete_country_route(
    country_id: str = Path(..., description="Country ObjectId"),
):
    await delete_country(country_id)


@router.patch(
    "/{country_id}/restore",
    response_model=CountryResponse,
    summary="Restore a soft-deleted country",
)
async def restore_country_route(
    country_id: str = Path(..., description="Country ObjectId"),
):
    return await restore_country(country_id)


@router.patch(
    "/{country_id}/disable",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deactivate a country",
)
async def disable_country_route(
    country_id: str = Path(..., description="Country ObjectId"),
):
    await disable_country(country_id)


@router.patch(
    "/{country_id}/activate",
    response_model=CountryResponse,
    summary="Activate a disabled country",
)
async def activate_country_route(
    country_id: str = Path(..., description="Country ObjectId"),
):
    return await activate_country(country_id)