from email.policy import default
from beanie import Document
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional
from uuid import uuid4
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timezone
from enum import Enum
from pymongo import ASCENDING, DESCENDING

class DiscountType(str, Enum):
    MANUAL = "manual"
    PERCENTAGE = "percentage"
    PROMOTIONAL = "promotional"
    LOYALTY = "loyalty"

class PaymentMethod(str, Enum):
    CASH = "cash"
    CARD = "card"
    TRANSFER = "transfer"
    MOMO = "mobile_money"

class SalesType(str, Enum):
    pos = "POS"
    online = "online"
    other = "Not Specified"

class SaleItem(BaseModel):
    product_id: str = Field(..., min_length=1, max_length=50)
    product_name: str = Field(..., min_length=1, max_length=100)
    quantity: int = Field(..., gt=0)
    unit_price: Decimal = Field(..., gt=0, decimal_places=2, max_digits=10)
    total: Decimal = Field(..., gt=0, decimal_places=2, max_digits=10)
    cost_price: Decimal = Field(..., gt=0, decimal_places=2, max_digits=10)
    cogs: Decimal = Field(..., gt=0, decimal_places=2, max_digits=10)

    @field_validator("total", mode="before")
    @classmethod
    def calculate_total(cls, v, values):
        if v is None:
            return values["unit_price"] * values["quantity"]
        return v.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @field_validator("cogs", mode="before")
    @classmethod
    def calculate_cogs(cls, v, values):
        if v is None:
            return values["cost_price"] * values["quantity"]
        return v.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

class Sale(Document):
    reference: str = Field(
        default_factory=lambda: str(uuid4()),
        min_length=36,
        max_length=36
    )
    receipt_number: Optional[str] = Field(
        default=None,
        index=True,
        unique=True,
        min_length=5,
        max_length=20
    )
    branch_id: str = Field(..., min_length=1, max_length=50)
    department_id: Optional[str] = Field(None, min_length=1, max_length=50)
    warehouse_id: str = Field(..., min_length=1, max_length=50)
    cashier_id: str = Field(..., min_length=1, max_length=50)
    items: List[SaleItem] = Field(..., min_items=1)

    total_amount: Decimal = Field(..., gt=0, decimal_places=2, max_digits=12)
    discount: Decimal = Field(default=0, ge=0, decimal_places=2, max_digits=10)
    discount_type: DiscountType = Field(default=DiscountType.MANUAL)
    net_amount: Decimal = Field(..., gt=0, decimal_places=2, max_digits=12)

    vat_rate: Decimal = Field(default=Decimal("0.075"), ge=0, decimal_places=3, max_digits=5)
    vat_amount: Decimal = Field(..., ge=0, decimal_places=2, max_digits=10)
    gross_amount: Decimal = Field(..., gt=0, decimal_places=2, max_digits=12)

    payment_method: PaymentMethod
    payment_reference: Optional[str] = Field(None, min_length=1, max_length=50)
    sales_type: SalesType = Field(default=SalesType.other, description="Where sales came from")

    is_voided: bool = Field(default=False)
    voided_by: Optional[str] = Field(None, min_length=1, max_length=50)
    voided_at: Optional[datetime] = None
    void_reason: Optional[str] = Field(None, min_length=1, max_length=200)

    created_by: str = Field(..., min_length=1, max_length=50)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "sales"
        indexes = [
            [("branch_id", ASCENDING), ("created_at", DESCENDING)],
            [("cashier_id", ASCENDING), ("created_at", DESCENDING)],
            [("is_voided", ASCENDING), ("created_at", DESCENDING)],
            [("receipt_number", ASCENDING)],
            [("payment_method", ASCENDING), ("created_at", DESCENDING)],
            [("created_at", DESCENDING)],
            [("gross_amount", DESCENDING)],
            [("items.product_id", ASCENDING)]  # For product sales analysis
        ]

    @model_validator(mode="before")
    @classmethod
    def calculate_totals(cls, values):
        items = values.get("items", [])
        discount = values.get("discount", Decimal("0"))
        vat_rate = values.get("vat_rate", Decimal("0.075"))

        total_amount = sum(item["total"] for item in items)
        net_amount = total_amount - discount
        vat_amount = (net_amount * vat_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        gross_amount = (net_amount + vat_amount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        values.update({
            "total_amount": total_amount,
            "net_amount": net_amount,
            "vat_amount": vat_amount,
            "gross_amount": gross_amount
        })
        return values

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "reference": "550e8400-e29b-41d4-a716-446655440000",
                "receipt_number": "POS20250708-0001",
                "branch_id": "branch_123",
                "department_id": "dept_456",
                "warehouse_id": "warehouse_789",
                "cashier_id": "user_901",
                "items": [
                    {
                        "product_id": "prod_123",
                        "product_name": "Sliced Bread",
                        "quantity": 2,
                        "unit_price": Decimal("3.50"),
                        "cost_price": Decimal("2.20"),
                        "total": Decimal("7.00"),
                        "cogs": Decimal("4.40")
                    }
                ],
                "total_amount": Decimal("7.00"),
                "discount": Decimal("0"),
                "discount_type": "manual",
                "net_amount": Decimal("7.00"),
                "vat_rate": Decimal("0.075"),
                "vat_amount": Decimal("0.53"),
                "gross_amount": Decimal("7.53"),
                "payment_method": "cash",
                "payment_reference": "CASH-001",
                "is_voided": False,
                "created_by": "user_901",
                "created_at": "2025-07-08T08:00:00Z",
                "updated_at": "2025-07-08T08:00:00Z"
            }
        }
    }