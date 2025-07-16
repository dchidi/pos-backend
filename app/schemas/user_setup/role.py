from pydantic import BaseModel, Field
from typing import Optional, Set
from enum import Enum
from datetime import datetime

class RoleStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"

class RoleBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    description: Optional[str] = Field(None, max_length=200)

class RoleCreate(RoleBase):
    permissions: Set[str]
    status: RoleStatus = RoleStatus.ACTIVE

class RolePatch(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    permissions: Optional[Set[str]] = None
    status: Optional[RoleStatus] = None

class RoleResponse(RoleBase):
    id: str = Field(..., alias="_id")
    permissions: Set[str]
    status: RoleStatus
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: Optional[str]
    last_modified_by: Optional[str]

    class Config:
        from_attributes = True