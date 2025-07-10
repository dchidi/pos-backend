from typing import Set, Optional
from beanie import Document
from pydantic import Field, ConfigDict
from datetime import datetime, timezone
from pymongo import ASCENDING, DESCENDING

from app.schemas.enums import RoleStatus



class Role(Document):
  name: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
  status: RoleStatus = RoleStatus.ACTIVE
  permissions: Set[str]
  description: Optional[str] = Field(None, max_length=200)
  created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
  updated_at: Optional[datetime] = None
  created_by: Optional[str] = None  # Track who created the role
  last_modified_by: Optional[str] = None  # Track who last modified

  class Settings:
      name = "roles"
      use_state_management = True
      indexes = [
          "name",  # Single field index
          [("status", ASCENDING), ("created_at", DESCENDING)],  # Compound index
      ]

  model_config = ConfigDict(
      json_schema_extra={
          "example": {
              "name": "user_manager",
              "status": "active",
              "permissions": ["can_view_user", "can_edit_user"],
              "description": "Manages basic user operations",
              "created_at": "2025-07-05T11:00:00Z"
          }
      },
      from_attributes=True
  )

  async def update_timestamp(self):
      """Update the updated_at field"""
      self.updated_at = datetime.now(timezone.utc)
      await self.save()