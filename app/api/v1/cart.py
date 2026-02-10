from bson import ObjectId
from fastapi import APIRouter, Depends

from app.core.deps import get_current_user, get_db
from app.repositories.carts_repo import CartsRepository
from app.repositories.dishes_repo import DishesRepository
from app.schemas.cart import CartItemCreate, CartItemUpdate, CartResponse
from app.services.cart_service import CartService

router = APIRouter()


def _service(db) -> CartService:
    return CartService(CartsRepository(db), DishesRepository(db))


@router.get("", response_model=CartResponse)
async def get_cart(db=Depends(get_db), current_user=Depends(get_current_user)):
    service = _service(db)
    return await service.get_cart(ObjectId(current_user.id))


@router.post("/items", response_model=CartResponse)
async def add_item(
    payload: CartItemCreate,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = _service(db)
    return await service.add_item(ObjectId(current_user.id), payload)


@router.put("/items/{dish_id}", response_model=CartResponse)
async def update_item(
    dish_id: str,
    payload: CartItemUpdate,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = _service(db)
    return await service.update_item(ObjectId(current_user.id), dish_id, payload)


@router.delete("/items/{dish_id}", response_model=CartResponse)
async def remove_item(
    dish_id: str,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = _service(db)
    return await service.remove_item(ObjectId(current_user.id), dish_id)


@router.delete("", response_model=CartResponse)
async def clear_cart(db=Depends(get_db), current_user=Depends(get_current_user)):
    service = _service(db)
    return await service.clear_cart(ObjectId(current_user.id))

