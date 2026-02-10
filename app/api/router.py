from fastapi import APIRouter

from app.api.v1 import auth, dishes, cart, orders, favorites, categories

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(dishes.router, prefix="/dishes", tags=["dishes"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(favorites.router, prefix="/favorites", tags=["favorites"])
api_router.include_router(cart.router, prefix="/cart", tags=["cart"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])



