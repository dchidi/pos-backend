# from beanie import Document, Indexed
# from pydantic import Field, field_validator
# from typing import Optional
# from decimal import Decimal
# from datetime import datetime, timezone
# import uuid


# class SupplierRating(Document):
#     supplier_id: str
#     delivery_score: int = Field(..., ge=1, le=5) # All scores should be automatically generated based on policy settings and users should not manually enter them to avoid impartiality
#     quality_score: int = Field(..., ge=1, le=5)
#     responsiveness_score: int = Field(..., ge=1, le=5)
#     compliance_score: Optional[int] = Field(None, ge=1, le=5)
#     notes: Optional[str] = None # This should auto populate from the form user used to receive goods

#     overall_score: Decimal = Field(..., max_digits=3, decimal_places=2)  # average of above scores
#     rating_context: Optional[str] = Field(None, description="Optional — e.g., PO ID or audit session")
    
#     created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
#     version: int = Field(default=1)

#     class Settings:
#         name = "supplier_ratings"
#         indexes = [
#             ("supplier_id", 1),
#             ("rated_by", 1),
#             ("created_at", 1),
#         ]

#     @field_validator("overall_score")
#     def validate_score_range(cls, v):
#         if v < 1 or v > 5:
#             raise ValueError("Overall score must be between 1 and 5")
#         return v

#     model_config = {
#         "json_schema_extra": {
#             "example": {
#                 "supplier_id": "supplier123",
#                 "rated_by": "user456",
#                 "delivery_score": 4,
#                 "quality_score": 5,
#                 "responsiveness_score": 3,
#                 "compliance_score": 4,
#                 "overall_score": 4.00,
#                 "notes": "Generally reliable but slow on one order",
#                 "rating_context": "PO-2025-0009"
#             }
#         },
#         "from_attributes": True
#     }
