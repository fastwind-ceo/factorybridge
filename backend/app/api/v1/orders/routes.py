from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.order import OrderCreateFromQuote, OrderEventCreate, OrderStatusChange
from app.security.dependencies import get_current_user
from app.services.order_service import (
    add_order_event,
    change_order_status,
    create_order_from_quote,
    get_order_or_404,
    list_my_orders,
    list_order_events,
    require_order_view,
    serialize_order,
    serialize_order_event,
)

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/from-quote/{quote_id}", response_model=APIResponse)
def create_from_quote(
    quote_id: str,
    payload: OrderCreateFromQuote,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = create_order_from_quote(db, current_user, quote_id, payload)
    events = list_order_events(db, current_user, order)
    return APIResponse(data=serialize_order(order, include_timeline=True, events=events))


@router.get("/my", response_model=APIResponse)
def my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    orders = list_my_orders(db, current_user)
    return APIResponse(data={"items": [serialize_order(order) for order in orders]})


@router.get("/{order_id}", response_model=APIResponse)
def get_order(
    order_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = get_order_or_404(db, order_id)
    require_order_view(current_user, order)
    events = list_order_events(db, current_user, order)
    return APIResponse(data=serialize_order(order, include_timeline=True, events=events))


@router.post("/{order_id}/status", response_model=APIResponse)
def set_status(
    order_id: str,
    payload: OrderStatusChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = get_order_or_404(db, order_id)
    order = change_order_status(db, current_user, order, payload.new_status.value, payload.comment)
    events = list_order_events(db, current_user, order)
    return APIResponse(data=serialize_order(order, include_timeline=True, events=events))


@router.post("/{order_id}/events", response_model=APIResponse)
def create_event(
    order_id: str,
    payload: OrderEventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = get_order_or_404(db, order_id)
    event = add_order_event(db, current_user, order, payload)
    return APIResponse(data=serialize_order_event(event))


@router.get("/{order_id}/events", response_model=APIResponse)
def events(
    order_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = get_order_or_404(db, order_id)
    items = list_order_events(db, current_user, order)
    return APIResponse(data={"items": [serialize_order_event(item) for item in items]})
