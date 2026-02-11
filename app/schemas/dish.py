from bson import ObjectId
from pydantic import BaseModel, Field

from app.schemas.common import MongoModel


class DishInDB(MongoModel):
    id: ObjectId | None = Field(default=None, alias="_id")
    title: str
    description: str
    price: float
    image_url: str
    category: str
    rating: float = 0.0
    rating_count: int = 0
    restaurant_name: str


class DishCreate(BaseModel):
    title: str
    description: str
    price: float
    image_url: str
    category: str
    restaurant_name: str
    rating: float | None = None
    rating_count: int | None = None


class DishPublic(BaseModel):
    id: str
    title: str
    description: str
    price: float
    image_url: str
    category: str
    rating: float
    rating_count: int
    restaurant_name: str

