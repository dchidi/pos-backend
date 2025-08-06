from beanie import Document
from pydantic import Field, field_validator
from datetime import datetime, timezone
from typing import Optional
from decimal import Decimal
from pymongo import ASCENDING
from enum import Enum

from app.constants import StockStatus

class WarehouseStock(Document):
    product_id: str = Field(..., description="Reference to product document")
    warehouse_id: str = Field(..., description="Reference to warehouse document")
    quantity: int = Field(..., gt=0, description="Current stock quantity (must be positive)")
    physical_location: Optional[str] = Field(
        None,
        max_length=50,
        description="Storage location (e.g., 'Aisle 3, Shelf B2')"
    )
    cost_price: Optional[Decimal] = Field(
        None,
        max_digits=10,
        decimal_places=2,
        description="Last purchase cost for FIFO calculations"
    )
    received_date: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When stock was received"
    )
    batch_reference: Optional[str] = Field(
        None,
        max_length=30,
        description="Manufacturer batch/lot number"
    )
    expiry_date: Optional[datetime] = Field(
        None,
        description="Expiration date for perishable goods"
    )
    status: StockStatus = Field(
        default=StockStatus.ACTIVE,
        description="Stock condition status"
    )
    created_by: Optional[str] = Field(
        None,
        description="User ID who created this record"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Record creation timestamp"
    )
    last_updated: Optional[datetime] = Field(
        None,
        description="Last modification timestamp"
    )
    reorder_level: Optional[int] = Field(
        None,
        ge=0,
        description="Minimum stock level before reordering"
    )
    minimum_stock_threshold: Optional[int] = Field(
        None,
        ge=0,
        description="Critical low stock threshold"
    )

    class Settings:
        name = "warehouse_stocks"
        indexes = [
            # Primary product tracking (FIFO optimized)
            [("product_id", ASCENDING), ("received_date", ASCENDING)],
            
            # Warehouse inventory views
            [("warehouse_id", ASCENDING), ("product_id", ASCENDING)],
            
            # Expiry management
            [("expiry_date", ASCENDING), ("status", ASCENDING)],
            
            # Location tracking
            [("physical_location", ASCENDING)],
            
            # Status monitoring
            [("status", ASCENDING), ("warehouse_id", ASCENDING)],
            
            # Batch tracking
            [("batch_reference", ASCENDING)],
            
            # Replenishment alerts
            [("warehouse_id", ASCENDING), ("quantity", ASCENDING)]
        ]

    @field_validator('expiry_date')
    def validate_expiry_date(cls, v):
        if v and v < datetime.now(timezone.utc):
            raise ValueError("Expiry date cannot be in the past")
        return v

    @field_validator('quantity')
    def validate_quantity(cls, v, values):
        if 'minimum_stock_threshold' in values and values['minimum_stock_threshold']:
            if v < values['minimum_stock_threshold']:
                raise ValueError("Quantity below minimum threshold")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "product_id": "prd_123456",
                "warehouse_id": "wh_789012",
                "quantity": 150,
                "physical_location": "Zone-A/Rack-4/Shelf-2",
                "cost_price": "285.50",
                "received_date": "2025-07-15T09:30:00Z",
                "batch_reference": "LOT-2025-Q3-001",
                "expiry_date": "2026-01-31T00:00:00Z",
                "status": "active",
                "created_by": "user_901234",
                "created_at": "2025-07-15T09:35:00Z",
                "last_updated": "2025-07-20T14:15:00Z",
                "reorder_level": 50,
                "minimum_stock_threshold": 20
            }
        },
        "from_attributes": True
    }