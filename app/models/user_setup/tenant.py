import re
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Annotated

from beanie import Document, before_event, Insert, Indexed, PydanticObjectId
from pydantic import Field, field_validator, EmailStr, HttpUrl
from pymongo import ASCENDING, IndexModel

from app.models.base import TimeStampMixin
from app.constants.status_enum import TenantStatus, TenantTier

from app.schemas.user_setup.tenant import (
    AddressSchema, BillingInfoSchema, TenantSettingsSchema
)


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

    display_name: Optional[str] = Field(None, max_length=100, description="Display name different from legal name")

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
    settings: TenantSettingsSchema = Field(default_factory=TenantSettingsSchema)
    plan_id: PydanticObjectId = Field(..., description="Reference to the tenant's current plan")

    # Business locations
    addresses: List[AddressSchema] = Field(default_factory=list)

    # Financial information
    billing_info: Optional[BillingInfoSchema] = None

    # Subscription dates
    trial_start_date: Optional[datetime] = None
    trial_end_date: Optional[datetime] = None
    subscription_start_date: Optional[datetime] = None
    subscription_end_date: Optional[datetime] = None

    # Metadata
    tags: List[str] = Field(default_factory=list, description="Categories or labels for tenant organization")
    custom_fields: Dict[str, str] = Field(default_factory=dict, description="Flexible key-value pairs for tenant-specific data")

    class Settings:
        name = "tenants"
        indexes = [
            IndexModel([("status", ASCENDING)], name="tenant_model_status"),
            IndexModel([("tier", ASCENDING)], name="tenant_model_tier"),
            IndexModel([("created_at", ASCENDING)], name="tenant_model_created_at"),
            IndexModel([("status", ASCENDING), ("tier", ASCENDING)], name="tenant_model_status_tier"),
        ]

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "name": "Golden Crust Bakery Inc.",
                "display_name": "Golden Crust",
                "description": "Premium artisanal bakery with 5 locations",
                "industry": "Food & Beverage",
                "website": "https://goldencrust.example.com",
                "logo_url": "https://cdn.example.com/tenants/goldencrust/logo.png",
                "phone_number": "+1 (555) 123-4567",
                "email": "contact@goldencrust.example.com",
                "plan_id": "60*12",
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
                    "billing_start": "2025-08-01T00:00:00Z",
                    "billing_end": "2025-08-31T00:00:00Z",
                    "subscription_duration_days": 30,
                    "payment_terms_days": 10,
                    "due_date": "2025-08-11T00:00:00Z",
                    "notes": "Early access invoice"
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
        }
    }

    @field_validator("phone_number")
    def validate_phone(cls, v):
        if v and not re.match(r"^\+?[1-9]\d{1,14}$", v):
            raise ValueError("Invalid E.164 phone number")
        return v

    @before_event([Insert])
    async def set_trial_dates(self):
        """Set trial period dates if not provided"""
        now = datetime.now(timezone.utc)
        if self.tier == TenantTier.FREE and not self.trial_start_date:
            self.trial_start_date = now
            self.trial_end_date = None  # Free tier has no end date

        elif self.tier != TenantTier.FREE and not self.trial_start_date:
            self.trial_start_date = now
            self.trial_end_date = now + timedelta(days=30)

        # Optional: auto-calculate due_date if not set
        if self.billing_info and self.billing_info.billing_start and not self.billing_info.due_date:
            self.billing_info.due_date = self.billing_info.billing_start + timedelta(days=self.billing_info.payment_terms_days)
