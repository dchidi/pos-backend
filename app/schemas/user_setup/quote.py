from pydantic import BaseModel, Field, EmailStr, HttpUrl
from typing import Optional, List
from datetime import datetime
from app.schemas import PyObjectId
from app.constants.currency_enum import Currency
from app.constants.payment_method_enum import PaymentMethod
from app.constants.status_enum import TenantTier
from app.schemas.base import BaseResponse


class QuoteSettingsSchema(BaseModel):
    timezone: Optional[str] = Field(default="UTC")
    locale: Optional[str] = Field(default="en-US")
    currency: Optional[Currency] = Field(default=Currency.US_DOLLAR)
    allow_multiple_locations: Optional[bool] = Field(default=False)
    max_users: Optional[int] = Field(default=5, ge=1)
    receipt_footer: Optional[str] = None


class QuoteAddressSchema(BaseModel):
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    is_primary: Optional[bool] = Field(default=True)


class QuoteBase(BaseModel):
    user_id: Optional[PyObjectId] = Field(None)
    full_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, max_length=20)

    company_name: Optional[str] = None
    website: Optional[HttpUrl] = None
    industry: Optional[str] = None
    logo_url: Optional[HttpUrl] = None

    plan_id: Optional[PyObjectId] = None
    tier: Optional[TenantTier] = None

    settings: Optional[QuoteSettingsSchema] = None
    addresses: Optional[List[QuoteAddressSchema]] = None

    payment_method: Optional[PaymentMethod] = None
    currency: Optional[Currency] = Field(default=Currency.US_DOLLAR)
    expected_start_date: Optional[datetime] = None
    notes: Optional[str] = None

    completed: bool = Field(default=False)


class QuoteCreate(QuoteBase):
    pass


class QuoteUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None

    company_name: Optional[str] = None
    website: Optional[HttpUrl] = None
    industry: Optional[str] = None
    logo_url: Optional[HttpUrl] = None

    plan_id: Optional[PyObjectId] = None
    tier: Optional[TenantTier] = None

    settings: Optional[QuoteSettingsSchema] = None
    addresses: Optional[List[QuoteAddressSchema]] = None

    payment_method: Optional[PaymentMethod] = None
    currency: Optional[Currency] = None
    expected_start_date: Optional[datetime] = None
    notes: Optional[str] = None

    completed: Optional[bool] = None


class QuoteResponse(QuoteBase, BaseResponse):
    id: PyObjectId
    created_at: datetime
    updated_at: datetime
