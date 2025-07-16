from beanie import Document, before_event, Insert, Replace, Update
from pydantic import Field, AnyUrl
from datetime import datetime, timezone
from typing import Optional

class Category(Document):
    # required at the API/schema level
    name: str
    code: str

    # optional, defaults
    parent_id: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True
    is_deleted: bool = False
    image_url: Optional[AnyUrl] = None

    # timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "categories"

    @before_event([Insert, Replace, Update])
    async def touch_updated_at(self):
        self.updated_at = datetime.now(timezone.utc)

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Bread",
                "code": "CAT001",
                "parent_id": "category_obj_id",
                "description": "All bread products",
                "image_url": "https://…",
                "is_active": True,
                "is_deleted": False,
                "created_at": "2025-07-08T10:00:00Z",
                "updated_at": "2025-07-10T15:30:00Z",
            }
        },
        "from_attributes": True,
    }
