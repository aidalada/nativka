from bson import ObjectId
from fastapi import APIRouter, Depends

from app.core.deps import get_current_user, get_db
from app.repositories.favorites_repo import FavoritesRepository
from app.schemas.favorite import FavoritesResponse
from app.services.favorite_service import FavoriteService

router = APIRouter()


def _service(db) -> FavoriteService:
    return FavoriteService(FavoritesRepository(db))


@router.get("", response_model=FavoritesResponse)
async def get_favorites(db=Depends(get_db), current_user=Depends(get_current_user)):
    service = _service(db)
    return await service.get_favorites(ObjectId(current_user.id))


@router.post("/{dish_id}", response_model=FavoritesResponse)
async def toggle_favorite(
    dish_id: str,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = _service(db)
    return await service.toggle_favorite(ObjectId(current_user.id), dish_id)


@router.delete("/{dish_id}", response_model=FavoritesResponse)
async def remove_favorite(
    dish_id: str,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = _service(db)
    return await service.remove_favorite(ObjectId(current_user.id), dish_id)

