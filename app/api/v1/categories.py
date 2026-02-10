from fastapi import APIRouter, Depends

from app.core.deps import get_db
from app.repositories.dishes_repo import DishesRepository

router = APIRouter()


@router.get("", response_model=dict)
async def get_categories(db=Depends(get_db)):
    repo = DishesRepository(db)
    items = await repo.distinct_categories()
    return {"items": items}

