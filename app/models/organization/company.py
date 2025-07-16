from beanie import Document, Indexed
from pydantic import Field
from datetime import datetime, timezone
from typing import Optional, Annotated


class Company(Document):
    name: Annotated[
        str,
        Indexed(
            unique=True,
            name="country_model_name",
            collation={"locale": "en", "strength": 2},
        ),
    ] = Field(..., description="Country name (unique, case-insensitive)")

    description: Optional[str] = None
    logo_url: Optional[str] = None  # Optional logo for UI display

    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "companies"

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Golden Crust Industries",
                "description": "Makers of premium bakery brands",
                "logo_url": "https://example.com/logos/goldencrust.png",
                "is_active": True,
                "created_at": "2025-07-12T09:30:00Z"
            }
        },
        "from_attributes": True
    }
