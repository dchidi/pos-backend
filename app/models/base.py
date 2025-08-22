from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone
from typing import Optional
from beanie import PydanticObjectId, before_event, Insert, Replace, Update


class TimeStampMixin(BaseModel):
    """
    Simplified UTC-only timestamp mixin:
    - All timestamps stored in UTC
    - Frontend handles local time conversion
    """

    # Core timestamp fields (UTC only)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when record was created"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when last updated"
    )
    
    deleted_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when record was deleted"
    )
    # Status flags
    is_active: bool = Field(
        default=True,
        description="Active status flag (soft delete)"
    )
    is_deleted: bool = Field(
        default=False,
        description="Soft deletion flag"
    )

    # Audit fields
    created_by: Optional[PydanticObjectId] = Field(
        default=None,
        description="User ID who created the record"
    )
    updated_by: Optional[PydanticObjectId] = Field(
        default=None,
        description="User ID who last updated the record"
    )
    
    deleted_by: Optional[PydanticObjectId] = Field(
        default=None,
        description="User ID who deleted the record"
    )
    # Simplified timestamp handlers
    @before_event([Insert])
    async def _set_initial_timestamps(self):
        """Set both timestamps to current UTC time"""
        now = datetime.now(timezone.utc)
        self.created_at = now
        self.updated_at = now

    @before_event([Replace, Update])
    async def _touch_updated_at(self):
        """Update timestamp to current UTC time"""
        self.updated_at = datetime.now(timezone.utc)

    # Validation (ensures UTC)
    @field_validator("created_at", "updated_at")
    @classmethod
    def ensure_utc(cls, v: datetime) -> datetime:
        """Validate datetime is UTC timezone-aware"""
        if v.utcoffset() != timezone.utc.utcoffset(None):
            raise ValueError("Timestamps must be in UTC")
        return v
