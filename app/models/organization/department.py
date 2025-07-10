from beanie import Document
from pydantic import Field
from datetime import datetime, timezone
from typing import Optional

class Department(Document):
    name: str
    code: str
    branch_id: str
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    is_active: bool = True

    class Settings:
        name = "departments"

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Bakery",
                "code": "DPT001",
                "branch_id": "branch_object_id",
                "created_by": "user_id_1",
                "updated_by": "user_id_2",
                "is_active": True,
                "created_at": "2025-07-08T08:00:00Z"
            }
        },
        "from_attributes": True
    }
