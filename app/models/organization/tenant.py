import re
from pydantic import BaseModel, Field, field_validator, EmailStr, HttpUrl
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Annotated
from beanie import (
  Document, before_event, Insert, Indexed
)
from app.models.base import TimeStampMixin

from app.constants.tenants_enum import (
    PaymentMethod, TenantStatus, TenantTier
)

from pymongo import ASCENDING, IndexModel

class Address(BaseModel):
    """Physical address structure"""
    street: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=50)
    state: Optional[str] = Field(None, max_length=50)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)    
    is_primary: bool = Field(default=True)

class BillingInfo(BaseModel):
    """Financial billing information"""
    company_name: str = Field(..., max_length=100)
    tax_id: Optional[str] = Field(None, max_length=50, description="VAT, GST, or other tax ID")
    payment_method: PaymentMethod = Field(default=PaymentMethod.CREDIT_CARD)
    billing_email: EmailStr = Field(..., description="Email for invoices and billing communications")
    billing_address: Optional[Address] = Field(None)
    payment_terms_days: int = Field(default=30, ge=0, description="Net payment terms in days")

class TenantSettings(BaseModel):
    """Configurable tenant-specific settings"""
    timezone: str = Field(default="UTC", description="IANA timezone string")
    locale: str = Field(default="en-US", description="Default locale/language")
    currency: str = Field(default="USD", min_length=3, max_length=3)
    allow_multiple_locations: bool = Field(default=False)
    max_users: int = Field(default=5, ge=1)
    receipt_footer: Optional[str] = Field(None, description="Custom text for POS receipts")

class Tenant(Document, TimeStampMixin):
    """Primary tenant/organization model for multi-tenant POS system"""
    # Core identification
    name: Annotated[
        str,
        Indexed(
            unique=True,
            name="tenant_model_name",
            collation={"locale": "en", "strength": 2},
        ),
    ] = Field(..., min_length=2, max_length=100, description="Legal business name")
    
    display_name: Optional[str] = Field(
        None, 
        max_length=100,
        description="Optional display name different from legal name"
    )
    
    # Business information
    description: Optional[str] = Field(None, max_length=500)
    industry: Optional[str] = Field(None, max_length=50)
    website: Optional[HttpUrl] = None
    logo_url: Optional[HttpUrl] = None
    phone_number: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    
    # Tenant configuration
    tier: TenantTier = Field(default=TenantTier.BASIC)
    status: TenantStatus = Field(default=TenantStatus.ACTIVE)
    settings: TenantSettings = Field(default_factory=TenantSettings)
    
    # Business locations
    addresses: List[Address] = Field(default_factory=list)
    
    # Financial information
    billing_info: Optional[BillingInfo] = None
    
    # Subscription dates
    trial_start_date: Optional[datetime] = None
    trial_end_date: Optional[datetime] = None
    subscription_start_date: Optional[datetime] = None
    subscription_end_date: Optional[datetime] = None
    
    # Metadata
    tags: List[str] = Field(
        default_factory=list,
        description="Categories or labels for tenant organization"
    )
    custom_fields: Dict[str, str] = Field(
        default_factory=dict,
        description="Flexible key-value pairs for tenant-specific data"
    )

    class Settings:
        name = "tenants"
        indexes = [
            IndexModel([("status", ASCENDING)], name="tenant_model_status"),
            IndexModel([("tier", ASCENDING)], name="tenant_model_tier"),
            IndexModel([("created_at", ASCENDING)], name="tenant_model_created_at"),
            IndexModel([("name", ASCENDING)], name="tenant_model_name"),  # Already indexed via Annotated
            IndexModel([("status", ASCENDING), ("tier", ASCENDING)], name="tenant_model_status_tier"),  # Compound index
        ]

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Golden Crust Bakery Inc.",
                "display_name": "Golden Crust",
                "description": "Premium artisanal bakery with 5 locations",
                "industry": "Food & Beverage",
                "website": "https://goldencrust.example.com",
                "logo_url": "https://cdn.example.com/tenants/goldencrust/logo.png",
                "phone": "+1 (555) 123-4567",
                "email": "contact@goldencrust.example.com",
                "tier": "pro",
                "status": "active",
                "settings": {
                    "timezone": "America/New_York",
                    "locale": "en-US",
                    "currency": "USD",
                    "allow_multiple_locations": True,
                    "max_users": 10,
                    "receipt_footer": "Thank you for supporting local business!"
                },
                "addresses": [{
                    "street": "123 Main St",
                    "city": "New York",
                    "state": "NY",
                    "postal_code": "10001",
                    "country": "USA",
                    "is_primary": True
                }],
                "billing_info": {
                    "company_name": "Golden Crust Bakery Inc.",
                    "tax_id": "US123456789",
                    "payment_method": "credit_card",
                    "billing_email": "accounting@goldencrust.example.com",
                    "billing_address": {
                        "street": "123 Main St",
                        "city": "New York",
                        "state": "NY",
                        "postal_code": "10001",
                        "country": "USA",
                        "is_primary": True
                    },
                    "payment_terms_days": 30
                },
                "trial_start_date": "2025-01-01T00:00:00Z",
                "trial_end_date": "2025-01-31T00:00:00Z",
                "subscription_start_date": "2025-02-01T00:00:00Z",
                "subscription_end_date": "2026-01-31T00:00:00Z",
                "tags": ["bakery", "retail", "food-service"],
                "custom_fields": {
                    "favorite_color": "gold",
                    "preferred_contact": "email"
                }
            }
        },
        "from_attributes": True
    }

    @field_validator("phone_number")
    def validate_phone(cls, v):
        if v and not re.match(r"^\+?[1-9]\d{1,14}$", v):
            raise ValueError("Invalid E.164 phone number")
        return v
    
    @before_event([Insert])
    async def set_trial_dates(self):
        """Set trial period dates if not provided"""
        if self.tier == TenantTier.FREE and not self.trial_start_date:
            self.trial_start_date = datetime.now(timezone.utc)
            self.trial_end_date = None  # Free tier has no end date
            
        elif self.tier != TenantTier.FREE and not self.trial_start_date:
            self.trial_start_date = datetime.now(timezone.utc)
            self.trial_end_date = datetime.now(timezone.utc) + timedelta(days=30)