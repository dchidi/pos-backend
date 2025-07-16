from beanie import Document, Indexed
from pydantic import Field, field_validator
from typing import Optional, Literal
from decimal import Decimal
from datetime import datetime, timezone
import uuid


class PriceList(Document):
    product_id: str
    unit_id: str
    price_type: Literal["SELL", "BUY"] = "SELL"

    price: Decimal = Field(..., max_digits=10, decimal_places=2)
    cost_price: Optional[Decimal] = Field(
        None, max_digits=10, decimal_places=2,
        description="Optional — projected or agreed cost"
    )

    version: int = Field(..., description="Version of the price for this product/unit/type")
    effective_from: datetime = Field(..., description="When this price becomes active")
    effective_to: Optional[datetime] = None

    is_active: bool = True
    created_by: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "price_list"
        indexes = [
            [("product_id", 1), ("unit_id", 1), ("price_type", 1), ("version", 1)],
            [("product_id", 1), ("unit_id", 1), ("price_type", 1), ("is_active", 1)],
            [("effective_from", 1)]
        ]

    @field_validator("effective_to")
    def validate_date_order(cls, v, info):
        if v and v <= info.data["effective_from"]:
            raise ValueError("effective_to must be after effective_from")
        return v
