from typing import Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.schemas.user import UserInDB


class UsersRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self._col = db["users"]

    async def get_by_email(self, email: str) -> Optional[UserInDB]:
        doc = await self._col.find_one({"email": email})
        return UserInDB(**doc) if doc else None

    async def get_by_id(self, user_id: ObjectId) -> Optional[UserInDB]:
        doc = await self._col.find_one({"_id": user_id})
        return UserInDB(**doc) if doc else None

    async def create(self, user: UserInDB) -> UserInDB:
        payload = user.model_dump(by_alias=True, exclude_none=True)
        result = await self._col.insert_one(payload)
        user.id = result.inserted_id
        return user




