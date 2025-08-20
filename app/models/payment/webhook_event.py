from __future__ import annotations
from datetime import datetime, timezone
from beanie import Document, PydanticObjectId
from pydantic import Field
from pymongo import ASCENDING, IndexModel

class WebhookEvent(Document):
  event_key: str
  received_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


  class Settings:
    name = "webhook_events"
    indexes = [    
        IndexModel([("event_key", ASCENDING)], name="webhook_events_model_event_key", unique=True),
        IndexModel([("received_at", ASCENDING)], name="webhook_events_model_received_at")
    ]

  model_config = {
      "from_attributes": True,
      "json_encoders": {PydanticObjectId: str},
      "json_schema_extra": {
          "example": {
              "id": "64f95b0c2ab5ec9e0b22c77f",
              "event_key": "event key",               
              "received_at": "datetime",
          }
      },
  }