from beanie import Document
from pydantic import Field
from typing import Literal, Optional
from decimal import Decimal
from datetime import datetime, timezone

class ReplenishmentPolicy(Document):
    product_id: str
    warehouse_id: str

    method: Literal["min_max", "days_of_cover", "demand_forecast"]
    reorder_level: Optional[int] = None
    max_stock_level: Optional[int] = None
    safety_stock: Optional[int] = None
    average_daily_sales: Optional[Decimal] = None  # Used for "days_of_cover"
    lead_time_days: Optional[int] = None  # Days between order and delivery

    is_active: bool = True
    created_by: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "replenishment_policies"
