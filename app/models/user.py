from beanie import Document, Indexed
from pydantic import EmailStr, Field
from datetime import datetime, timezone
from typing import Optional, Set, Annotated
from pymongo import ASCENDING

class User(Document):
    email: Annotated[EmailStr, Indexed(unique=True)]  # Instead of defining in Settings
    hashed_password: str
    full_name: Optional[str] = None
    role: str = "cashier"
    permissions: Set[str] = []
    is_verified: bool = False
    is_active: bool = True

    branch_id: str
    department_id: str
    warehouse_id: Optional[str] = None  # Optional warehouse assigned to user

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    class Settings:
        name = "users"
        indexes = [
            "branch_id",
            "department_id",
            "warehouse_id"
        ]

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "admin@example.com",
                "full_name": "John Doe",
                "role": "cashier",
                "permissions": ["can_view_user", "can_edit_users"],
                "branch_id": "branch_obj_id",
                "department_id": "department_obj_id",
                "warehouse_id": "warehouse_obj_id",  # Optional
                "is_verified": False,
                "is_active": True,
                "created_at": "2025-07-05T11:00:00Z"
            }
        },
        "from_attributes": True
    }
