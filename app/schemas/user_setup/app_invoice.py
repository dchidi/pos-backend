from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from app.constants.currency_enum import Currency
from app.constants.status_enum import PaymentStatus, TenantTier
from app.schemas.base import BaseResponse
from app.schemas import PyObjectId


class PlanInfoSnapshot(BaseModel):
    plan_name: str
    plan_description: Optional[str]
    plan_price: float
    plan_tier: TenantTier
    plan_duration_days: int
    number_of_users: int
    number_of_branch: int
    features: List[str]


class AppInvoiceBase(BaseModel):
    company_id: PyObjectId = Field(..., description="Reference to the tenant or subscriber")
    invoice_number: str = Field(..., description="Unique invoice identifier")

    currency: Currency = Field(default=Currency.US_DOLLAR)
    amount: float = Field(..., ge=0, description="Total amount billed")

    plan: PlanInfoSnapshot = Field(..., description="Snapshot of the plan at billing time")

    payment_status: PaymentStatus = Field(default=PaymentStatus.PENDING)
    paid_at: Optional[datetime] = Field(None, description="When payment was completed")

    billing_start: datetime = Field(..., description="Billing period start")
    billing_end: datetime = Field(..., description="Billing period end")

    notes: Optional[str] = Field(None)


class AppInvoiceCreate(AppInvoiceBase):
    pass


class AppInvoiceUpdate(BaseModel):
    payment_status: Optional[PaymentStatus] = None
    paid_at: Optional[datetime] = None
    notes: Optional[str] = None


class AppInvoiceResponse(AppInvoiceBase, BaseResponse):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
