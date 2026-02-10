from typing import Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.schemas.cart import CartInDB


class CartsRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._col = db["carts"]

    async def get_by_user_id(self, user_id: ObjectId) -> Optional[CartInDB]:
        doc = await self._col.find_one({"user_id": user_id})
        return CartInDB(**doc) if doc else None

    async def upsert_for_user(self, cart: CartInDB) -> CartInDB:
        payload = cart.model_dump(by_alias=True, exclude_none=True)
        await self._col.update_one(
            {"user_id": cart.user_id},
            {"$set": payload},
            upsert=True,
        )
        doc = await self._col.find_one({"user_id": cart.user_id})
        return CartInDB(**doc)  # type: ignore[arg-type]

    async def clear_items(self, user_id: ObjectId) -> None:
        await self._col.update_one({"user_id": user_id}, {"$set": {"items": []}})



