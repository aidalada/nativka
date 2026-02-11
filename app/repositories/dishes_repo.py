from typing import Any, Dict, List, Optional, Tuple

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.schemas.dish import DishCreate, DishInDB


class DishesRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._col = db["dishes"]

    async def get_by_id(self, dish_id: str) -> Optional[DishInDB]:
        if not ObjectId.is_valid(dish_id):
            return None
        doc = await self._col.find_one({"_id": ObjectId(dish_id)})
        return DishInDB(**doc) if doc else None

    async def list(
        self,
        *,
        q: Optional[str],
        category: Optional[str],
        sort: Optional[str],
        skip: int,
        limit: int,
    ) -> Tuple[List[DishInDB], int]:
        query: Dict[str, Any] = {}
        if q:
            query["title"] = {"$regex": q, "$options": "i"}
        if category:
            query["category"] = category

        sort_spec: list[tuple[str, int]] = []
        if sort == "popular":
            sort_spec = [("rating_count", -1)]
        elif sort == "rating":
            sort_spec = [("rating", -1)]
        elif sort == "price_asc":
            sort_spec = [("price", 1)]
        elif sort == "price_desc":
            sort_spec = [("price", -1)]

        cursor = self._col.find(query)
        if sort_spec:
            cursor = cursor.sort(sort_spec)
        total = await self._col.count_documents(query)
        docs = await cursor.skip(skip).limit(limit).to_list(length=limit)
        return [DishInDB(**d) for d in docs], total

    async def create(self, data: DishCreate) -> DishInDB:
        payload: Dict[str, Any] = data.model_dump(exclude_unset=True)
        # значения по умолчанию
        payload.setdefault("rating", 0.0)
        payload.setdefault("rating_count", 0)
        result = await self._col.insert_one(payload)
        payload["_id"] = result.inserted_id
        return DishInDB(**payload)

    async def distinct_categories(self) -> List[str]:
        return await self._col.distinct("category")




