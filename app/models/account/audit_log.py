# accounting/models/audit_log.py

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any

from beanie import Document, Indexed
from pydantic import BaseModel, Field


class AuditAction(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class AuditLog(Document):
    model_name: str = Field(..., description="The name of the model being audited, e.g., 'Account'")
    document_id: str = Field(..., description="The ID of the audited document")
    action: AuditAction = Field(..., description="Type of action performed")

    changed_by: str = Field(..., description="User or system ID that made the change")
    changed_at: datetime = Field(default_factory=datetime.utcnow)

    changes: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Field-level changes, e.g., { 'name': ['Old Name', 'New Name'] }"
    )

    reason: Optional[str] = Field(None, description="Optional comment or reason for the change")

    class Settings:
        name = "audit_logs"

    class Config:
        schema_extra = {
            "example": {
                "model_name": "Account",
                "document_id": "664f8a78a843d1ee9047dc12",
                "action": "UPDATE",
                "changed_by": "admin_user_id",
                "changes": {
                    "name": ["Cash", "Cash at Bank"],
                    "currency": ["USD", "NGN"]
                },
                "reason": "Updated for branch compliance"
            }
        }
