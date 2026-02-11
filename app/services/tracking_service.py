from datetime import timedelta

from bson import ObjectId

from app.core.config import settings
from app.repositories.orders_repo import OrdersRepository
from app.schemas.order import TrackingResponse
from app.utils.datetime import utcnow


class TrackingService:
    def __init__(self, orders_repo: OrdersRepository):
        self.orders_repo = orders_repo

    async def get_tracking(self, user_id: ObjectId, order_id: str) -> TrackingResponse | None:
        order = await self.orders_repo.get_by_id_for_user(order_id, user_id)
        if not order:
            return None

        if order.status == "canceled":
            return TrackingResponse(
                order_id=str(order.id),
                status="canceled",
                progress=0.0,
                eta_remaining_seconds=0,
                steps=[],
            )

        now = utcnow()
        elapsed = (now - order.tracking_started_at).total_seconds()
        eta = order.eta_seconds
        remaining = max(int(eta - elapsed), 0)
        progress = min(max(elapsed / eta, 0.0), 1.0) if eta > 0 else 1.0

        status = order.status
        if elapsed >= eta:
            status = "delivered"
        elif elapsed < 15:
            status = "preparing"
        elif elapsed < 50:
            status = "on_way"
        elif elapsed < eta:
            status = "arriving"

        steps = [
            {"name": "ordered", "completed": True},
            {"name": "preparing", "completed": elapsed >= 15},
            {"name": "on_way", "completed": elapsed >= 50},
            {"name": "arriving", "completed": elapsed >= eta},
            {"name": "delivered", "completed": elapsed >= eta},
        ]

        return TrackingResponse(
            order_id=str(order.id),
            status=status,
            progress=progress,
            eta_remaining_seconds=remaining,
            steps=steps,
        )




