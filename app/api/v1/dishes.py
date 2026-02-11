from fastapi import APIRouter, Depends, Query

from app.core.deps import get_db
from app.repositories.dishes_repo import DishesRepository
from app.schemas.dish import DishCreate, DishPublic
from app.services.dish_service import DishService
from app.utils.errors import not_found
from app.utils.pagination import paginate

router = APIRouter()


@router.get("", response_model=dict)
async def list_dishes(
    q: str | None = Query(default=None),
    category: str | None = Query(default=None),
    sort: str | None = Query(default=None, pattern="^(popular|rating|price_asc|price_desc)$"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db=Depends(get_db),
):
    service = DishService(DishesRepository(db))
    items, total = await service.list_dishes(q=q, category=category, sort=sort, page=page, limit=limit)
    return paginate(items, total, page, limit)


@router.post("", response_model=DishPublic)
async def create_dish(payload: DishCreate, db=Depends(get_db)):
    repo = DishesRepository(db)
    dish_in_db = await repo.create(payload)
    return DishPublic(
        id=str(dish_in_db.id),
        title=dish_in_db.title,
        description=dish_in_db.description,
        price=dish_in_db.price,
        image_url=dish_in_db.image_url,
        category=dish_in_db.category,
        rating=dish_in_db.rating,
        rating_count=dish_in_db.rating_count,
        restaurant_name=dish_in_db.restaurant_name,
    )


@router.get("/{dish_id}", response_model=DishPublic)
async def get_dish(dish_id: str, db=Depends(get_db)):
    service = DishService(DishesRepository(db))
    dish = await service.get_dish(dish_id)
    if not dish:
        raise not_found("dish")
    return dish

