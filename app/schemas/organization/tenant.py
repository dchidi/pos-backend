from pydantic import BaseModel, Field, EmailStr, AnyUrl
from typing import Optional, List, Dict
from datetime import datetime
from app.schemas.base import BaseResponse
from app.schemas import PyObjectId
from app.constants.tenants_enum import PaymentMethod, TenantStatus, TenantTier


class AddressSchema(BaseModel):
    street: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=50)
    state: Optional[str] = Field(None, max_length=50)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    is_primary: bool = Field(default=True)


class BillingInfoSchema(BaseModel):
    company_name: str = Field(..., max_length=100)
    tax_id: Optional[str] = Field(None, max_length=50)
    payment_method: PaymentMethod = Field(default=PaymentMethod.CREDIT_CARD)
    billing_email: EmailStr
    billing_address: Optional[AddressSchema] = None
    payment_terms_days: int = Field(default=30, ge=0)


class TenantSettingsSchema(BaseModel):
    timezone: str = Field(default="UTC")
    locale: str = Field(default="en-US")
    currency: str = Field(default="USD", min_length=3, max_length=3)
    allow_multiple_locations: bool = Field(default=False)
    max_users: int = Field(default=5, ge=1)
    receipt_footer: Optional[str] = None


class TenantBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    display_name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    industry: Optional[str] = Field(None, max_length=50)
    website: Optional[AnyUrl] = None
    logo_url: Optional[AnyUrl] = None
    phone_number: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    tier: TenantTier = Field(default=TenantTier.BASIC)
    status: TenantStatus = Field(default=TenantStatus.ACTIVE)
    settings: TenantSettingsSchema = Field(default_factory=TenantSettingsSchema)
    addresses: List[AddressSchema] = Field(default_factory=list)
    billing_info: Optional[BillingInfoSchema] = None
    trial_start_date: Optional[datetime] = None
    trial_end_date: Optional[datetime] = None
    subscription_start_date: Optional[datetime] = None
    subscription_end_date: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)
    custom_fields: Dict[str, str] = Field(default_factory=dict)


class TenantCreate(TenantBase):
    created_by: Optional[PyObjectId] = None
    updated_by: Optional[PyObjectId] = None


class TenantUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    display_name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    industry: Optional[str] = Field(None, max_length=50)
    website: Optional[AnyUrl] = None
    logo_url: Optional[AnyUrl] = None
    phone_number: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    tier: Optional[TenantTier] = None
    status: Optional[TenantStatus] = None
    settings: Optional[TenantSettingsSchema] = None
    addresses: Optional[List[AddressSchema]] = None
    billing_info: Optional[BillingInfoSchema] = None
    trial_start_date: Optional[datetime] = None
    trial_end_date: Optional[datetime] = None
    subscription_start_date: Optional[datetime] = None
    subscription_end_date: Optional[datetime] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, str]] = None


class TenantResponse(TenantBase, BaseResponse):
    id: PyObjectId
    created_at: datetime
    updated_at: datetime
    created_by: Optional[PyObjectId] = None
    updated_by: Optional[PyObjectId] = None
