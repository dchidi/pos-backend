# schemas/brand.py
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional
from datetime import datetime


class BrandBase(BaseModel):
    name: str
    description: Optional[str] = None
    logo_url: Optional[HttpUrl] = None
    is_active: bool = True


class BrandCreate(BrandBase):
    pass


class BrandUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[HttpUrl] = None
    is_active: Optional[bool] = None


class BrandResponse(BrandBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True
