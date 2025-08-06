from beanie import Document, Indexed, PydanticObjectId
from pydantic import Field, field_validator
from typing import Annotated

from app.models.base import TimeStampMixin                      
       

class Region(Document, TimeStampMixin):

    name: Annotated[
        str,
        Indexed(
            unique=True,
            name="region_model_name",
            collation={"locale": "en", "strength": 2},
        ),
    ] = Field(..., min_length=2, max_length=100,  description="Region name (unique, case-insensitive)")

    code: Annotated[
        str,
        Indexed(unique=True, name="region_model_code"),
    ] = Field(...)

    country_id: Annotated[
        PydanticObjectId,
        Indexed(
            name="region_model_country_id",
        ),
    ] = Field(..., description="Country ID")
    
    company_id: Annotated[
        PydanticObjectId,
        Indexed(
            name="region_model_company_id",
        ),
    ] = Field(..., description="Company/Rental ID")

    class Settings:
        name = "regions"
        indexes = [
            [("country_id", 1), ("company_id", 1)],
            [("country_id", 1), ("company_id", 1), ("name", 1)]
        ]

    @field_validator("code", mode="before")
    @classmethod
    def _upper(cls, v: str) -> str:  # noqa: D401, N802
        """Normalise to uppercase so users can send either 'ng' or 'NG'."""
        return v.upper()
