from typing import List, Optional, Tuple

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.schemas.order import OrderInDB


class OrdersRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._col = db["orders"]

    async def create(self, order: OrderInDB) -> OrderInDB:
        payload = order.model_dump(by_alias=True, exclude_none=True)
        result = await self._col.insert_one(payload)
        order.id = result.inserted_id
        return order

    async def get_by_id_for_user(self, order_id: str, user_id: ObjectId) -> Optional[OrderInDB]:
        if not ObjectId.is_valid(order_id):
            return None
        doc = await self._col.find_one({"_id": ObjectId(order_id), "user_id": user_id})
        return OrderInDB(**doc) if doc else None

    async def list_for_user(self, user_id: ObjectId) -> List[OrderInDB]:
        cursor = self._col.find({"user_id": user_id}).sort("created_at", -1)
        docs = await cursor.to_list(length=100)
        return [OrderInDB(**d) for d in docs]

    async def update_status(self, order_id: ObjectId, status: str) -> None:
        await self._col.update_one({"_id": order_id}, {"$set": {"status": status}})




