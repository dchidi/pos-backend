from datetime import datetime, timezone
from typing import Optional, List
from beanie import Document, PydanticObjectId
from pydantic import Field, EmailStr, AnyUrl
from pymongo import IndexModel, ASCENDING

from app.models.base import TimeStampMixin

from app.constants import Currency, PaymentMethod, TenantTier

from app.schemas.user_setup.quote import QuoteAddressSchema, QuoteSettingsSchema




class Quote(Document, TimeStampMixin):
    # User identity and contact (optional for internal tracking)
    user_id: Optional[PydanticObjectId] = Field(None)
    full_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, max_length=20)

    # Business info
    company_name: Optional[str] = None
    website: Optional[AnyUrl] = None
    industry: Optional[str] = None
    logo_url: Optional[AnyUrl] = None

    # Plan selection
    plan_id: Optional[PydanticObjectId] = Field(None)
    tier: Optional[TenantTier] = None

    # Preferences/settings
    settings: Optional[QuoteSettingsSchema] = None
    addresses: Optional[List[QuoteAddressSchema]] = None

    # Billing / payment intent
    payment_method: Optional[PaymentMethod] = None
    currency: Optional[Currency] = Field(default=Currency.US_DOLLAR)
    expected_start_date: Optional[datetime] = None
    notes: Optional[str] = None

    class Settings:
        name = "quotes"
        indexes = [
            IndexModel([("user_id", ASCENDING)], name="quote_md_user_id"),
            IndexModel([("email", ASCENDING)], name="quote_md_email"),
            IndexModel([("plan_id", ASCENDING)], name="quote_md_plan_id"),
            IndexModel([("created_at", ASCENDING)], name="quote_md_created_at")
        ]

    class Config:
        schema_extra = {
            "example": {
                "user_id": "60d5f484a2b4b5a9c3d4e8f0",
                "full_name": "Jane Doe",
                "email": "jane.doe@example.com",
                "company_name": "Doe Enterprises",
                "plan_id": "60d5f484a2b4b5a9c3d4e8f1",
                "tier": "pro",
                "settings": {
                    "timezone": "America/New_York",
                    "locale": "en-US",
                    "currency": "USD",
                    "allow_multiple_locations": True,
                    "max_users": 10
                },
                "payment_method": "credit_card",
                "completed": False
            }
        }
