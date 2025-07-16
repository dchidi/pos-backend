from typing import List, Optional, Set, Annotated
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator

from app.schemas import PyObjectId

from app.schemas.base import BaseResponse  
from app.constants.role_enum import UserRole

RoleStr = Annotated[str, Field(min_length=2, max_length=64)]

class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., example="John Doe")
    role: RoleStr | UserRole = UserRole.CASHIER
    permissions: Set[str] = Field(default_factory=set, example={"can_view_user"})
    branch_ids: Set[PyObjectId] = Field(default_factory=set)
    department_id: Optional[PyObjectId] = None
    warehouse_id: Optional[PyObjectId] = None
    is_verified: bool = False
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


class UserUpdate(BaseModel):
    # every field optional for PATCH‑style updates
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[RoleStr | UserRole] = None
    permissions: Optional[Set[str]] = None
    branch_ids: Optional[Set[PyObjectId]] = None
    department_id: Optional[PyObjectId] = None
    warehouse_id: Optional[PyObjectId] = None
    is_verified: Optional[bool] = None
    password: Optional[str] = None


class UserResponse(UserBase, BaseResponse):
    created_at: datetime
    updated_at: datetime
    is_active: bool
    is_deleted: bool

    # exclude hash automatically
    model_config = ConfigDict(ser_json_exclude={"hashed_password"}, from_attributes=True)

# from pydantic import(
#   BaseModel,
#   EmailStr, 
#   ConfigDict, 
#   field_validator, 
#   Field
# )
# from typing import Optional, List, Set
# from bson import ObjectId
# from app.schemas import PyObjectId
# from app.schemas.enums import RoleEnum
# from datetime import datetime
# from app.constants.role_enum import UserRole


# # from app.schemas.base import BaseResponse


# class UserBase(BaseModel):
#     email: EmailStr
#     full_name: str
#     branch_id: Set[Optional[str]] = Field(default=set, description="Associated branch ID")
#     department_id: Optional[str] = Field(default=None, description="Associated department ID")
#     permissions: Set[str] = Field(default_factory=set, description="User permissions set")    
#     role: str = UserRole.CASHIER

#     @field_validator("email")
#     @classmethod
#     def normalize_email(cls, v: str) -> str:
#         return v.lower()

#     @field_validator("full_name")
#     @classmethod
#     def validate_full_name(cls, v: Optional[str]) -> Optional[str]:
#         if v and any(char in v for char in ["$", "{", "}"]):
#             raise ValueError("Invalid characters in full name")
#         return v.strip() if v else v

#     model_config = ConfigDict(
#         from_attributes=True,
#         json_encoders={ObjectId: str}
#     )


# class UserCreate(UserBase):
#     password: str
#     # permissions: Set[str] = Field(..., description="Initial permissions set")


# class UserResponse(UserBase):
#     id: PyObjectId
#     is_deleted: bool
#     is_active: bool
#     is_verified: bool
#     branch_id: Optional[PyObjectId] = None
#     department_id: Optional[PyObjectId] = None    
#     warehouse_id: Optional[PyObjectId] = None
#     created_at: datetime
#     updated_at: datetime

# class UserUpdate(BaseModel):
#     full_name: Optional[str] = None
#     role: Optional[RoleEnum] = None
#     is_active: Optional[bool] = None
#     is_verified: Optional[bool] = None
#     branch_id: Optional[str] = None
#     department_id: Optional[str] = None    
#     warehouse_id: Optional[str] = None

#     @field_validator("full_name")
#     @classmethod
#     def validate_full_name(cls, v: Optional[str]) -> Optional[str]:
#         if v and any(char in v for char in ["$", "{", "}"]):
#             raise ValueError("Invalid characters in full name")
#         return v.strip() if v else v

# class UserPatch(UserUpdate):
#     pass

# class PaginationParams(BaseModel):
#     skip: int = 0
#     limit: int = 10

#     @field_validator("skip")
#     @classmethod
#     def validate_skip(cls, v: int) -> int:
#         if v < 0:
#             raise ValueError("Pagination 'skip' must be non-negative")
#         return v
    
# class UserFilterParams(BaseModel):
#     role: Optional[str] = Field(None, description="Filter by user role")
#     is_active: Optional[bool] = Field(None, description="Filter by active status")
#     email: Optional[str] = Field(None, description="Filter by email (partial match)")

# class PaginatedUserResponse(BaseModel):
#     items: List[UserResponse]
#     total: int