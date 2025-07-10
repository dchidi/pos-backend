from beanie import Document
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional

class ReturnItem(BaseModel):
    product_id: str
    product_name: str
    quantity: int
    unit_price: Decimal
    total: Decimal

class SaleReturn(Document):
    sale_id: str
    branch_id: str
    warehouse_id: str
    returned_by: str  # user id
    items: List[ReturnItem]
    total_refund: Decimal
    reason: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "sale_returns"

    model_config = {
        "json_schema_extra": {
            "example": {
                "sale_id": "sale_obj_id",
                "branch_id": "branch_id",
                "returned_by": "user_id",
                "items": [
                    {
                        "product_id": "prd_id",
                        "product_name": "Sliced Bread",
                        "quantity": 1,
                        "unit_price": 3.50,
                        "total": 3.50
                    }
                ],
                "total_refund": 3.50,
                "reason": "Customer returned expired item",
                "created_at": "2025-07-08T12:00:00Z"
            }
        },
        "from_attributes": True
    }
