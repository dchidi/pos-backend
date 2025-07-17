from typing import List, Optional
from beanie import PydanticObjectId
from app.models.organization.area import Area
from app.schemas.organization.location import AreaCreate, AreaUpdate
from app.services.exceptions import (
    NotFoundError, AlreadyExistsError, ValidationError
)


async def create_area(data: AreaCreate) -> Area:
    """Create a new area, enforcing business rules."""
    if not (data.name.strip() or data.name.strip()):
        raise ValidationError("Area name or code must not be empty")
    # Unique name check
    existing_area = await Area.find_one({"code":data.code})
    if existing_area:
        raise AlreadyExistsError(f"Area '{data.name}' or '{data.code}' already exists")
    area = Area(**data.model_dump())
    await area.insert()
    return area

async def get_area(area_id: str, include_flag: bool = False) -> Area:
    """Retrieve a area by ID, optionally including deleted ones."""
    try:
        oid = PydanticObjectId(area_id)
    except Exception:
        raise NotFoundError(f"Invalid area ID '{area_id}'")
    area = await Area.get(oid)
    if not area or (area.is_deleted and not include_flag):
        raise NotFoundError(f"Area '{area_id}' not found or deleted")
    return area

async def list_areas(
    skip: int = 0,
    limit: int = 50,
    include_deleted: bool = False,
    name: Optional[str] = None,
    code: Optional[str] = None,
    created_by: Optional[str] = None,    
    updated_by: Optional[str] = None,
) -> List[Area]:
    """List areas with optional filters and deletion flag."""
    qb = Area.find()
    # Soft-delete filter
    if not include_deleted:
        qb = qb.find(Area.is_active == True, Area.is_deleted == False)
    # Name filter
    if name:
        qb = qb.find(Area.name == name)
    # Cpde filter
    if code:
        qb = qb.find(Area.code == code)
    # created by filter
    if created_by:
        qb = qb.find({'created_by': created_by})

    if updated_by:
        qb = qb.find({'updated_by': updated_by})
    return await qb.skip(skip).limit(limit).to_list()

async def update_area(area_id: str, data: AreaUpdate) -> Area:
    """Update fields on an existing area."""
    area = await get_area(area_id)
    update_data = data.model_dump(exclude_unset=True)
    # Name validations
    if 'name' in update_data or 'code' in update_data:
        if not update_data['name'].strip():
            raise ValidationError("Area name must not be empty")
        
        if 'name' in update_data or 'code' in update_data:
            # Check for conflicts in name OR code
            existing = await Area.find_one({
                "$or": [
                    {"name": update_data.get('name'), "_id": {"$ne": area.id}},
                    {"code": update_data.get('code'), "_id": {"$ne": area.id}},
                ]
            })
            if existing:
                conflict_field = "name" if existing.name == update_data.get('name') else "code"
                raise AlreadyExistsError(
                    f"Area {conflict_field} '{update_data[conflict_field]}' already exists"
                )
        
    for field, val in update_data.items():
        setattr(area, field, val)
    await area.replace()
    return area

async def delete_area(area_id: str) -> None:
    """Soft-delete a area."""
    area = await get_area(area_id)
    area.is_active = False
    area.is_deleted = True
    await area.replace()

async def restore_area(area_id: str) -> Area:
    """Restore a previously soft-deleted area."""
    area = await get_area(area_id, include_flag=True)
    if not area.is_deleted:
        raise ValidationError(f"Area '{area_id}' is not deleted")
    area.is_deleted = False
    area.is_active = True
    await area.replace()
    return area


async def disable_area(area_id: str) -> None:
    """Deactivate a area."""
    area = await get_area(area_id)
    area.is_active = False
    await area.replace()


async def activate_area(area_id: str) -> Area:
    """Restore a previously soft-deleted area."""
    area = await get_area(area_id, include_flag=True)
    if area.is_active:
        raise ValidationError(f"Area '{area_id}' is not disabled")
    area.is_active = True
    await area.replace()
    return area
