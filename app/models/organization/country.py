from beanie import Document, Indexed, PydanticObjectId
from pydantic import Field, field_validator
from typing import Optional, Annotated
from app.models.base import TimeStampMixin                      
         

class Country(Document, TimeStampMixin):

    name: Annotated[
        str,
        Indexed(
            unique=True,
            name="country_model_name",
            collation={"locale": "en", "strength": 2},
        ),
    ] = Field(..., description="Country name (unique, case-insensitive)")

    code: Annotated[
        str,
        Indexed(unique=True, name="country_model_code"),
    ] = Field(...)

    created_by: Optional[PydanticObjectId] = Field(
        default=None, description="User who created the record"
    )
    updated_by: Optional[PydanticObjectId] = Field(
        default=None, description="User who last updated the record"
    )

    class Settings:
        name = "countries"

    @field_validator("code", mode="before")
    @classmethod
    def _upper(cls, v: str) -> str:  # noqa: D401, N802
        """Normalise to uppercase so users can send either 'ng' or 'NG'."""
        return v.upper()

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Nigeria",
                "code": "NG",
                "created_by": "64f95b0c2ab5ec9e0b22c77f",
                "updated_by": "64f95b0c2ab5ec9e0b22c77f",
                "is_active": True,
                "created_at": "2025-07-08T08:00:00Z",
                "updated_at": "2025-07-08T10:00:00Z",
            }
        }
    }
