from beanie import Document, PydanticObjectId
from pydantic import Field, field_validator
from typing import Optional
from pymongo import ASCENDING, DESCENDING
from app.constants.warehouse_enum import WarehouseType
from app.models.base import TimeStampMixin


class Warehouse(Document, TimeStampMixin):
    name: str = Field(..., min_length=3, max_length=100, description="Warehouse display name")
    code: str = Field(..., min_length=2, max_length=100, description="Short unique identifier (e.g., 'WH-MAIN')")
    branch_id: PydanticObjectId = Field(..., description="Associated branch reference")
    warehouse_type: WarehouseType = Field(
        default=WarehouseType.USER,
        description="Classification of warehouse"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Detailed description of warehouse"
    )
    location: Optional[str] = Field(
        None,
        max_length=200,
        description="Physical address or location identifier. Physical warehouse ONLY"
    )
    capacity: Optional[int] = Field(
        None,
        gt=0,
        description="Total storage capacity in cubic meters. Physical warehouse ONLY"
    )

    created_by: Optional[str] = Field(
        None,
        description="User ID who created this record"
    )
    updated_by: Optional[str] = Field(
        None,
        description="User ID who last updated this record"
    )

    class Settings:
        name = "warehouses"
        indexes = [
            # Primary operational indexes
            [("branch_id", ASCENDING), ("warehouse_type", ASCENDING)],
            [("code", ASCENDING)],
            
            # Management indexes
            [("is_active", ASCENDING), ("warehouse_type", ASCENDING)],
            [("created_at", DESCENDING)],  # For recent entries
            
            # Location search
            [("location", "text")]
        ]

    @field_validator('name')
    def validate_name(cls, v):
        if any(char in v for char in '\\/*?"<>|'):
            raise ValueError("Name contains invalid characters")
        return v.strip()

    @field_validator('code')
    def validate_code(cls, v):
        if not v.isalnum() and '-' not in v:
            raise ValueError("Code must be alphanumeric with optional hyphens")
        return v.upper()

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Main Branch Warehouse",
                "code": "WH-MAIN",
                "branch_id": "branch_123",
                "warehouse_type": "branch",
                "description": "Primary storage facility for Lagos branch",
                "location": "23 Bode Thomas Street, Surulere, Lagos",
                "capacity": 1500,
                "is_active": True,
                "created_by": "user_901234",
                "updated_by": "user_901234",
                "created_at": "2025-07-15T09:30:00Z",
                "updated_at": "2025-07-20T14:15:00Z"
            }
        },
        "from_attributes": True
    }