from typing import List, Optional
from beanie import PydanticObjectId
from app.models.organization.region import Region
from app.schemas.organization.location import RegionCreate, RegionUpdate
from app.services.exceptions import (
    NotFoundError, AlreadyExistsError, ValidationError
)
from app.services.crud_services import CRUD

crud = CRUD(Region)


async def create_region(data: RegionCreate) -> Region:
    res = await crud.create(data, unique_fields=["name", "code"])
    return res


async def get_region(region_id: str, include_flag: bool = False) -> Region:
    res = await crud.get_by_id(region_id, include_flag)
    return res
    # """Retrieve a region by ID, optionally including deleted ones."""
    # try:
    #     oid = PydanticObjectId(region_id)
    # except Exception:
    #     raise NotFoundError(f"Invalid region ID '{region_id}'")
    # region = await Region.get(oid)
    # if not region or (region.is_deleted and not include_flag):
    #     raise NotFoundError(f"Region '{region_id}' not found or deleted")
    # return region


async def list_regions(
    skip: int = 0,
    limit: int = 50,
    include_deleted: bool = False,
    name: Optional[str] = None,
    code: Optional[str] = None,
    created_by: Optional[str] = None,
    updated_by: Optional[str] = None,
) -> List[Region]:

    res = await crud.list(
        skip,
        limit,
        include_deleted,
        filters={
            "name": name, "code": code,
            "created_by": created_by, "updated_by": updated_by
        },
        # sort: Optional[List[Tuple[str, SortOrder]]] = None
    )
    return res
    # """List regions with optional filters and deletion flag."""
    # qb = Region.find()
    # # Soft-delete filter
    # if not include_deleted:
    #     qb = qb.find(Region.is_active == True, Region.is_deleted == False)
    # # Name filter
    # if name:
    #     qb = qb.find(Region.name == name)
    # # Cpde filter
    # if code:
    #     qb = qb.find(Region.code == code)
    # # created by filter
    # if created_by:
    #     qb = qb.find({'created_by': created_by})

    # if updated_by:
    #     qb = qb.find({'updated_by': updated_by})
    # return await qb.skip(skip).limit(limit).to_list()

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
