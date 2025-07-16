
from pydantic import BaseModel, Field, AnyUrl
from typing import Optional, List
from datetime import datetime

class CategoryBase(BaseModel):
    name: str
    code: str
    parent_id: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True
    image_url: Optional[AnyUrl] = None


class CategoryCreate(CategoryBase):
    """Schema for creating a new category."""
    pass


class CategoryUpdate(BaseModel):
    """Schema for updating an existing category."""
    name: Optional[str] = None
    code: Optional[str] = None
    parent_id: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    image_url: Optional[AnyUrl] = None


class CategoryResponse(CategoryBase):
    """Schema for reading category data."""
    id: str = Field(..., alias="_id")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CategoryListResponse(BaseModel):
    """Paginated response for categories."""
    total: int
    items: List[CategoryResponse]