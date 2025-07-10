from beanie import Document
from pydantic import Field
from datetime import datetime, timezone
from typing import List

class StockAdjustment(Document):
    product_id: str
    branch_id: str
    warehouse_id:str
    old_quantity: int
    new_quantity: int
    reason: str  # e.g. 'stock count correction'
    serial_numbers: List[str]  # Track individual items
    investigation_notes: str   # Required for large discrepancies
    adjusted_by: str
    adjusted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "stock_adjustments"

    model_config = {
        "json_schema_extra": {
            "example": {
                "product_id": "prd_id",
                "branch_id": "branch_id",
                "warehouse_id": "warehouse_id",
                "old_quantity": 95,
                "new_quantity": 100,
                "reason": "Correction after count",
                "adjusted_by": "user_id",
                "adjusted_at": "2025-07-08T11:00:00Z"
            }
        },
        "from_attributes": True
    }
