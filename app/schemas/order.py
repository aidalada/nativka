from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from pydantic import BaseModel, Field

from app.schemas.cart import CartItem
from app.schemas.common import MongoModel


class OrderInDB(MongoModel):
    id: ObjectId | None = Field(default=None, alias="_id")
    user_id: ObjectId
    items: List[CartItem]
    subtotal: float
    delivery_fee: float
    total: float
    address: str
    delivery_time: str
    leave_at_door: bool
    courier_note: Optional[str] = None
    payment_method: str
    status: str
    created_at: datetime
    updated_at: datetime
    tracking_started_at: datetime
    eta_seconds: int = 60


class CheckoutRequest(BaseModel):
    address: str
    delivery_time: str
    leave_at_door: bool = False
    courier_note: Optional[str] = None
    payment_method: str
    promo_code: Optional[str] = None


class OrderPreview(BaseModel):
    id: str
    status: str
    created_at: datetime
    total: float
    items_count: int
    restaurant_name_preview: Optional[str] = None


class OrderDetail(BaseModel):
    id: str
    user_id: str
    items: List[CartItem]
    subtotal: float
    delivery_fee: float
    total: float
    address: str
    delivery_time: str
    leave_at_door: bool
    courier_note: Optional[str]
    payment_method: str
    status: str
    created_at: datetime
    updated_at: datetime
    tracking_started_at: datetime
    eta_seconds: int


class OrderCreatedResponse(BaseModel):
    id: str
    status: str
    created_at: datetime
    total: float
    eta_seconds: int


class TrackingResponse(BaseModel):
    order_id: str
    status: str
    progress: float
    eta_remaining_seconds: int
    steps: list[dict]

