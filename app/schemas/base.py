from pydantic import BaseModel, Field, ConfigDict
from beanie import PydanticObjectId
from bson import ObjectId

class BaseResponse(BaseModel):
    # accept ObjectId on input, but expose it under `id`
    id: PydanticObjectId = Field(alias="_id")

    model_config = ConfigDict(
        from_attributes=True,      # allows Brand → BrandResponse
        populate_by_name=True,     # id OR _id both work
        json_encoders={            # turn it into a string in JSON
            ObjectId: str,
            PydanticObjectId: str,
        },
    )
