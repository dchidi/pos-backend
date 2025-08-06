from beanie import Document
from pydantic import Field, field_validator, BaseModel
from typing import Optional, List
from datetime import datetime
from pymongo import ASCENDING, IndexModel

from app.models.base import TimeStampMixin

from app.constants import Currency, PaymentStatus, TenantTier


class PlanInfo(BaseModel):
    plan_name: str
    plan_description: Optional[str]
    plan_price: float
    plan_tier: TenantTier
    plan_duration_days: int
    number_of_users: int
    number_of_branch: int
    features: List[str]


class AppInvoiceTransaction(Document, TimeStampMixin):
    company_id: str = Field(..., description="Reference to the tenant or subscriber")
    plan: PlanInfo = Field(..., description="Snapshot of the plan at billing time")

    invoice_number: str = Field(..., description="Unique invoice identifier")

    currency: Currency = Field(default=Currency.US_DOLLAR)
    amount: float = Field(..., ge=0, description="Total amount billed")

    payment_status: PaymentStatus = Field(default=PaymentStatus.PENDING, description="Current status of payment")
    paid_at: Optional[datetime] = Field(None, description="Timestamp when payment was successfully completed")

    billing_start: datetime = Field(..., description="Billing period start")
    billing_end: datetime = Field(..., description="Billing period end")

    notes: Optional[str] = Field(None)

    class Settings:
        name = "app_invoice_transactions"
        indexes = [
            IndexModel([("invoice_number", ASCENDING)], name="appinvoice_model_invoice_number", unique=True),
            IndexModel([("company_id", ASCENDING)], name="appinvoice_model_invoice_tenant"),
            IndexModel([("payment_status", ASCENDING)], name="appinvoice_model_invoice_payment_status"),
            IndexModel([("payment_status", ASCENDING), ("created_at", ASCENDING)], name="appinvoice_model_created_at_payment_status"),
        ]

    @field_validator("amount")
    def check_amount_positive(cls, v):
        if v < 0:
            raise ValueError("Amount must be non-negative")
        return v

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "company_id": "tenant_123abc",
                "invoice_number": "INV-2025-0001",
                "currency": "USD",
                "amount": 49.99,
                "payment_status": "paid",
                "paid_at": "2025-08-03T15:22:10Z",
                "billing_start": "2025-08-01T00:00:00",
                "billing_end": "2025-08-31T23:59:59",
                "notes": "Monthly invoice for Pro plan",
                "plan": {
                    "plan_name": "Pro Monthly",
                    "plan_description": "Best for growing teams",
                    "plan_price": 49.99,
                    "plan_tier": "pro",
                    "plan_duration_days": 30,
                    "number_of_users": 10,
                    "number_of_branch": 3,
                    "features": ["Advanced reports", "Multiple branches", "Priority support"]
                }
            }
        }
    }
