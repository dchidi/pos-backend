from typing import List, Optional
from beanie import PydanticObjectId
from app.models.organization.country import Country
from app.schemas.organization.location import LocationCreate, LocationUpdate
from app.services.exceptions import NotFoundError, AlreadyExistsError, ValidationError


async def create_country(data: LocationCreate) -> Country:
    """Create a new country, enforcing business rules."""
    if not (data.name.strip() or data.name.strip()):
        raise ValidationError("Country name or code must not be empty")
    # Unique name check
    existing_country = await Country.find_one({"code":data.code})
    if existing_country:
        raise AlreadyExistsError(f"Country '{data.name}' or '{data.code}' already exists")
    country = Country(**data.model_dump())
    await country.insert()
    return country

async def get_country(country_id: str, include_flag: bool = False) -> Country:
    """Retrieve a country by ID, optionally including deleted ones."""
    try:
        oid = PydanticObjectId(country_id)
    except Exception:
        raise NotFoundError(f"Invalid country ID '{country_id}'")
    country = await Country.get(oid)
    if not country or (country.is_deleted and not include_flag):
        raise NotFoundError(f"Country '{country_id}' not found or deleted")
    return country

async def list_countries(
    skip: int = 0,
    limit: int = 50,
    include_deleted: bool = False,
    name: Optional[str] = None,
    code: Optional[str] = None,
    created_by: Optional[str] = None,    
    updated_by: Optional[str] = None,
) -> List[Country]:
    """List countries with optional filters and deletion flag."""
    qb = Country.find()
    # Soft-delete filter
    if not include_deleted:
        qb = qb.find(Country.is_active == True, Country.is_deleted == False)
    # Name filter
    if name:
        qb = qb.find(Country.name == name)
    # Cpde filter
    if code:
        qb = qb.find(Country.code == code)
    # created by filter
    if created_by:
        qb = qb.find({'created_by': created_by})

    if updated_by:
        qb = qb.find({'updated_by': updated_by})
    return await qb.skip(skip).limit(limit).to_list()

async def update_country(country_id: str, data: LocationUpdate) -> Country:
    """Update fields on an existing country."""
    country = await get_country(country_id)
    update_data = data.model_dump(exclude_unset=True)
    # Name validations
    if 'name' in update_data or 'code' in update_data:
        if not update_data['name'].strip():
            raise ValidationError("Country name must not be empty")
        
        if 'name' in update_data or 'code' in update_data:
            # Check for conflicts in name OR code
            existing = await Country.find_one({
                "$or": [
                    {"name": update_data.get('name'), "_id": {"$ne": country.id}},
                    {"code": update_data.get('code'), "_id": {"$ne": country.id}},
                ]
            })
            if existing:
                conflict_field = "name" if existing.name == update_data.get('name') else "code"
                raise AlreadyExistsError(
                    f"Country {conflict_field} '{update_data[conflict_field]}' already exists"
                )
        
    for field, val in update_data.items():
        setattr(country, field, val)
    await country.replace()
    return country

async def delete_country(country_id: str) -> None:
    """Soft-delete a country."""
    country = await get_country(country_id)
    country.is_active = False
    country.is_deleted = True
    await country.replace()

async def restore_country(country_id: str) -> Country:
    """Restore a previously soft-deleted country."""
    country = await get_country(country_id, include_flag=True)
    if not country.is_deleted:
        raise ValidationError(f"Country '{country_id}' is not deleted")
    country.is_deleted = False
    country.is_active = True
    await country.replace()
    return country


async def disable_country(country_id: str) -> None:
    """Deactivate a country."""
    country = await get_country(country_id)
    country.is_active = False
    await country.replace()


async def activate_country(country_id: str) -> Country:
    """Restore a previously soft-deleted country."""
    country = await get_country(country_id, include_flag=True)
    if country.is_active:
        raise ValidationError(f"Country '{country_id}' is not disabled")
    country.is_active = True
    await country.replace()
    return country
