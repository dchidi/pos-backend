from typing import List, Optional, Tuple, Any, Dict
from beanie import PydanticObjectId
from app.models.organization.region import Region
from app.schemas.organization.location import RegionCreate, RegionUpdate
from app.services.exceptions import (
     AlreadyExistsError, ValidationError
)
from app.services.crud_services import CRUD

from app.constants.sort_order import SortOrder

crud = CRUD(Region)


async def create_region(data: RegionCreate) -> Region:
    res = await crud.create(data, unique_fields=["name", "code"])
    return res


async def get_region(region_id: str, include_flag: bool = False) -> Region:
    res = await crud.get_by_id(region_id, include_flag)
    return res


async def list_regions(
    skip: int = 0,
    limit: int = 50,
    include_deleted: bool = False,
    filters: Optional[Dict[str, Any]] = None,
    search: Optional[Dict[str, Any]] = None,
    sort_order: Optional[List[Tuple[str, SortOrder]]] = None,
    exact_match: Optional[bool] = False
) -> List[Region]:

    res = await crud.list(
        skip,
        limit,
        include_deleted,
        filters=filters,
        sort=sort_order,
        search=search,
        exact_match=exact_match if exact_match is not None else False
    )
    return res


async def update_region(region_id: str, data: RegionUpdate) -> Region:
    """Update fields on an existing region."""
    region = await get_region(region_id)
    update_data = data.model_dump(exclude_unset=True)
    # Name validations
    if 'name' in update_data or 'code' in update_data:
        if not update_data['name'].strip():
            raise ValidationError("Region name must not be empty")
        
        if 'name' in update_data or 'code' in update_data:
            # Check for conflicts in name OR code
            existing = await Region.find_one({
                "$or": [
                    {"name": update_data.get('name'), "_id": {"$ne": region.id}},
                    {"code": update_data.get('code'), "_id": {"$ne": region.id}},
                ]
            })
            if existing:
                conflict_field = "name" if existing.name == update_data.get('name') else "code"
                raise AlreadyExistsError(
                    f"Region {conflict_field} '{update_data[conflict_field]}' already exists"
                )
        
    for field, val in update_data.items():
        setattr(region, field, val)
    await region.replace()
    return region

async def delete_region(region_id: str) -> None:
    """Soft-delete a region."""
    region = await get_region(region_id)
    region.is_active = False
    region.is_deleted = True
    await region.replace()

async def restore_region(region_id: str) -> Region:
    """Restore a previously soft-deleted region."""
    region = await get_region(region_id, include_flag=True)
    if not region.is_deleted:
        raise ValidationError(f"Region '{region_id}' is not deleted")
    region.is_deleted = False
    region.is_active = True
    await region.replace()
    return region


async def disable_region(region_id: str) -> None:
    """Deactivate a region."""
    region = await get_region(region_id)
    region.is_active = False
    await region.replace()


async def activate_region(region_id: str) -> Region:
    """Restore a previously soft-deleted region."""
    region = await get_region(region_id, include_flag=True)
    if region.is_active:
        raise ValidationError(f"Region '{region_id}' is not disabled")
    region.is_active = True
    await region.replace()
    return region
