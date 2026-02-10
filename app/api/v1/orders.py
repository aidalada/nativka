from bson import ObjectId
from fastapi import APIRouter, Depends

from app.core.deps import get_current_user, get_db
from app.repositories.carts_repo import CartsRepository
from app.repositories.orders_repo import OrdersRepository
from app.schemas.order import (
    CheckoutRequest,
    OrderCreatedResponse,
    OrderDetail,
    OrderPreview,
    TrackingResponse,
)
from app.services.order_service import OrderService
from app.services.tracking_service import TrackingService
from app.utils.errors import not_found

router = APIRouter()


def _order_service(db) -> OrderService:
    return OrderService(CartsRepository(db), OrdersRepository(db))


def _tracking_service(db) -> TrackingService:
    return TrackingService(OrdersRepository(db))


@router.post("", response_model=OrderCreatedResponse)
async def create_order(
    payload: CheckoutRequest,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = _order_service(db)
    return await service.checkout(ObjectId(current_user.id), payload)


@router.get("", response_model=dict)
async def list_orders(db=Depends(get_db), current_user=Depends(get_current_user)):
    service = _order_service(db)
    items = await service.list_orders(ObjectId(current_user.id))
    return {"items": items}


@router.get("/{order_id}", response_model=OrderDetail)
async def get_order(
    order_id: str,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = _order_service(db)
    order = await service.get_order(ObjectId(current_user.id), order_id)
    if not order:
        raise not_found("order")
    return order


@router.patch("/{order_id}/cancel", response_model=OrderCreatedResponse)
async def cancel_order(
    order_id: str,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = _order_service(db)
    return await service.cancel_order(ObjectId(current_user.id), order_id)


@router.get("/{order_id}/tracking", response_model=TrackingResponse)
async def tracking_order(
    order_id: str,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = _tracking_service(db)
    tracking = await service.get_tracking(ObjectId(current_user.id), order_id)
    if not tracking:
        raise not_found("order")
    return tracking

