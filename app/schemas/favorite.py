from datetime import datetime
from typing import List

from bson import ObjectId
from pydantic import BaseModel, Field

from app.schemas.common import MongoModel


class FavoritesInDB(MongoModel):
    id: ObjectId | None = Field(default=None, alias="_id")
    user_id: ObjectId
    dish_ids: List[str] = Field(default_factory=list)
    updated_at: datetime


class FavoritesResponse(BaseModel):
    dish_ids: List[str]

