from beanie import Document, Indexed, PydanticObjectId
from pydantic import EmailStr, Field
from datetime import datetime, timezone
from typing import Optional, Set, Annotated, Union
from app.constants.role_enum import UserRole
from pymongo import ASCENDING

from app.models.base import TimeStampMixin

RoleStr = Annotated[str, Field(min_length=2, max_length=64)]

class User(Document, TimeStampMixin):
    email: Annotated[
        EmailStr,
        Indexed(
            name="uq_user_email",
            unique=True,
            collation={"locale": "en", "strength": 2}
        )
    ] = Field(..., description="Unique email of each user")
    hashed_password: str = Field(repr=False) # never show in repr / JSON
    full_name: str

    role:  Union[UserRole, RoleStr] = UserRole.CASHIER
    permissions: Set[str] = Field(default_factory=set)
    is_verified: bool = False # This extra checks will be needed for certain roles/permissions

    branch_ids: Set[PydanticObjectId] = Field(
        default_factory=set,
        description="Branches the user belongs to",
    )
    department_id: Optional[PydanticObjectId] = None
    warehouse_id: Optional[PydanticObjectId] = None  # Optional warehouse assigned to user


    class Settings:
        name = "users"
        indexes = [
            "branch_id",
            "department_id",
            "warehouse_id"
        ]

    model_config = {
        "from_attributes": True,
        "json_encoders": {PydanticObjectId: str},
        "ser_json_exclude": {"hashed_password"},
        "json_schema_extra": {
            "example": {
                "email": "admin@example.com",
                "full_name": "John Doe",
                "role": "manager",
                "permissions": ["can_view_user", "can_edit_user"],
                "branch_ids": ["64f95b0c2ab5ec9e0b22c77f"],
                "department_id": "64f95b0c2ab5ec9e0b22c780",
                "warehouse_id": None,
                "is_verified": False,
            }
        },
    }