from beanie import Document
from pydantic import Field
from datetime import datetime, timezone
from typing import Optional

class Shift(Document):
    user_id: str
    branch_id: str
    start_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: Optional[datetime] = None
    is_closed: bool = False

    class Settings:
        name = "shifts"

    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "cashier_id",
                "branch_id": "branch_id",
                "start_time": "2025-07-08T07:00:00Z",
                "is_closed": False
            }
        },
        "from_attributes": True
    }
