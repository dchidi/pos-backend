# app/models/payment/webhook_event.py
from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from beanie import Document, PydanticObjectId
from pydantic import Field
from pymongo import ASCENDING, IndexModel

class WebhookEvent(Document):
    # Idempotency key (e.g., paystack data.id or fallback to reference)
    event_key: str

    # Helpful metadata (optional, for quick queries)
    event: Optional[str] = None
    reference: Optional[str] = None

    # Timestamps
    gateway_paid_at: Optional[datetime] = None
    received_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Full webhook payload for audit/debug
    payload: Optional[Dict[str, Any]] = None

    class Settings:
        name = "webhook_events"
        indexes = [
            IndexModel([("event_key", ASCENDING)], name="webhook_events_event_key", unique=True),
            IndexModel([("received_at", ASCENDING)], name="webhook_events_received_at"),
            IndexModel([("reference", ASCENDING)], name="webhook_events_reference"),
            IndexModel([("gateway_paid_at", ASCENDING)], name="webhook_events_gateway_paid_at"),
        ]

    model_config = {
        "from_attributes": True,
        "json_encoders": {PydanticObjectId: str},
        "json_schema_extra": {
            "example": {
                "id": "64f95b0c2ab5ec9e0b22c77f",
                "event_key": "charge.success:ABC123",
                "event": "charge.success",
                "reference": "ABC123",
                "gateway_paid_at": "2024-01-01T12:34:56Z",
                "received_at": "2024-01-01T12:34:58Z",
                "payload": {"event": "charge.success", "data": {"reference": "ABC123", "...": "..."}}
            }
        },
    }
