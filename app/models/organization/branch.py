from beanie import Document, PydanticObjectId
from typing import Optional
from app.models.base import TimeStampMixin

class Branch(Document, TimeStampMixin):
    name: str
    code: str  # unique code like "BR001"
    address: Optional[str] = None
    
    created_by: Optional[PydanticObjectId] = None
    updated_by: Optional[PydanticObjectId] = None

    state_id: Optional[PydanticObjectId] = None
    area_id: Optional[PydanticObjectId] = None
    region_id: Optional[PydanticObjectId] = None    
    country_id: Optional[PydanticObjectId] = None


    class Settings:
        name = "branches"

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Asaba Central",
                "code": "BR001",
                "address": "123 Main Street, Asaba",
                "created_by": "user_id_1",
                "updated_by": "user_id_2",
                "is_active": True,
                "created_at": "2025-07-08T08:00:00Z",
                "updated_at": "2025-07-08T10:00:00Z"
            }
        },
        "from_attributes": True
    }
