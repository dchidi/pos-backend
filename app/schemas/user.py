from typing import List, Optional, Set, Annotated
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator

from app.schemas import PyObjectId

from app.schemas.base import BaseResponse  
from app.constants.role_enum import UserRole

RoleStr = Annotated[str, Field(min_length=2, max_length=64)]

class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., example="John Doe")
    role: RoleStr | UserRole = UserRole.CASHIER
    permissions: Set[str] = Field(default_factory=set, example={"can_view_user"})
    branch_ids: Set[PyObjectId] = Field(default_factory=set)
    department_id: Optional[PyObjectId] = None
    is_verified: bool = False
    company_id: Optional[PyObjectId] = None

    # hashed_password: str = Field(repr=False)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.lower()

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: Optional[str]) -> Optional[str]:
        if v and any(char in v for char in ["$", "{", "}"]):
            raise ValueError("Invalid characters in full name")
        return v.strip() if v else v

    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)   
    warehouse_id: Optional[PyObjectId] = None 
    
    

class UserUpdate(BaseModel):
    # every field optional for PATCH‑style updates
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[RoleStr | UserRole] = None
    permissions: Optional[Set[str]] = None
    branch_ids: Optional[Set[PyObjectId]] = None
    department_id: Optional[PyObjectId] = None
    is_verified: Optional[bool] = None
    password: Optional[str] = None


class UserResponse(UserBase, BaseResponse):
    created_at: datetime
    updated_at: datetime
    is_active: bool
    is_deleted: bool
    # exclude hash automatically
    model_config = ConfigDict(ser_json_exclude={"hashed_password"}, from_attributes=True)
