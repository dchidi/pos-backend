from datetime import datetime, timezone
from typing import Optional
from pydantic import Field
from beanie import Document

# Try to make it ai driven also
class DemandForecast(Document):
    product_id: str
    warehouse_id: Optional[str] = None  # Optional if forecasting is centralized
    period_start: datetime
    period_end: datetime
    forecast_quantity: int
    method: Optional[str] = "simple_moving_avg" # have other methods also and AI

    created_by: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "demand_forecasts"
