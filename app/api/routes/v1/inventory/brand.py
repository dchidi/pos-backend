# routers/brand.py
from fastapi import APIRouter, HTTPException, status
from typing import List
from app.models.inventory.brand import Brand
from app.schemas.inventory.brand import BrandCreate, BrandUpdate, BrandResponse

router = APIRouter(prefix="/brands", tags=["Brands"])


@router.post("/", response_model=BrandResponse, status_code=status.HTTP_201_CREATED)
async def create_brand(payload: BrandCreate):
    brand = Brand(**payload.dict())
    await brand.insert()
    return brand


@router.get("/", response_model=List[BrandResponse])
async def get_all_brands():
    return await Brand.find_all().to_list()


@router.get("/{brand_id}", response_model=BrandResponse)
async def get_brand_by_id(brand_id: str):
    brand = await Brand.get(brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    return brand


@router.put("/{brand_id}", response_model=BrandResponse)
async def update_brand(brand_id: str, payload: BrandUpdate):
    brand = await Brand.get(brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    
    brand_data = payload.dict(exclude_unset=True)
    for key, value in brand_data.items():
        setattr(brand, key, value)
    await brand.save()
    return brand


@router.delete("/{brand_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_brand(brand_id: str):
    brand = await Brand.get(brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    await brand.delete()
