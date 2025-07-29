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


class CountryCreate(LocationBase):
    pass


class RegionCreate(CountryCreate):
    country_id: Optional[PyObjectId] = Field(None, example="64f95b0c2ab5ec9e0b22c77f")


class AreaCreate(RegionCreate):
    region_id: Optional[PyObjectId] = Field(None, example="64f95b0c2ab5ec9e0b22c77f")


class StateCreate(AreaCreate):    
    area_id: Optional[PyObjectId] = Field(None, example="64f95b0c2ab5ec9e0b22c77f")

class CountryUpdate(BaseModel):
    """Schema for updating any location type."""
    name: Optional[str] = Field(None)
    code: Optional[str] = Field(None)
    created_by: Optional[PyObjectId] = Field(None)
    updated_by: Optional[PyObjectId] = Field(None)

class RegionUpdate(CountryUpdate):
    country_id: Optional[PyObjectId] = Field(None)

class AreaUpdate(RegionUpdate):
    country_id: Optional[PyObjectId] = Field(None)
    region_id: Optional[PyObjectId] = Field(None)

class StateUpdate(AreaUpdate):
    country_id: Optional[PyObjectId] = Field(None)
    region_id: Optional[PyObjectId] = Field(None)
    area_id: Optional[PyObjectId] = Field(None)

class CountryResponse(LocationBase, BaseResponse):
    created_at: datetime
    updated_at: datetime
    is_active: bool
    is_deleted: bool    
    company_id: Optional[PyObjectId] = Field(None)

class RegionResponse(CountryResponse):
    country_id: Optional[PyObjectId] = Field(None)
    
class AreaResponse(RegionResponse):
    region_id: Optional[PyObjectId] = Field(None)

class StateResponse(AreaResponse):    
    area_id: Optional[PyObjectId] = Field(None)
