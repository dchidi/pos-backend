from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict
from datetime import datetime
from beanie import PydanticObjectId
from app.schemas.user_setup.tenant import AddressSchema

class StoreSettingsSchema(BaseModel):
    timezone: str = Field(default="UTC")
    locale: str = Field(default="en-US")
    currency: str = Field(default="USD", min_length=3, max_length=3)
    receipt_footer: Optional[str] = None
    max_users: int = Field(default=5)  # optional store-level user limit
    add_ons_stores: int = Field(default=0)

class StoreBase(BaseModel):
    tenant_id: PydanticObjectId = Field(..., description="Reference to the parent tenant")
    name: str = Field(..., min_length=2, max_length=100)
    display_name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    phone_number: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    logo_url: Optional[str] = None
    addresses: List[AddressSchema] = Field(default_factory=list)
    
    settings: StoreSettingsSchema = Field(default_factory=StoreSettingsSchema)
    tax_rate: float = Field(default=0.0, ge=0.0, le=100.0)  # % applied to sales    
    tax_id: Optional[str] = Field(default="VAT", max_length=50)
    
    custom_fields: Dict[str, str] = Field(default_factory=dict)

class StoreCreate(StoreBase):
    created_by: Optional[PydanticObjectId] = None
    updated_by: Optional[PydanticObjectId] = None

class StoreUpdate(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    logo_url: Optional[str] = None
    addresses: Optional[List[AddressSchema]] = None
    settings: Optional[StoreSettingsSchema] = None
    tax_rate: Optional[float] = None
    custom_fields: Optional[Dict[str, str]] = None

class StoreResponse(StoreBase):
    id: PydanticObjectId
    created_at: datetime
    updated_at: datetime
    created_by: Optional[PydanticObjectId] = None
    updated_by: Optional[PydanticObjectId] = None
