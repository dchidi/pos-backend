from beanie import Document
from pydantic import Field
from datetime import datetime, timezone
from typing import Optional


class BrandSupplierLink(Document):
    brand_id: str
    supplier_id: str
    valid_from: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    valid_to: Optional[datetime] = None  # optional end of relationship

    class Settings:
        name = "brand_supplier_links"
