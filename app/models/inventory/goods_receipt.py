from beanie import Document
from pydantic import Field
from datetime import datetime, timezone
from typing import Optional

class GoodsReceipt(Document):
    purchase_order_id: str
    branch_id: str
    warehouse_id: str
    received_by: str
    delivery_vehicle: Optional[str]  # Track inbound logistics
    carrier_reference: Optional[str] # Shipping tracking ID
    received_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    note: Optional[str] = None

    class Settings:
        name = "goods_receipts"

    model_config = {
        "json_schema_extra": {
            "example": {
                "purchase_order_id": "po_obj_id",
                "branch_id": "branch_obj_id",
                "warehouse_id": "warehouse_obj_id",
                "received_by": "user_id",
                "received_at": "2025-07-08T10:00:00Z",
                "note": "Delivered complete"
            }
        },
        "from_attributes": True
    }
