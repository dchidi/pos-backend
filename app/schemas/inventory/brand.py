from pydantic import BaseModel, Field, AnyUrl
from datetime import datetime
from typing import List, Optional
from app.schemas.base import BaseResponse
from beanie import PydanticObjectId

class BrandBase(BaseModel):
    name: str = Field(..., example="Golden Crust")
    description: Optional[str] = Field(None, example="Premium bakery brand")
    logo_url: Optional[AnyUrl] = Field(None, example="https://example.com/logo.png")
    category_ids: List[PydanticObjectId] = Field(default_factory=list, example=["64" * 12])
    company_id: Optional[PydanticObjectId] = Field(
        None,
        description="The company or manufacturer that owns the brand"
    )

class BrandCreate(BrandBase):
    """Schema for creating a brand."""
    pass

class BrandUpdate(BaseModel):
    """Schema for updating a brand; all fields optional."""
    name: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[AnyUrl] = None
    category_ids: Optional[List[PydanticObjectId]] = None
    company_id: Optional[PydanticObjectId] = None

class BrandResponse(BrandBase, BaseResponse):
    """Schema for reading brand data."""
    created_at: datetime
    updated_at: datetime
    is_active: bool
    is_deleted: bool
