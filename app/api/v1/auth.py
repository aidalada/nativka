from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.core.deps import get_current_user, get_users_repo
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserPublic
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=UserPublic)
async def register(
    payload: RegisterRequest,
    users_repo=Depends(get_users_repo),
):
    service = AuthService(users_repo)
    return await service.register(payload)


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    users_repo=Depends(get_users_repo),
):
    service = AuthService(users_repo)
    return await service.login(payload)


@router.post("/token", response_model=TokenResponse)
async def login_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    users_repo=Depends(get_users_repo),
):
    service = AuthService(users_repo)
    payload = LoginRequest(email=form_data.username, password=form_data.password)
    return await service.login(payload)


@router.get("/me", response_model=UserPublic)
async def me(current_user=Depends(get_current_user)):
    return UserPublic(id=str(current_user.id), name=current_user.name, email=current_user.email)

