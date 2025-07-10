from beanie import Document
from pydantic import Field, EmailStr, field_validator
from datetime import datetime, timezone
from typing import Optional
from enum import Enum
from pymongo import ASCENDING, DESCENDING
import re

class SupplierStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    BLACKLISTED = "blacklisted"

class Supplier(Document):
    name: str = Field(..., min_length=2, max_length=100, description="Registered business name")
    legal_name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=100,
        description="Legal entity name if different from business name"
    )
    contact_name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=50,
        description="Primary contact person"
    )
    email: Optional[EmailStr] = Field(
        None,
        index=True,
        description="Primary business email"
    )
    phone: Optional[str] = Field(
        None,
        index=True,
        min_length=5,
        max_length=20,
        description="Primary contact number with country code"
    )
    secondary_phone: Optional[str] = Field(
        None,
        min_length=5,
        max_length=20
    )
    address: Optional[str] = Field(
        None,
        max_length=200,
        description="Full physical address"
    )
    city: Optional[str] = Field(None, max_length=50)
    country: Optional[str] = Field(None, max_length=50)
    tax_id: Optional[str] = Field(
        None,
        max_length=30,
        description="VAT/TIN number"
    )
    website: Optional[str] = Field(
        None,
        max_length=100,
        description="Company website URL"
    )
    lead_time_days: Optional[int] = Field(
        None,
        ge=0,
        description="Average delivery lead time in days"
    )
    payment_terms: Optional[str] = Field(
        None,
        max_length=50,
        description="e.g., 'Net 30', '50% advance'"
    )

    status: SupplierStatus = Field(
        default=SupplierStatus.ACTIVE,
        description="Supplier account status"
    )
    created_by: str = Field(
        ...,
        min_length=1,
        description="User ID who created this record"
    )
    updated_by: Optional[str] = Field(
        None,
        min_length=1,
        description="User ID who last updated this record"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Record creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Last modification timestamp"
    )

    class Settings:
        name = "suppliers"
        indexes = [
            [("name", ASCENDING)],
            [("email", ASCENDING)],
            [("phone", ASCENDING)],
            [("status", ASCENDING), ("name", ASCENDING)],
            [("city", ASCENDING), ("country", ASCENDING)],
            [("created_at", DESCENDING)],
            [("name", "text"), ("contact_name", "text")]  # For search
        ]

    @field_validator('phone', 'secondary_phone')
    def validate_phone(cls, v):
        if v and not re.match(r'^\+?[\d\s-]{5,20}$', v):
            raise ValueError("Invalid phone number format")
        return v

    @field_validator('website')
    def validate_website(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError("Website must start with http:// or https://")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Golden Mill Suppliers Ltd",
                "legal_name": "Golden Mill Enterprises Limited",
                "contact_name": "Tunde Johnson",
                "email": "orders@goldenmill.com",
                "phone": "+2348012345678",
                "secondary_phone": "+2348098765432",
                "address": "45 Market Road, Lagos Island",
                "city": "Lagos",
                "country": "Nigeria",
                "tax_id": "VAT-12345678",
                "website": "https://goldenmill.com",
                "lead_time_days": 7,
                "payment_terms": "Net 30",
                "status": "active",
                "created_by": "user_123",
                "updated_by": "user_123",
                "created_at": "2025-07-08T09:00:00Z",
                "updated_at": "2025-07-10T14:30:00Z"
            }
        },
        "from_attributes": True
    }