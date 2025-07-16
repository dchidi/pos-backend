from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.schemas.base import BaseResponse
from app.schemas import PyObjectId

class LocationBase(BaseModel):
    name: str = Field(..., example="Delta State")
    code: str = Field(..., example="DLST")
    created_by: Optional[PyObjectId] = Field(None, example="64f95b0c2ab5ec9e0b22c77f")
    updated_by: Optional[PyObjectId] = Field(None, example="64f95b0c2ab5ec9e0b22c77f")


class LocationCreate(LocationBase):
    """Base schema for creating a location entry (e.g., Country, Region, Area)."""
    pass


class RegionCreate(LocationCreate):
    country_id: Optional[PyObjectId] = Field(None, example="64f95b0c2ab5ec9e0b22c77f")


class AreaCreate(RegionCreate):
    region_id: Optional[PyObjectId] = Field(None, example="64f95b0c2ab5ec9e0b22c77f")


class StateCreate(AreaCreate):    
    area_id: Optional[PyObjectId] = Field(None, example="64f95b0c2ab5ec9e0b22c77f")


class LocationUpdate(BaseModel):
    """Schema for updating any location type."""
    name: Optional[str] = Field(None)
    code: Optional[str] = Field(None)
    country_id: Optional[PyObjectId] = Field(None)
    region_id: Optional[PyObjectId] = Field(None)
    area_id: Optional[PyObjectId] = Field(None)
    created_by: Optional[PyObjectId] = Field(None)
    updated_by: Optional[PyObjectId] = Field(None)


class LocationResponse(LocationBase, BaseResponse):
    created_at: datetime
    updated_at: datetime
    is_active: bool
    is_deleted: bool


class RegionResponse(LocationResponse):
    country_id: Optional[PyObjectId] = Field(None, example="64f95b0c2ab5ec9e0b22c77f")


class AreaResponse(RegionResponse):
    region_id: Optional[PyObjectId] = Field(None, example="64f95b0c2ab5ec9e0b22c77f")


class StateResponse(AreaResponse):    
    area_id: Optional[PyObjectId] = Field(None, example="64f95b0c2ab5ec9e0b22c77f")
