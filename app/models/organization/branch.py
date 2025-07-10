from beanie import Document
from pydantic import Field
from datetime import datetime, timezone
from typing import Optional

class Branch(Document):
    name: str
    code: str  # unique code like "BR001"
    address: Optional[str] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    is_active: bool = True

    class Settings:
        name = "branches"

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Asaba Central",
                "code": "BR001",
                "address": "123 Main Street, Asaba",
                "created_by": "user_id_1",
                "updated_by": "user_id_2",
                "is_active": True,
                "created_at": "2025-07-08T08:00:00Z",
                "updated_at": "2025-07-08T10:00:00Z"
            }
        },
        "from_attributes": True
    }
