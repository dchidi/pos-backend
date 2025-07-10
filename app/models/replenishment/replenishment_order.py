from datetime import datetime, timezone
from typing import Optional
from pydantic import Field
from beanie import Document
from uuid import uuid4

class ReplenishmentOrder(Document):
    reference: str = Field(default_factory=lambda: f"ROP-{uuid4().hex[:8].upper()}")
    product_id: str
    source_warehouse_id: Optional[str] = None  # For inter-warehouse transfer
    destination_warehouse_id: str
    quantity: int

    status: str = "pending"  # pending, approved, in_transit, completed, cancelled
    related_suggestion_id: Optional[str] = None

    created_by: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "replenishment_orders"
