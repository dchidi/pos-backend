from beanie import Document
from pydantic import Field
from datetime import datetime, timezone
from typing import Optional

class StockAuditSession(Document):
    branch_id: str
    conducted_by: str
    warehouse_id: str
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    ended_at: Optional[datetime] = None
    note: Optional[str] = None

    class Settings:
        name = "stock_audits"

    model_config = {
        "json_schema_extra": {
            "example": {
                "branch_id": "branch_id",
                "conducted_by": "user_id",
                "started_at": "2025-07-01T08:00:00Z",
                "ended_at": "2025-07-01T14:00:00Z",
                "note": "Monthly audit"
            }
        },
        "from_attributes": True
    }
