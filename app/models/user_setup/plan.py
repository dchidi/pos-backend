from beanie import Document
from pydantic import Field, field_validator
from typing import Optional, List
from pymongo import ASCENDING, IndexModel

from app.models.base import TimeStampMixin

from app.constants.tenants_enum import TenantTier
from app.constants.currency_enum import Currency


class Plan(Document, TimeStampMixin):
    name: str = Field(..., min_length=2, max_length=100, description="Name of the subscription plan")
    description: Optional[str] = Field(None, description="Short summary of what the plan includes")

    price: float = Field(..., description="Cost of the plan in default currency")
    currency: Currency = Field(default=Currency.US_DOLLAR, description="Currency for pricing", example="NGN, USD, GBP, EUR")

    tier: TenantTier = Field(..., description="Tier of the plan", example="free, basic, pro, enterprise")
    duration_in_days: int = Field(..., gt=0, description="Duration of the subscription in days")

    features: List[str] = Field(default_factory=list, description="List of features included in the plan")
    is_trial_available: bool = Field(False, description="Indicates if a trial is available for this plan")
    trial_period_days: Optional[int] = Field(None, description="Length of trial period if available")

    number_of_users: int = Field(..., gt=0, description="Number of users allowed on the plan")
    number_of_branch: int = Field(default=0, description="Number of branches a company is allowed to have")

    class Settings:
        name = "plans"
        indexes = [
            IndexModel([("name", ASCENDING)], name="plan_model_name"),
            IndexModel([("tier", ASCENDING)], name="plan_model_tier"),
            IndexModel([("price", ASCENDING)], name="plan_model_price"),
        ]

    @field_validator('price')
    def check_price(cls, v):
        if v < 0:
            raise ValueError('Price must be greater than 0')
        return v

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "name": "Starter Plan",
                "description": "Best for small teams just starting out",
                "price": 0.0,
                "currency": "USD",
                "tier": "Free",
                "duration_in_days": 30,
                "features": ["1 user", "Basic analytics", "Email support"],
                "is_active": True,
                "is_trial_available": True,
                "trial_period_days": 14
            }
        },
    }
