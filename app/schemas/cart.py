from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from pydantic import BaseModel, Field

from app.schemas.common import MongoModel


class CartItem(BaseModel):
    dish_id: str
    qty: int = 1
    price_snapshot: float
    title_snapshot: str
    image_snapshot: str


class CartInDB(MongoModel):
    id: ObjectId | None = Field(default=None, alias="_id")
    user_id: ObjectId
    items: List[CartItem] = Field(default_factory=list)
    promo_code: Optional[str] = None
    updated_at: datetime


class CartTotals(BaseModel):
    subtotal: float
    delivery_fee: float
    total: float


class CartResponse(BaseModel):
    items: List[CartItem]
    subtotal: float
    delivery_fee: float
    total: float


class CartItemCreate(BaseModel):
    dish_id: str
    qty: int = 1


class CartItemUpdate(BaseModel):
    qty: int

