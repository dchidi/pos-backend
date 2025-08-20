from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from beanie import PydanticObjectId
from pydantic import BaseModel, Field, HttpUrl


from app.constants import Currency


class CartItem(BaseModel):
    product_id: str
    sku: Optional[str] = None
    name: str
    quantity: int
    unit_price: int

    @property
    def total(self) -> float:
        return float(self.quantity) * float(self.unit_price)


class InitPaymentRequest(BaseModel):
    tenant_id: PydanticObjectId
    customer_email: str
    customer_name: Optional[str] = None
    currency: Currency = Currency.US_DOLLAR
    items: List[CartItem]
    callback_url: Optional[HttpUrl] = None
    reference: Optional[str] = Field(None, description="Client-generated idempotent key")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @property
    def amount_major(self) -> float:
        return sum(item.total for item in self.items)


class InitPaymentResponse(BaseModel):
    reference: str
    authorization_url: HttpUrl
    access_code: Optional[str] = None


class VerifyResponse(BaseModel):
    reference: str
    status: str
    amount_minor: int
    currency: Currency
    paid_at: Optional[datetime] = None
    gateway_response: Optional[str] = None


class SubscriptionInterval(str, Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    quarterly = "quarterly"
    annually = "annually"


class StartSubscriptionRequest(BaseModel):
    tenant_id: PydanticObjectId
    customer_email: str
    plan_id: Optional[str] = None


class StartSubscriptionResponse(BaseModel):
    reference: str
    authorization_url: HttpUrl
    plan_id: str


class SubscriptionStatusResponse(BaseModel):
    tenant_id: PydanticObjectId
    customer_email: str
    status: str
    plan_id: Optional[str] = None
    subscription_code: Optional[str] = None