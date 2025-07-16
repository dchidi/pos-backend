from datetime import datetime, timezone
from typing import Optional
from pydantic import Field
from beanie import Document

class ReplenishmentSuggestion(Document):
    product_id: str
    warehouse_id: str
    suggested_quantity: int
    current_stock: int
    reorder_level: int
    max_stock_level: Optional[int] = None
    forecast_period_days: Optional[int] = None
    source: Optional[str] = "policy_based"  # or 'forecast_based', 'AI'
    urgency: str  # "low", "medium", "critical"

    is_approved: bool = False
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None

    created_by: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "replenishment_suggestions"
