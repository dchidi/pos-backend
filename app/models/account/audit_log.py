from datetime import datetime, timezone
from typing import Optional, Dict, Any

from beanie import Document
from pydantic import Field

from app.constants import AuditAction


class AuditLog(Document):
    model_name: str = Field(..., description="The name of the model being audited, e.g., 'Account'")
    document_id: str = Field(..., description="The ID of the audited document")
    action: AuditAction = Field(..., description="Type of action performed")

    changed_by: str = Field(..., description="User or system ID that made the change")
    changed_at: datetime = Field(default_factory=datetime.now(timezone.utc))

    changes: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Field-level changes, e.g., { 'name': ['Old Name', 'New Name'] }"
    )

    reason: Optional[str] = Field(None, description="Optional comment or reason for the change")

    class Settings:
        name = "audit_logs"

 