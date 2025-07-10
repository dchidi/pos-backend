from beanie import Document
from pydantic import Field
from datetime import datetime, timezone
from typing import Optional

class Category(Document):
    name: str
    code: str
    parent_id: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "categories"

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Bread",
                "code": "CAT001",
                "parent_id": "category_obj_id",
                "description": "All bread products",
                "is_active": True,
                "created_at": "2025-07-08T10:00:00Z"
            }
        },
        "from_attributes": True
    }
