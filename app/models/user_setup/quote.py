from datetime import datetime
from typing import Optional, List
from beanie import Document, Indexed, PydanticObjectId
from pydantic import BaseModel, Field, EmailStr, HttpUrl
from app.constants.currency_enum import Currency
from app.constants.payment_method_enum import PaymentMethod
from app.constants.status_enum import TenantTier
from app.schemas.user_setup.quote import QuoteAddressSchema, QuoteSettingsSchema




class Quote(Document):
    # User identity and contact (optional for internal tracking)
    user_id: Optional[PydanticObjectId] = Field(None)
    full_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, max_length=20)

    # Business info
    company_name: Optional[str] = None
    website: Optional[HttpUrl] = None
    industry: Optional[str] = None
    logo_url: Optional[HttpUrl] = None

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

    # Lifecycle
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "quotes"
        indexes = [
            Indexed("user_id"),
            Indexed("email"),
            Indexed("plan_id"),
            Indexed("completed"),
            Indexed([("created_at", 1)])
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
