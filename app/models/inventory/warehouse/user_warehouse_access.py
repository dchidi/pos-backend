from beanie import PydanticObjectId, Document
from typing import Optional

class UserWarehouseAccess(Document):
    user_id: PydanticObjectId 
    company_id: PydanticObjectId 
    warehouse_id: PydanticObjectId
    access_level: Optional[str] = None  # e.g., "admin", "viewer", "manager"
    
    class Settings:
        indexes = [
            [("user_id", 1), ("warehouse_id", 1), ("company_id", 1)],  # Compound unique index
        ]