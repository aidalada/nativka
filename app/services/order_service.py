from bson import ObjectId

from app.core.config import settings
from app.repositories.carts_repo import CartsRepository
from app.repositories.orders_repo import OrdersRepository
from app.schemas.order import CheckoutRequest, OrderCreatedResponse, OrderDetail, OrderInDB, OrderPreview
from app.utils.datetime import utcnow
from app.utils.errors import bad_request, conflict


class OrderService:
    def __init__(self, carts_repo: CartsRepository, orders_repo: OrdersRepository):
        self.carts_repo = carts_repo
        self.orders_repo = orders_repo

    async def checkout(self, user_id: ObjectId, data: CheckoutRequest) -> OrderCreatedResponse:
        cart = await self.carts_repo.get_by_user_id(user_id)
        if not cart or not cart.items:
            raise bad_request("empty_cart", "Cart is empty")

        # totals
        subtotal = sum(item.price_snapshot * item.qty for item in cart.items)
        delivery_fee = 0.0 if subtotal >= settings.free_delivery_threshold else settings.delivery_fee
        total = subtotal + delivery_fee

        now = utcnow()
        order = OrderInDB(
            user_id=user_id,
            items=cart.items,
            subtotal=round(subtotal, 2),
            delivery_fee=round(delivery_fee, 2),
            total=round(total, 2),
            address=data.address,
            delivery_time=data.delivery_time,
            leave_at_door=data.leave_at_door,
            courier_note=data.courier_note,
            payment_method=data.payment_method,
            status="ordered",
            created_at=now,
            updated_at=now,
            tracking_started_at=now,
            eta_seconds=settings.tracking_eta_seconds,
        )
        order = await self.orders_repo.create(order)
        await self.carts_repo.clear_items(user_id)

        return OrderCreatedResponse(
            id=str(order.id),
            status=order.status,
            created_at=order.created_at,
            total=order.total,
            eta_seconds=order.eta_seconds,
        )

    async def list_orders(self, user_id: ObjectId) -> list[OrderPreview]:
        orders = await self.orders_repo.list_for_user(user_id)
        previews: list[OrderPreview] = []
        for o in orders:
            items_count = sum(i.qty for i in o.items)
            restaurant_name_preview = o.items[0].title_snapshot if o.items else None
            previews.append(
                OrderPreview(
                    id=str(o.id),
                    status=o.status,
                    created_at=o.created_at,
                    total=o.total,
                    items_count=items_count,
                    restaurant_name_preview=restaurant_name_preview,
                )
            )
        return previews

    async def get_order(self, user_id: ObjectId, order_id: str) -> OrderDetail | None:
        order = await self.orders_repo.get_by_id_for_user(order_id, user_id)
        if not order:
            return None
        return OrderDetail(
            id=str(order.id),
            user_id=str(order.user_id),
            items=order.items,
            subtotal=order.subtotal,
            delivery_fee=order.delivery_fee,
            total=order.total,
            address=order.address,
            delivery_time=order.delivery_time,
            leave_at_door=order.leave_at_door,
            courier_note=order.courier_note,
            payment_method=order.payment_method,
            status=order.status,
            created_at=order.created_at,
            updated_at=order.updated_at,
            tracking_started_at=order.tracking_started_at,
            eta_seconds=order.eta_seconds,
        )

    async def cancel_order(self, user_id: ObjectId, order_id: str) -> OrderCreatedResponse:
        order = await self.orders_repo.get_by_id_for_user(order_id, user_id)
        if not order:
            from fastapi import HTTPException, status

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "order_not_found", "message": "Order not found"},
            )
        if order.status == "delivered":
            raise conflict("cannot_cancel", "Order already delivered")

        await self.orders_repo.update_status(ObjectId(order.id), "canceled")  # type: ignore[arg-type]
        order.status = "canceled"
        return OrderCreatedResponse(
            id=str(order.id),
            status=order.status,
            created_at=order.created_at,
            total=order.total,
            eta_seconds=order.eta_seconds,
        )




