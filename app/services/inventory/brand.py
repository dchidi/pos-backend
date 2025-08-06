from typing import List, Optional
from beanie import PydanticObjectId

from app.models.inventory.brand import Brand

from app.schemas.inventory.brand import BrandCreate, BrandUpdate

from app.services.exceptions import NotFoundError, AlreadyExistsError, ValidationError


async def create_brand(data: BrandCreate) -> Brand:
    """Create a new brand, enforcing business rules."""
    if not data.name.strip():
        raise ValidationError("Brand name must not be empty")
    # Unique name check
    existing_brand = await Brand.find_one({"name":data.name})
    if existing_brand:
        raise AlreadyExistsError(f"Brand '{data.name}' already exists")
    brand = Brand(**data.model_dump())
    await brand.insert()
    return brand

async def get_brand(brand_id: str, include_flag: bool = False) -> Brand:
    """Retrieve a brand by ID, optionally including deleted ones."""
    try:
        oid = PydanticObjectId(brand_id)
    except Exception:
        raise NotFoundError(f"Invalid brand ID '{brand_id}'")
    brand = await Brand.get(oid)
    if not brand or (brand.is_deleted and not include_flag):
        raise NotFoundError(f"Brand '{brand_id}' not found or deleted")
    return brand

async def list_brands(
    skip: int = 0,
    limit: int = 50,
    include_deleted: bool = False,
    name: Optional[str] = None,
    company_id: Optional[str] = None,
    category_id: Optional[str] = None,
) -> List[Brand]:
    """List brands with optional filters and deletion flag."""
    qb = Brand.find()
    # Soft-delete filter
    if not include_deleted:
        qb = qb.find(Brand.is_active == True, Brand.is_deleted == False)
    # Name filter
    if name:
        qb = qb.find(Brand.name == name)
    # Company filter
    if company_id:
        qb = qb.find(Brand.company_id == company_id)
    # Category filter
    if category_id:
        qb = qb.find({'category_ids': category_id})
    return await qb.skip(skip).limit(limit).to_list()

async def update_brand(brand_id: str, data: BrandUpdate) -> Brand:
    """Update fields on an existing brand."""
    brand = await get_brand(brand_id)
    update_data = data.model_dump(exclude_unset=True)
    # Name validations
    if 'name' in update_data:
        if not update_data['name'].strip():
            raise ValidationError("Brand name must not be empty")
        
        existing = await Brand.find_one({
            "name": update_data['name'],
            "_id": {"$ne": brand.id}  # Exclude current brand
        })
        if existing:
            raise AlreadyExistsError(f"Brand '{update_data['name']}' already exists")
        
    for field, val in update_data.items():
        setattr(brand, field, val)
    await brand.replace()
    return brand

async def delete_brand(brand_id: str) -> None:
    """Soft-delete a brand."""
    brand = await get_brand(brand_id)
    brand.is_active = False
    brand.is_deleted = True
    await brand.replace()

async def restore_brand(brand_id: str) -> Brand:
    """Restore a previously soft-deleted brand."""
    brand = await get_brand(brand_id, include_flag=True)
    if not brand.is_deleted:
        raise ValidationError(f"Brand '{brand_id}' is not deleted")
    brand.is_deleted = False
    brand.is_active = True
    await brand.replace()
    return brand


async def disable_brand(brand_id: str) -> None:
    """Deactivate a brand."""
    brand = await get_brand(brand_id)
    brand.is_active = False
    await brand.replace()


async def activate_brand(brand_id: str) -> Brand:
    """Restore a previously soft-deleted brand."""
    brand = await get_brand(brand_id, include_flag=True)
    if brand.is_active:
        raise ValidationError(f"Brand '{brand_id}' is not disabled")
    brand.is_active = True
    await brand.replace()
    return brand
