from beanie import Document
from pydantic import Field
from datetime import datetime, timezone
from typing import Optional


class Brand(Document):
    name: str
    description: Optional[str] = None
    logo_url: Optional[str] = None  # Optional logo for the brand
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True

    class Settings:
        name = "brands"

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Golden Crust",
                "description": "Premium bakery brand",
                "logo_url": "https://example.com/logo.png",
                "created_at": "2025-07-08T10:00:00Z",
                "is_active": True
            }
        },
        "from_attributes": True
    }
