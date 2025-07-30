from pydantic import BaseModel, Field, PositiveFloat
from typing import Optional, List
from datetime import datetime

from app.constants.tenants_enum import TenantTier
from app.constants.currency_enum import Currency
from app.schemas.base import BaseResponse
from app.schemas import PyObjectId


class PlanBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Name of the subscription plan")
    description: Optional[str] = Field(None, description="Short summary of what the plan includes")

    price: PositiveFloat = Field(..., description="Cost of the plan in the default currency")
    currency: Currency = Field(..., description="Currency for pricing")

    tier: TenantTier = Field(..., description="Tier of the plan")
    duration_in_days: int = Field(..., gt=0, description="Duration of the subscription in days")

    features: List[str] = Field(default_factory=list, description="Features included in the plan")
    is_trial_available: bool = Field(default=False, description="Is trial available?")
    trial_period_days: Optional[int] = Field(None, description="Length of the trial period, if available")


class PlanCreate(PlanBase):
    created_by: Optional[PyObjectId] = None
    updated_by: Optional[PyObjectId] = None


class PlanUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None

    price: Optional[PositiveFloat] = None
    currency: Optional[Currency] = None

    tier: Optional[TenantTier] = None
    duration_in_days: Optional[int] = Field(None, gt=0)

    features: Optional[List[str]] = None
    is_trial_available: Optional[bool] = None
    trial_period_days: Optional[int] = None

    updated_by: Optional[PyObjectId] = None


class PlanResponse(PlanBase, BaseResponse):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[PyObjectId] = None
    updated_by: Optional[PyObjectId] = None
