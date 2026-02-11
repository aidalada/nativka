from typing import Optional

from app.repositories.dishes_repo import DishesRepository
from app.schemas.dish import DishInDB, DishPublic


class DishService:
    def __init__(self, dishes_repo: DishesRepository):
        self.dishes_repo = dishes_repo

    async def get_dish(self, dish_id: str) -> Optional[DishPublic]:
        dish = await self.dishes_repo.get_by_id(dish_id)
        if not dish:
            return None
        return DishPublic(
            id=str(dish.id),
            title=dish.title,
            description=dish.description,
            price=dish.price,
            image_url=dish.image_url,
            category=dish.category,
            rating=dish.rating,
            rating_count=dish.rating_count,
            restaurant_name=dish.restaurant_name,
        )

    async def list_dishes(
        self,
        *,
        q: Optional[str],
        category: Optional[str],
        sort: Optional[str],
        page: int,
        limit: int,
    ):
        skip = (page - 1) * limit
        dishes, total = await self.dishes_repo.list(q=q, category=category, sort=sort, skip=skip, limit=limit)
        items = [
            DishPublic(
                id=str(d.id),
                title=d.title,
                description=d.description,
                price=d.price,
                image_url=d.image_url,
                category=d.category,
                rating=d.rating,
                rating_count=d.rating_count,
                restaurant_name=d.restaurant_name,
            )
            for d in dishes
        ]
        return items, total




