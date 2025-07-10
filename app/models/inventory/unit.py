from beanie import Document
from pydantic import Field
from datetime import datetime, timezone
from typing import Optional

class Unit(Document):
    name: str  # e.g., "Kg", "Pack", "Piece"
    symbol: Optional[str] = None  # e.g., "kg", "pk", "pcs"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True

    class Settings:
        name = "units"

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Kilogram",
                "symbol": "kg",
                "created_at": "2025-07-08T10:00:00Z"
            }
        },
        "from_attributes": True
    }
