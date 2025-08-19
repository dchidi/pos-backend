from datetime import datetime
from typing import Optional, List
from pydantic import Field
from beanie import Document, PydanticObjectId
from pymongo import ASCENDING, IndexModel

from app.constants import Currency, TenantTier


class AppCouponAndDiscount(Document):
    name: str = Field(..., description="Label for internal/admin use")
    description: Optional[str] = Field(None, description="What this coupon/discount is for")

    # Type of discount
    discount_percent: Optional[float] = Field(None, ge=0, le=100, description="Percentage off (e.g. 10%)")
    discount_amount: Optional[float] = Field(None, ge=0, description="Fixed currency amount off")

    # Coupon code if applicable
    code: Optional[str] = Field(None, max_length=30, description="If set, this acts as a redeemable coupon code")
    requires_code: bool = Field(default=False, description="If true, must provide matching coupon code to apply")

    # Plan/duration-based rules
    valid_for_plan_ids: Optional[List[PydanticObjectId]] = Field(None, description="Restrict to specific plans")
    valid_for_tiers: Optional[List[TenantTier]] = Field(None, description="Restrict to specific plan tiers")
    valid_durations_in_days: Optional[List[int]] = Field(None, description="Only apply if subscription matches duration")

    # Activation control
    currency: Optional[Currency] = Field(default=None, description="Applies to subscriptions in this currency (optional)")
    start_date: Optional[datetime] = Field(None, description="When this becomes active")
    end_date: Optional[datetime] = Field(None, description="When this expires")

    # Usage control
    max_redemptions: Optional[int] = Field(None, ge=1, description="Max total uses allowed")
    times_redeemed: int = Field(default=0, description="How many times it has been redeemed")
    active: bool = Field(default=True)
    stackable: bool = Field(default=False, description="Can this be combined with other discounts?")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "app_coupon_discounts"
        indexes = [
            IndexModel([("code", ASCENDING)], name="discount_code_idx"),
            IndexModel([("active", ASCENDING)], name="discount_active_idx"),
            IndexModel([("start_date", ASCENDING), ("end_date", ASCENDING)], name="discount_validity_range_idx"),
        ]
        
    model_config = {
        "from_attributes": True,
        "json_schema_extra" : {
            "example": {
                "name": "Summer Promo 20%",
                "description": "20% off all pro-tier plans in USD",
                "discount_percent": 20.0,
                "code": "SUMMER20",
                "requires_code": True,
                "valid_for_tiers": ["pro"],
                "currency": "USD",
                "start_date": "2025-08-01T00:00:00Z",
                "end_date": "2025-09-01T00:00:00Z",
                "max_redemptions": 500,
                "times_redeemed": 24,
                "active": True,
                "stackable": False
            }
        }
    }