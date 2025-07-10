from beanie import Document
from pydantic import Field
from datetime import datetime, timezone
from typing import Optional

class POSSession(Document):
    cashier_id: str
    branch_id: str
    opened_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    closed_at: Optional[datetime] = None
    is_closed: bool = False
    total_sales: Optional[float] = 0.0

    class Settings:
        name = "pos_sessions"

    model_config = {
        "json_schema_extra": {
            "example": {
                "cashier_id": "user_id",
                "branch_id": "branch_id",
                "opened_at": "2025-07-08T08:00:00Z",
                "is_closed": False,
                "total_sales": 0.0
            }
        },
        "from_attributes": True
    }
