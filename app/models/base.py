from pydantic import BaseModel, Field
from datetime import datetime, timezone

class TimeStampMixin(BaseModel):
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    is_active: bool = True
    is_deleted: bool = False

    model_config = {"from_attributes": True}