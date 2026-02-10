from typing import Annotated

from bson import ObjectId
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.security import decode_access_token
from app.db.mongodb import get_database
from app.repositories.users_repo import UsersRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


async def get_db() -> AsyncIOMotorDatabase:
    return get_database()


def get_users_repo(db: Annotated[AsyncIOMotorDatabase, Depends(get_db)]) -> UsersRepository:
    return UsersRepository(db)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    users_repo: Annotated[UsersRepository, Depends(get_users_repo)],
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"code": "unauthorized", "message": "Could not validate credentials"},
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id: str | None = payload.get("sub")  # type: ignore[assignment]
        if user_id is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception

    if not ObjectId.is_valid(user_id):
        raise credentials_exception

    user = await users_repo.get_by_id(ObjectId(user_id))
    if user is None:
        raise credentials_exception
    return user

