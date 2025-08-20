from __future__ import annotations
from typing import Optional
from beanie import Document, PydanticObjectId
from pydantic import Field, EmailStr
from pymongo import ASCENDING, DESCENDING, IndexModel

from app.models.base import TimeStampMixin

class Subscription(Document, TimeStampMixin):
  tenant_id: PydanticObjectId
  customer_email: EmailStr
  plan_code: str
  status: str = Field(default="incomplete") # active|trialing|past_due|canceled|incomplete
  authorization_code: Optional[str] = None
  subscription_code: Optional[str] = None
  email_token: Optional[str] = None
  gateway: str = Field(default="paystack")


  class Settings:
    name = "subscriptions"
    indexes = [    
        IndexModel([("tenant_id", ASCENDING), ("customer_email", DESCENDING)], name="subscriptions_model_tenant_id_customer_email"),
        IndexModel([("plan_code", ASCENDING)], name="subscriptions_model_plan_code")
    ]

  model_config = {
      "from_attributes": True,
      "json_encoders": {PydanticObjectId: str},
      "json_schema_extra": {
          "example": {
              "id": "64f95b0c2ab5ec9e0b22c77f",
              "tenant_id": "64f95b0c2ab5ec9e0b22c77f",
              "customer_email": "tchidi4real@u.com",
              "plan_code": "200",
              "status": "active",                
              "authorization_code": "auth code",                
              "subscription_code": "sub code", 
              "email_token": "email token",                
              "gateway": "paystack",                
              "created_at": "datetime",               
              "updated_at": "datetime",
          }
      },
  }