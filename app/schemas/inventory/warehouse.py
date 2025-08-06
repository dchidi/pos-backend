from pydantic import BaseModel, Field
from typing import Optional
from beanie import PydanticObjectId
from datetime import datetime

from app.constants import WarehouseType
from app.schemas.base import BaseResponse

class WarehouseBase(BaseModel):
  name: str = Field(..., min_length=3, max_length=100, example="Main Branch Warehouse")
  code: str = Field(..., min_length=2, max_length=100, example="WH-MAIN")
  branch_id: PydanticObjectId = Field(..., example="64f95b0c2ab5ec9e0b22c77f")
  warehouse_type: WarehouseType = Field(default=WarehouseType.USER, example="branch")
  description: Optional[str] = Field(None, max_length=500, example="Main warehouse for Lagos branch")
  location: Optional[str] = Field(None, max_length=200, example="23 Bode Thomas Street, Surulere, Lagos")
  capacity: Optional[int] = Field(None, gt=0, example=1500)
  created_by: Optional[PydanticObjectId] = Field(None, example="64f95b0c2ab5ec9e0b22c77f")
  updated_by: Optional[PydanticObjectId] = Field(None, example="64f95b0c2ab5ec9e0b22c77f")

class WarehouseCreate(WarehouseBase):
  pass

class WarehouseUpdate(BaseModel):
  name: Optional[str] = Field(None, min_length=3, max_length=100)
  code: Optional[str] = Field(None, min_length=2, max_length=100)
  branch_id: Optional[PydanticObjectId] = None
  warehouse_type: Optional[WarehouseType] = None
  description: Optional[str] = Field(None, max_length=500)
  location: Optional[str] = Field(None, max_length=200)
  capacity: Optional[int] = Field(None, gt=0)
  created_by: Optional[PydanticObjectId] = None
  updated_by: Optional[PydanticObjectId] = None


class WarehouseResponse(WarehouseBase, BaseResponse):
  is_active: bool
  is_deleted: bool
  created_at: datetime
  updated_at: datetime
