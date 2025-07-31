from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.constants.currency_enum import Currency
from app.constants.status_enum import TenantTier
from app.schemas import PyObjectId
from app.schemas.base import BaseResponse


class AppCouponDiscountBase(BaseModel):
    name: Optional[str] = Field(None, description="Internal label or admin name for this discount/coupon")
    description: Optional[str] = Field(None, description="Optional description for this discount")

    discount_percent: Optional[float] = Field(None, ge=0, le=100, description="Percentage discount (e.g. 20)")
    discount_amount: Optional[float] = Field(None, ge=0, description="Fixed amount off in specified currency")

    code: Optional[str] = Field(None, max_length=30, description="Optional coupon code")
    requires_code: Optional[bool] = Field(default=False, description="True if code is required to apply")

    valid_for_plan_ids: Optional[List[PyObjectId]] = Field(None, description="Restrict to specific plan IDs")
    valid_for_tiers: Optional[List[TenantTier]] = Field(None, description="Restrict to specific tenant tiers")
    valid_durations_in_days: Optional[List[int]] = Field(None, description="Only applies to these subscription durations")

    currency: Optional[Currency] = Field(None, description="Currency to restrict this discount to")
    start_date: Optional[datetime] = Field(None, description="When this discount becomes active")
    end_date: Optional[datetime] = Field(None, description="When this discount expires")

    max_redemptions: Optional[int] = Field(None, ge=1, description="Max number of redemptions allowed")
    times_redeemed: Optional[int] = Field(default=0, description="Times this has been redeemed")
    active: Optional[bool] = Field(default=True, description="Is this discount currently active?")
    stackable: Optional[bool] = Field(default=False, description="Can be combined with other discounts")


class AppCouponDiscountCreate(AppCouponDiscountBase):
    pass


class AppCouponDiscountUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

    discount_percent: Optional[float] = Field(None, ge=0, le=100)
    discount_amount: Optional[float] = Field(None, ge=0)

    code: Optional[str] = Field(None, max_length=30)
    requires_code: Optional[bool] = None

    valid_for_plan_ids: Optional[List[PyObjectId]] = None
    valid_for_tiers: Optional[List[TenantTier]] = None
    valid_durations_in_days: Optional[List[int]] = None

    currency: Optional[Currency] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    max_redemptions: Optional[int] = Field(None, ge=1)
    times_redeemed: Optional[int] = None
    active: Optional[bool] = None
    stackable: Optional[bool] = None


class AppCouponDiscountResponse(AppCouponDiscountBase, BaseResponse):
    id: PyObjectId
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
