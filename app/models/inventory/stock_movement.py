from beanie import Document, Indexed
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal
from decimal import Decimal
from datetime import datetime, timezone
import uuid


class StockMovement(Document):
    product_id: str
    warehouse_id: str
    quantity: Decimal = Field(..., gt=0)  # Always positive; movement_type decides direction
    unit_id: str  # The unit used in this movement

    movement_type: Literal[
        "GOODS_RECEIPT", 
        "STOCK_ADJUSTMENT", 
        "STOCK_TRANSFER_IN", 
        "STOCK_TRANSFER_OUT", 
        "SALE", 
        "RETURN", 
        "STOCK_AUDIT"
    ]

    source_type: Optional[str] = Field(None, description="E.g., goods_receipt, stock_adjustment")
    source_id: Optional[str] = Field(None, description="ObjectId from the source document")

    cost_price: Optional[Decimal] = Field(None, max_digits=10, decimal_places=2)  # Useful for COGS
    selling_price: Optional[Decimal] = Field(None, max_digits=10, decimal_places=2)  # Only for SALE

    created_by: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    revision: str = Field(default_factory=lambda: str(uuid.uuid4()))
    is_active: bool = True  # Logical deletion flag

    class Settings:
        name = "stock_movements"
        indexes = [
            ("product_id", "warehouse_id"),
            ("movement_type", "created_at"),
            ("source_type", "source_id"),
        ]

    model_config = {
        "json_schema_extra": {
            "example": {
                "product_id": "product_obj_id",
                "warehouse_id": "warehouse_obj_id",
                "quantity": 100.00,
                "unit_id": "unit_piece_id",
                "movement_type": "GOODS_RECEIPT",
                "source_type": "goods_receipt",
                "source_id": "receipt_obj_id",
                "cost_price": 250.00,
                "created_by": "user_id_1",
                "created_at": "2025-07-12T09:30:00Z",
                "revision": "b2fae580-5e42-4a30-a4d6-ecab1e0c1d92"
            }
        },
        "from_attributes": True
    }

    @field_validator('quantity')
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError("Quantity must be greater than zero")
        return v
