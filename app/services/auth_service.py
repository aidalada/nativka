from datetime import datetime

from fastapi import HTTPException, status

from app.core.security import create_access_token, get_password_hash, verify_password
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserCreate, UserInDB, UserPublic
from app.utils.datetime import utcnow
from app.utils.errors import bad_request


class AuthService:
    def __init__(self, users_repo):
        self.users_repo = users_repo

    async def register(self, data: RegisterRequest) -> UserPublic:
        existing = await self.users_repo.get_by_email(data.email)
        if existing:
            raise bad_request("email_taken", "User with this email already exists")

        user_in = UserInDB(
            name=data.name,
            email=data.email,
            password_hash=get_password_hash(data.password),
            created_at=utcnow(),
        )
        user = await self.users_repo.create(user_in)
        return UserPublic(id=str(user.id), name=user.name, email=user.email)

    async def login(self, data: LoginRequest) -> TokenResponse:
        user = await self.users_repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "invalid_credentials", "message": "Incorrect email or password"},
            )
        token = create_access_token(str(user.id))
        return TokenResponse(access_token=token)



