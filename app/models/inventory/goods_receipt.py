from beanie import Document
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime, timezone
from decimal import Decimal


class GoodsReceiptItem(BaseModel):
    product_id: str
    unit_id: str
    quantity_ordered: Decimal = Field(..., gt=0)
    quantity_received: Decimal = Field(..., ge=0)
    cost_price: Decimal = Field(..., gt=0)
    remarks: Optional[str] = None

    @property
    def status(self) -> Literal["FULL", "PARTIAL", "REJECTED"]:
        if self.quantity_received == 0:
            return "REJECTED"
        elif self.quantity_received < self.quantity_ordered:
            return "PARTIAL"
        return "FULL"


class GoodsReceipt(Document):
    purchase_order_id: str
    branch_id: str
    warehouse_id: str
    received_by: str

    delivery_vehicle: Optional[str] = None
    carrier_reference: Optional[str] = None

    receive_type: Literal["FULL", "PARTIAL", "REJECTED"]
    reason: Optional[Literal["DAMAGED", "SHORT_SHIPMENT", "WRONG_ITEM", "EXPIRED", "OTHER"]] = None
    note: Optional[str] = Field(None, description="Free-text explanation or observations")

    items: List[GoodsReceiptItem]

    received_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "goods_receipts"

    model_config = {
        "json_schema_extra": {
            "example": {
                "purchase_order_id": "po_obj_id",
                "branch_id": "branch_obj_id",
                "warehouse_id": "warehouse_obj_id",
                "received_by": "user_id",
                "receive_type": "PARTIAL",
                "reason": "DAMAGED",
                "note": "Delivery partially accepted",
                "items": [
                    {
                        "product_id": "prod123",
                        "unit_id": "unit_piece",
                        "quantity_ordered": 100,
                        "quantity_received": 80,
                        "cost_price": 120.00,
                        "remarks": "20 rejected due to broken packaging"
                    }
                ],
                "received_at": "2025-07-12T10:00:00Z"
            }
        },
        "from_attributes": True
    }
