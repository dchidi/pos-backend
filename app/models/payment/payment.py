from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from beanie import Document, PydanticObjectId
from pydantic import Field, EmailStr
from pymongo import ASCENDING, DESCENDING, IndexModel

from app.constants import Currency

class Payment(Document):
  reference: str
  tenant_id: PydanticObjectId
  customer_email: EmailStr
  amount_minor: int = Field(..., ge=0)
  currency: Currency = Field(default=Currency.US_DOLLAR)
  status: str = Field(default="initialized") # initialized|paid|failed|abandoned
  authorization_url: Optional[str] = None
  metadata: Optional[Dict[str, Any]] = None
  gateway: str = Field(default="paystack")
  created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
  paid_at: Optional[datetime] = None


  class Settings:
    name = "payments"
    indexes = [    
        IndexModel([("reference", ASCENDING)], name="payment_model_reference", unique=True),    
        IndexModel([("tenant_id", ASCENDING), ("created_at", DESCENDING)], name="payment_model_tenant_id_created_at"),
        IndexModel([("customer_email", ASCENDING)], name="payment_model_customer_email")
    ]

  model_config = {
      "from_attributes": True,
      "json_encoders": {PydanticObjectId: str},
      "json_schema_extra": {
          "example": {
              "id": "64f95b0c2ab5ec9e0b22c77f",
              "reference": "reference string",
              "tenant_id": "64f95b0c2ab5ec9e0b22c77f",
              "customer_email": "tchidi4real@u.com",
              "amount_minor": "200",
              "currency": True,
              "status": False,                
              "authorization_url": "url path",                
              "metadata": {},                
              "gateway": "paystack",                
              "created_at": "datetime",               
              "paid_at": "datetime",
          }
      },
  }