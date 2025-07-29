from fastapi import Depends
from typing import List, Optional, Tuple, Any, Dict
from beanie import PydanticObjectId
from app.models.organization.region import Region
from app.schemas.organization.location import RegionCreate, RegionUpdate
from app.services.crud_services import CRUD
from app.constants.sort_order import SortOrder
from app.services.auth import get_current_company

crud = CRUD(Region)


async def create_region(data: RegionCreate, user_tz: str) -> Region:
    res = await crud.create(data, unique_fields=["name", "code"])
    return res


async def get_region(
    region_id: str,
    company_id:PydanticObjectId = Depends(get_current_company),
    include_flag: bool = False
) -> Region:
    res = await crud.get_by_id(region_id, company_id, include_flag)
    return res


async def list_regions(
    company_id:PydanticObjectId = Depends(get_current_company),
    skip: int = 0,
    limit: int = 50,
    include_deleted: bool = False,
    filters: Optional[Dict[str, Any]] = None,
    search: Optional[Dict[str, Any]] = None,
    sort_order: Optional[List[Tuple[str, SortOrder]]] = None,
    exact_match: Optional[bool] = False
) -> List[Region]:

    res = await crud.list(
        company_id,
        skip,
        limit,
        include_deleted,
        filters=filters,
        sort=sort_order,
        search=search,
        exact_match=exact_match if exact_match is not None else False
    )
    return res


async def update_region(
    region_id: str,
    data: RegionUpdate,     
    company_id:PydanticObjectId = Depends(get_current_company)
) -> Region:
    res = await crud.update(region_id, company_id, data, unique_fields=["name", "code"])
    return res

async def soft_delete_region(
    region_id: str,
    company_id:PydanticObjectId = Depends(get_current_company)
) -> None:
    """Soft-delete a region."""
    res = await crud.update_flags(region_id, company_id,  fields=[("is_deleted", True), ("is_active", False)])
    return res

async def delete_region(
    region_id: str,
    company_id:PydanticObjectId = Depends(get_current_company)
) -> None:
    """hard-delete a region."""
    res = await crud.delete(region_id, company_id, hard_delete= True)
    return res

async def restore_region(
    region_id: str,
    company_id:PydanticObjectId = Depends(get_current_company)
) -> Region:
    """Restore a previously soft-deleted region."""
    res = await crud.update_flags(region_id, company_id, fields=[("is_deleted", False), ("is_active", True)])
    return res


async def disable_region(
    region_id: str,
    company_id:PydanticObjectId = Depends(get_current_company)
) -> None:
    """Deactivate a region."""
    res = await crud.update_flags(region_id, company_id, [("is_active", False)])
    return res


async def activate_region(
    region_id: str,
    company_id:PydanticObjectId = Depends(get_current_company)
) -> Region:
    """Restore a previously deactivated region."""
    res = await crud.update_flags(region_id, company_id, [("is_active", True)])
    return res
