from decimal import Decimal
from beanie import Document, Indexed
from pydantic import Field, BaseModel, field_validator
from datetime import datetime, timezone
from typing import List, Optional, Annotated
from enum import Enum
from pymongo import ASCENDING, DESCENDING

class TransferStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    IN_TRANSIT = "in_transit"

class StockTransferItem(BaseModel):
    product_id: str
    quantity: int = Field(gt=0, description="Must be positive")
    cost_price: Optional[Decimal] = Field(None, max_digits=10, decimal_places=2)
    batch_reference: Optional[str] = Field(None, max_length=50)
    expiry_date: Optional[datetime] = None
    temperature_log: Optional[List[float]] = Field(
        None,
        description="Temperature readings for cold chain tracking"
    )

    @field_validator('temperature_log')
    def validate_temperatures(cls, v):
        if v and any(temp < -50 or temp > 50 for temp in v):
            raise ValueError("Temperature readings must be between -50 and 50°C")
        return v

class WarehouseStockTransferLog(Document):
    transfer_code: Annotated[str, Indexed(unique=True)]  # Format: "TRF-YYYYMMDD-XXXX"
    source_warehouse_id: str
    destination_warehouse_id: str
    items: List[StockTransferItem] = Field(min_length=1)

    initiated_by: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None  # New field for completion timestamp

    transfer_status: TransferStatus = Field(default=TransferStatus.PENDING)
    notes: Optional[str] = Field(None, max_length=500)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    estimated_transit_time: Optional[int] = Field(
        None,
        ge=0,
        description="Estimated transit time in hours"
    )

    class Settings:
        name = "stock_transfers"
        indexes = [
            [("source_warehouse_id", ASCENDING), ("transfer_status", ASCENDING)],
            [("destination_warehouse_id", ASCENDING), ("transfer_status", ASCENDING)],
            [("created_at", DESCENDING)],  # For recent transfers first
            [("items.product_id", ASCENDING)],  # For product-level queries
            [("transfer_status", ASCENDING), ("approved_at", DESCENDING)]
        ]

    model_config = {
        "json_schema_extra": {
            "example": {
                "transfer_code": "TRF-20250708-0001",
                "source_warehouse_id": "wh_main_id",
                "destination_warehouse_id": "wh_branch_1",
                "items": [
                    {
                        "product_id": "prd_obj_id",
                        "quantity": 10,
                        "cost_price": 280.00,
                        "batch_reference": "BATCH-JUL-01",
                        "expiry_date": "2025-09-30T00:00:00Z",
                        "temperature_log": [2.5, 3.0, 2.8]
                    }
                ],
                "initiated_by": "user_id_1",
                "approved_by": "user_id_2",
                "approved_at": "2025-07-08T10:00:00Z",
                "completed_at": "2025-07-08T15:30:00Z",
                "transfer_status": "completed",
                "notes": "Transfer for stock balancing",
                "estimated_transit_time": 4
            }
        },
        "from_attributes": True
    }