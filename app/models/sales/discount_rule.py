from beanie import Document
from pydantic import Field
from datetime import datetime, timezone
from typing import Optional

class DiscountRule(Document):
    name: str  # e.g., "Buy 2 Get 1 Free"
    description: Optional[str] = None
    is_active: bool = True
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "discount_rules"

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Mid-Year Promo",
                "description": "10% off all pastries",
                "is_active": True,
                "start_date": "2025-07-01T00:00:00Z",
                "end_date": "2025-07-15T23:59:00Z",
                "created_at": "2025-06-30T12:00:00Z"
            }
        },
        "from_attributes": True
    }
