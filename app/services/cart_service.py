from bson import ObjectId

from app.core.config import settings
from app.repositories.carts_repo import CartsRepository
from app.repositories.dishes_repo import DishesRepository
from app.schemas.cart import CartInDB, CartItem, CartItemCreate, CartItemUpdate, CartResponse
from app.utils.datetime import utcnow
from app.utils.errors import bad_request


class CartService:
    def __init__(self, carts_repo: CartsRepository, dishes_repo: DishesRepository):
        self.carts_repo = carts_repo
        self.dishes_repo = dishes_repo

    async def _get_or_create_cart(self, user_id: ObjectId) -> CartInDB:
        cart = await self.carts_repo.get_by_user_id(user_id)
        if cart:
            return cart
        return CartInDB(user_id=user_id, items=[], promo_code=None, updated_at=utcnow())

    def _calc_totals(self, cart: CartInDB) -> CartResponse:
        subtotal = sum(item.price_snapshot * item.qty for item in cart.items)
        if subtotal >= settings.free_delivery_threshold or subtotal == 0:
            delivery_fee = 0.0
        else:
            delivery_fee = settings.delivery_fee
        total = subtotal + delivery_fee
        return CartResponse(
            items=cart.items,
            subtotal=round(subtotal, 2),
            delivery_fee=round(delivery_fee, 2),
            total=round(total, 2),
        )

    async def get_cart(self, user_id: ObjectId) -> CartResponse:
        cart = await self._get_or_create_cart(user_id)
        return self._calc_totals(cart)

    async def add_item(self, user_id: ObjectId, data: CartItemCreate) -> CartResponse:
        cart = await self._get_or_create_cart(user_id)
        dish = await self.dishes_repo.get_by_id(data.dish_id)
        if not dish:
            raise bad_request("dish_not_found", "Dish not found")

        for item in cart.items:
            if item.dish_id == data.dish_id:
                item.qty += data.qty
                break
        else:
            cart.items.append(
                CartItem(
                    dish_id=data.dish_id,
                    qty=data.qty,
                    price_snapshot=dish.price,
                    title_snapshot=dish.title,
                    image_snapshot=dish.image_url,
                )
            )
        cart.updated_at = utcnow()
        cart = await self.carts_repo.upsert_for_user(cart)
        return self._calc_totals(cart)

    async def update_item(self, user_id: ObjectId, dish_id: str, data: CartItemUpdate) -> CartResponse:
        if data.qty < 1:
            raise bad_request("invalid_qty", "Quantity must be >= 1")
        cart = await self._get_or_create_cart(user_id)
        for item in cart.items:
            if item.dish_id == dish_id:
                item.qty = data.qty
                break
        cart.updated_at = utcnow()
        cart = await self.carts_repo.upsert_for_user(cart)
        return self._calc_totals(cart)

    async def remove_item(self, user_id: ObjectId, dish_id: str) -> CartResponse:
        cart = await self._get_or_create_cart(user_id)
        cart.items = [i for i in cart.items if i.dish_id != dish_id]
        cart.updated_at = utcnow()
        cart = await self.carts_repo.upsert_for_user(cart)
        return self._calc_totals(cart)

    async def clear_cart(self, user_id: ObjectId) -> CartResponse:
        cart = await self._get_or_create_cart(user_id)
        cart.items = []
        cart.updated_at = utcnow()
        cart = await self.carts_repo.upsert_for_user(cart)
        return self._calc_totals(cart)



