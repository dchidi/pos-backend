from beanie import Document, PydanticObjectId
from pydantic import Field
from typing import Optional, Set
from pymongo import ASCENDING, IndexModel
from app.models.base import TimeStampMixin
from app.constants import RoleStatus


class Role(Document, TimeStampMixin):    
    name: str = Field(..., description="Unique role name")
    permissions:  Optional[Set[str]] = Field(default_factory=set)
    exclusions:  Optional[Set[str]] = Field(default_factory=set)
    description: Optional[str] = None

    company_id: Optional[PydanticObjectId] = None


    class Settings:
        name = "roles"
        indexes = [        
            IndexModel([("name", ASCENDING), ("status", ASCENDING), ("company_id", ASCENDING)], name="role_model_name_status_company_id"),
            IndexModel([("company_id", ASCENDING)], name="role_company_id_idx")
        ]

    model_config = {
        "from_attributes": True,
        "json_encoders": {PydanticObjectId: str},
        "json_schema_extra": {
            "example": {
                "id": "64f95b0c2ab5ec9e0b22c77f",
                "name": "manager",
                "permissions": ["user:view", "user:edit"],
                "exclusions": ["user:hard_delete"],
                "company_id": "64f95b0c2ab5ec9e0b22c780",
                "is_active": True,
                "is_deleted": False,                
                "created_by": "64f95b0c2ab5ec9e0b22c780",                
                "updated_by": "64f95b0c2ab5ec9e0b22c780",                
                "created_at": "datetime",                
                "updated_at": "datetime",
            }
        },
    }