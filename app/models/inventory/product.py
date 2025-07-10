from beanie import Document, Indexed
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional, Annotated
import uuid
import re
from pymongo import ASCENDING


def generate_sku(prefix: str, name: str) -> str:
    name_code = ''.join(word[0].upper() for word in re.findall(r'\w+', name)[:2])
    unique_suffix = uuid.uuid4().hex[:4].upper()
    return f"{prefix}-{name_code}-{unique_suffix}"


class ProductUnitConversion(BaseModel):
    unit_id: str  # Reference to Unit document
    name_override: Optional[str] = None  # e.g., "Carton (12)"
    base_unit_equivalent: int = 1  # e.g., 1 carton = 12 base units
    price_per_unit: Decimal = Field(max_digits=10, decimal_places=2)
    is_default_for_sale: bool = False
    is_default_for_purchase: bool = False


class Product(Document):
    name: str
    code: Annotated[str, Indexed(unique=True)]  # Internal product code
    sku: Annotated[Optional[str], Indexed(unique=True)] = None
    barcode: Annotated[Optional[str], Indexed(unique=True)] = None
    description: Optional[str] = None

    category_id: str
    brand_id: str    
    supplier_id: str

    base_unit_id: str  # Reference to Unit (e.g., "Piece")
    unit_conversions: List[ProductUnitConversion] = []

    price: Decimal = Field(max_digits=10, decimal_places=2)  # Base unit selling price
    cost_price: Optional[Decimal] = Field(None, max_digits=10, decimal_places=2)
    
    is_serialized: bool = False  # For tracking items by serial numbers

    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    is_active: bool = True
    revision: str = Field(default_factory=lambda: str(uuid.uuid4()))  # For optimistic concurrency

    class Settings:
        name = "products"
        indexes = [
            [("category_id", ASCENDING), ("is_active", ASCENDING)],
            [("brand_id", ASCENDING), ("is_active", ASCENDING)],
            [("name", "text"), ("description", "text")],
            [("supplier_id", ASCENDING)]
        ]
        
    async def insert(self, *args, **kwargs):
        if not self.sku:
            try:
                prefix = self.code.split("-")[0] if "-" in self.code else self.code[:3].upper()
                self.sku = generate_sku(prefix=prefix, name=self.name)
            except Exception as e:
                raise ValueError(f"Failed to generate SKU: {str(e)}")
        return await super().insert(*args, **kwargs)

    @field_validator('barcode')
    def validate_barcode(cls, v):
        if v and not v.isdigit():
            raise ValueError("Barcode must contain only digits")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Sliced Bread",
                "code": "PRD001",
                "sku": "PRD-SB-1A2B",
                "barcode": "8934567890123",
                "description": "Freshly baked sliced bread",
                "category_id": "cat_obj_id",
                "brand_id": "brand_obj_id",
                "supplier_id": "supplier_obj_id",
                "base_unit_id": "unit_piece_id",
                "unit_conversions": [
                    {
                        "unit_id": "unit_carton_id",
                        "name_override": "Carton (12)",
                        "base_unit_equivalent": 12,
                        "price_per_unit": 3600.00,
                        "is_default_for_sale": False,
                        "is_default_for_purchase": True
                    },
                    {
                        "unit_id": "unit_piece_id",
                        "base_unit_equivalent": 1,
                        "price_per_unit": 300.00,
                        "is_default_for_sale": True,
                        "is_default_for_purchase": False
                    }
                ],
                "price": 300.00,
                "cost_price": 220.00,
                "is_serialized": False,
                "created_by": "user_id_1",
                "is_active": True,
                "created_at": "2025-07-08T08:00:00Z",
                "revision": "550e8400-e29b-41d4-a716-446655440000"
            }
        },
        "from_attributes": True
    }