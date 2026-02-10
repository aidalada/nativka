from bson import ObjectId

from app.repositories.favorites_repo import FavoritesRepository
from app.schemas.favorite import FavoritesInDB, FavoritesResponse
from app.utils.datetime import utcnow


class FavoriteService:
    def __init__(self, favorites_repo: FavoritesRepository):
        self.favorites_repo = favorites_repo

    async def get_favorites(self, user_id: ObjectId) -> FavoritesResponse:
        fav = await self.favorites_repo.get_by_user_id(user_id)
        if not fav:
            return FavoritesResponse(dish_ids=[])
        return FavoritesResponse(dish_ids=fav.dish_ids)

    async def toggle_favorite(self, user_id: ObjectId, dish_id: str) -> FavoritesResponse:
        fav = await self.favorites_repo.get_by_user_id(user_id)
        if not fav:
            fav = FavoritesInDB(user_id=user_id, dish_ids=[dish_id], updated_at=utcnow())
        else:
            if dish_id in fav.dish_ids:
                fav.dish_ids.remove(dish_id)
            else:
                fav.dish_ids.append(dish_id)
            fav.updated_at = utcnow()
        fav = await self.favorites_repo.upsert(fav)
        return FavoritesResponse(dish_ids=fav.dish_ids)

    async def remove_favorite(self, user_id: ObjectId, dish_id: str) -> FavoritesResponse:
        fav = await self.favorites_repo.get_by_user_id(user_id)
        if not fav:
            return FavoritesResponse(dish_ids=[])
        fav.dish_ids = [d for d in fav.dish_ids if d != dish_id]
        fav.updated_at = utcnow()
        fav = await self.favorites_repo.upsert(fav)
        return FavoritesResponse(dish_ids=fav.dish_ids)



