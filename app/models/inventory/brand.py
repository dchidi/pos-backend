from pydantic import Field, AnyUrl
from typing import Optional, List, Annotated
from beanie import Indexed, Document, PydanticObjectId
from app.models.base import TimeStampMixin

class Brand(Document, TimeStampMixin):
    name: Annotated[
        str,
        Indexed(
            name="uq_brands_name",
            unique=True,
            collation={"locale": "en", "strength": 2}
        )
    ] = Field(..., description="Unique name of the brand")

    description: Optional[str] = Field(None, description="Brand description")
    logo_url: Optional[AnyUrl] = Field(None, description="URL to brand logo")
    category_ids: List[PydanticObjectId] = Field(default_factory=list, description="Associated category IDs")

    company_id: Optional[PydanticObjectId] = Field(
        default=None,
        description="The company or manufacturer that owns the brand"
    )

    class Settings:
        name = "brands"
        indexes = [
            "company_id", 
            "category_ids"
        ]


    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Golden Crust",
                "description": "Premium bakery brand",
                "logo_url": "https://example.com/logo.png",
                "company_id": "64f95b0c2ab5ec9e0b22c77f",
                "category_ids": [],
                "created_at": "2025-07-08T10:00:00Z",
                "is_active": True
            }
        },
        "from_attributes": True
    }
