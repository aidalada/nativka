from typing import Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.schemas.favorite import FavoritesInDB


class FavoritesRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._col = db["favorites"]

    async def get_by_user_id(self, user_id: ObjectId) -> Optional[FavoritesInDB]:
        doc = await self._col.find_one({"user_id": user_id})
        return FavoritesInDB(**doc) if doc else None

    async def upsert(self, fav: FavoritesInDB) -> FavoritesInDB:
        payload = fav.model_dump(by_alias=True, exclude_none=True)
        await self._col.update_one(
            {"user_id": fav.user_id},
            {"$set": payload},
            upsert=True,
        )
        doc = await self._col.find_one({"user_id": fav.user_id})
        return FavoritesInDB(**doc)  # type: ignore[arg-type]



