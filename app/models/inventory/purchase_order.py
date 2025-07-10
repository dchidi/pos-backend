from beanie import Document
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import List, Optional
from decimal import Decimal

class PurchaseOrderItem(BaseModel):
    product_id: str
    quantity: int
    unit_cost: Decimal
    total: Decimal

class PurchaseOrder(Document):
    supplier_id: str
    branch_id: str
    warehouse_id: str
    items: List[PurchaseOrderItem]
    total_amount: Decimal
    status: str = "pending"  # 'pending', 'received', 'cancelled'
    created_by: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "purchase_orders"

    model_config = {
        "json_schema_extra": {
            "example": {
                "supplier_id": "supplier_obj_id",
                "branch_id": "branch_obj_id",
                "items": [
                    {
                        "product_id": "prd_123",
                        "quantity": 10,
                        "unit_cost": 2.5,
                        "total": 25.0
                    }
                ],
                "total_amount": 25.0,
                "status": "pending",
                "created_by": "user_id",
                "created_at": "2025-07-08T09:30:00Z"
            }
        },
        "from_attributes": True
    }
