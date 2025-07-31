from beanie import Document, Indexed, PydanticObjectId
from pydantic import EmailStr, Field, field_validator
from typing import Optional, Set, Annotated, Union
from app.constants.role_enum import UserRole
from pymongo import ASCENDING
import re
from datetime import datetime, timezone
from app.models.base import TimeStampMixin

RoleStr = Annotated[str, Field(min_length=2, max_length=64)]


class User(Document, TimeStampMixin):    
    hashed_password: str = Field(repr=False) # never show in repr / JSON

    email: Annotated[
        EmailStr,
        Indexed(
            name="user_model_email",
            unique=True,
            collation={"locale": "en", "strength": 2}
        )
    ] = Field(..., description="Unique email of each user")
    full_name: str = Field(..., description="User first and last name")    
    phone_number: Optional[str] = Field(None, pattern=r"^\+?[1-9]\d{1,14}$", description="User first and last name")

    company_id: Annotated[
        PydanticObjectId,
        Indexed(
            name="user_model_company_id",
        ),
    ] = Field(..., description="Company/Rental ID", example="646464646464646464646464")

    last_login_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when last logged in"
    )
    
    role:  Union[UserRole, RoleStr] = UserRole.CASHIER
    permissions: Set[str] = Field(default_factory=set)   

    refresh_token: Optional[str] = None
    refresh_token_expires_at: Optional[datetime] = None

    is_verified: bool = Field(False, description="Extra checks needed for higher access")
    reset_password: bool = Field(True, description="Request user to change their password")

    branch_ids: Set[PydanticObjectId] = Field(
        default_factory=set,
        description="Branches the user belongs to. This is useful for senior managers",
    )
    department_id: Optional[PydanticObjectId] = None

    @field_validator("phone_number")
    def validate_phone(cls, v):
        if v and not re.match(r"^\+?[1-9]\d{1,14}$", v):
            raise ValueError("Invalid E.164 phone number")
        return v

    class Settings:
        name = "users"
        indexes = [        
            [("company_id", ASCENDING), ("email", ASCENDING), ("is_active", ASCENDING), ("department_id", ASCENDING)],
            [("company_id", ASCENDING), ("is_active", ASCENDING)],
            [("company_id", ASCENDING), ("department_id", ASCENDING)],
            [("company_id", ASCENDING), ("is_active", ASCENDING), ("role", ASCENDING)],
            [("company_id", ASCENDING), ("created_at", ASCENDING)],  # For recent user signups
            [("company_id", ASCENDING), ("last_login_at", ASCENDING)],  # For inactive user cleanup
        ]

    model_config = {
        "from_attributes": True,
        "json_encoders": {PydanticObjectId: str},
        "ser_json_exclude": {"hashed_password"},
        "json_schema_extra": {
            "example": {
                "company_id": "64f95b0c2ab5ec9e0b22c77f",
                "email": "admin@example.com",
                "full_name": "John Doe",
                "phone_number": "+235899516678",
                "role": "manager",
                "permissions": ["can_view_user", "can_edit_user"],
                "branch_ids": ["64f95b0c2ab5ec9e0b22c77f"],
                "department_id": "64f95b0c2ab5ec9e0b22c780",
                "is_verified": False,
                "is_active": True,
                "is_deleted": False,                
                "created_by": "64f95b0c2ab5ec9e0b22c780",                
                "updated_by": "64f95b0c2ab5ec9e0b22c780",
            }
        },
    }