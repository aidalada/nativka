from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field


class MongoModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )

    id: ObjectId | None = Field(default=None, alias="_id")

