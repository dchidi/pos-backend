from beanie import Document
from pydantic import Field
from datetime import datetime, timezone, date
from decimal import Decimal

class DailySalesSummary(Document):
    branch_id: str
    cashier_id: str
    summary_date: date
    total_sales: Decimal
    total_refunds: Decimal
    total_transactions: int
    cash_total: Decimal
    card_total: Decimal
    transfer_total: Decimal
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "daily_sales_summaries"

    model_config = {
        "json_schema_extra": {
            "example": {
                "branch_id": "branch_id",
                "cashier_id": "user_id",
                "summary_date": "2025-07-08",
                "total_sales": 7500.00,
                "total_refunds": 500.00,
                "total_transactions": 34,
                "cash_total": 4000.00,
                "card_total": 2500.00,
                "transfer_total": 1000.00,
                "created_at": "2025-07-08T23:59:00Z"
            }
        },
        "from_attributes": True
    }
