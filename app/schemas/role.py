from pydantic import BaseModel, Field
from typing import Optional, Set
from beanie import PydanticObjectId
from datetime import datetime

from app.schemas.base import BaseResponse


class RoleBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    permissions: Optional[Set[str]] = Field(default_factory=set)    
    exclusions: Optional[Set[str]] = Field(default_factory=set) 
    

class RoleCreate(RoleBase):                 
    created_by: Optional[PydanticObjectId] = None,                
    updated_by: Optional[PydanticObjectId] = None

class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    permissions: Optional[Set[str]] = None

class RoleResponse(RoleBase, BaseResponse):
    permissions: Optional[Set[str]] = None
    company_id: Optional[PydanticObjectId] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[PydanticObjectId] = None
    updated_by: Optional[PydanticObjectId] = None