from pydantic import(
  BaseModel,
  EmailStr, 
  ConfigDict, 
  field_validator, 
  Field
)
from typing import Optional, List, Set
from bson import ObjectId
from app.schemas import PyObjectId
from app.schemas.enums import RoleEnum
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    branch_id: Optional[str] = Field(default=None, description="Associated branch ID")
    department_id: Optional[str] = Field(default=None, description="Associated department ID")
    permissions: Set[str] = Field(default_factory=set, description="User permissions set")

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

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={ObjectId: str}
    )


class UserCreate(UserBase):
    password: str
    role: str = "cashier"
    permissions: Set[str] = Field(..., description="Initial permissions set")


class UserResponse(UserBase):
    id: PyObjectId
    role: str
    is_active: bool
    is_verified: bool
    branch_id: Optional[str] = None
    department_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime]

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[RoleEnum] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    branch_id: Optional[str] = None
    department_id: Optional[str] = None

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: Optional[str]) -> Optional[str]:
        if v and any(char in v for char in ["$", "{", "}"]):
            raise ValueError("Invalid characters in full name")
        return v.strip() if v else v

class UserPatch(UserUpdate):
    pass

class PaginationParams(BaseModel):
    skip: int = 0
    limit: int = 10

    @field_validator("skip")
    @classmethod
    def validate_skip(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Pagination 'skip' must be non-negative")
        return v
    
class UserFilterParams(BaseModel):
    role: Optional[str] = Field(None, description="Filter by user role")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    email: Optional[str] = Field(None, description="Filter by email (partial match)")

class PaginatedUserResponse(BaseModel):
    items: List[UserResponse]
    total: int