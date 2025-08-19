from datetime import datetime, timezone
from beanie import Document, Indexed
from pydantic import BaseModel, Field
from typing import Optional
from app.constants import LogLevel

from pymongo import ASCENDING, DESCENDING, IndexModel


class Log(Document):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user_id: Optional[str] = None  # The user who triggered the log
    endpoint: Optional[str] = None  # The API endpoint accessed
    action: str  # What the user did or attempted
    level: str = LogLevel.INFO  # Log level: INFO, WARNING, ERROR, SECURITY
    details: Optional[dict] = None  # Any extra info you want to store

    # Optional: index for faster queries
    class Settings:
        name = "logs"
        indexes = [
            # Single-field index on user_id with custom name
            IndexModel(
                [("user_id", ASCENDING)],
                name="log_model_user_id_idx"
            ),
            # TTL index on timestamp with custom name
            IndexModel(
                [("timestamp", ASCENDING)],
                expireAfterSeconds=60*60*24*1,  # 1 day
                name="log_model_timestamp_idx"
            ),
            # Index on level for fast filtering
            IndexModel(
                [("level", ASCENDING)],
                name="log_model_level_idx"
            ),
            # Composite index on (level, timestamp) for common queries
            IndexModel(
                [("level", ASCENDING), ("timestamp", DESCENDING)],
                name="log_model_level_timestamp_idx"
            )
        ]

    model_config = {
        "json_schema_extra": {
            "example": {
                "timestamp": "2025-08-18T12:00:00Z",
                "user_id": "user_123",
                "endpoint": "/api/items",
                "action": "Unauthorized access attempt",
                "level": "SECURITY",
                "details": {"required_role": "admin"}
            }
        }
     }

