from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import MongoModel


class UserInDB(MongoModel):
    id: ObjectId | None = Field(default=None, alias="_id")
    name: str
    email: EmailStr
    password_hash: str
    created_at: datetime


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class UserPublic(BaseModel):
    id: str
    name: str
    email: EmailStr

