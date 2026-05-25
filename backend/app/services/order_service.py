from datetime import datetime, timezone, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import OrderStatus, QuoteStatus, RFQStatus, UserRole
from app.models.landed_cost import LandedCost
from app.models.order import Order, OrderEvent
from app.models.quote import Quote
from app.models.rfq import RFQ
from app.models.user import User
from app.schemas.order import OrderCreateFromQuote, OrderEventCreate
from app.services.audit_service import log_action
from app.services.auth_service import user_roles
from app.services.notification_service import notify_company, notify_roles
from app.services.quote_service import get_quote_or_404, supplier_company_ids
from app.services.rfq_service import user_company_ids


def is_operator_or_admin(user: User) -> bool:
    roles = set(user_roles(user))
    return UserRole.ADMIN.value in roles or UserRole.OPERATOR.value in roles


def generate_order_number(db: Session) -> str:
    year = datetime.now(timezone.utc).year
    total = len(list(db.scalars(select(Order.id)).all())) + 1
    return f"FB-ORD-{year}-{total:06d}"


def get_order_or_404(db: Session, order_id: str) -> Order:
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


def can_view_order(user: User, order: Order) -> bool:
    if is_operator_or_admin(user):
        return True
    company_ids = set(user_company_ids(user))
    return order.customer_company_id in company_ids or order.supplier_company_id in company_ids


def require_order_view(user: User, order: Order) -> None:
    if not can_view_order(user, order):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Order access denied")


def create_order_from_quote(db: Session, user: User, quote_id: str, payload: OrderCreateFromQuote) -> Order:
    if not is_operator_or_admin(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only operator/admin can create orders")
    quote = get_quote_or_404(db, quote_id)
    if quote.status != QuoteStatus.ACCEPTED.value:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only accepted quote can be converted to order")
    rfq = db.get(RFQ, quote.rfq_id)
    if not rfq:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="RFQ not found")
    existing = db.scalar(select(Order).where(Order.quote_id == quote.id))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Order already exists for this quote")
    landed_cost = None
    if payload.landed_cost_id:
        landed_cost = db.get(LandedCost, payload.landed_cost_id)
        if not landed_cost or landed_cost.quote_id != quote.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid landed cost for quote")
    total_amount = None
    currency = quote.currency
    if landed_cost:
        total_amount = landed_cost.final_customer_total_price
        currency = landed_cost.currency
    elif quote.quantity is not None:
        total_amount = float(quote.unit_price) * float(quote.quantity)
    order = Order(
        order_number=generate_order_number(db),
        rfq_id=rfq.id,
        quote_id=quote.id,
        customer_company_id=rfq.customer_company_id,
        supplier_company_id=quote.supplier_company_id,
        landed_cost_id=landed_cost.id if landed_cost else None,
        status=OrderStatus.CREATED.value,
        total_amount=total_amount,
        currency=currency,
        payment_terms=payload.payment_terms or quote.payment_terms,
        production_start_date=payload.production_start_date,
        planned_ready_date=payload.planned_ready_date,
        planned_delivery_date=payload.planned_delivery_date,
        operator_user_id=user.id,
        notes=payload.notes,
    )
    db.add(order)
    db.flush()
    db.add(OrderEvent(
        order_id=order.id,
        event_type="ORDER_CREATED",
        title="Order created from accepted quote",
        description=f"Created from quote {quote.quote_number}",
        created_by_user_id=user.id,
    ))
    rfq.status = RFQStatus.ORDER_CREATED.value
    log_action(db, actor_user_id=user.id, action="ORDER_CREATED", object_type="ORDER", object_id=order.id, after_data={"quote_id": quote_id})
    notify_company(db, company_id=order.customer_company_id, title="Order created", message=f"Order {order.order_number} was created", notification_type="ORDER_CREATED", object_type="ORDER", object_id=order.id)
    notify_company(db, company_id=order.supplier_company_id, title="Order created", message=f"Order {order.order_number} was created from accepted quote", notification_type="ORDER_CREATED", object_type="ORDER", object_id=order.id)
    notify_roles(db, roles=[UserRole.ADMIN.value, UserRole.OPERATOR.value], title="Order created", message=f"Order {order.order_number} was created", notification_type="ORDER_CREATED", object_type="ORDER", object_id=order.id)
    db.commit()
    db.refresh(order)
    return order


def change_order_status(db: Session, user: User, order: Order, new_status: str, comment: str | None = None) -> Order:
    if not is_operator_or_admin(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only operator/admin can change order status")
    old_status = order.status
    order.status = new_status
    event_title = f"Order status changed: {old_status} → {new_status}"
    db.add(OrderEvent(
        order_id=order.id,
        event_type="STATUS_CHANGED",
        title=event_title,
        description=comment,
        created_by_user_id=user.id,
    ))
    log_action(db, actor_user_id=user.id, action="ORDER_STATUS_CHANGED", object_type="ORDER", object_id=order.id, before_data={"status": old_status}, after_data={"status": new_status})
    notify_company(db, company_id=order.customer_company_id, title="Order status updated", message=f"Order {order.order_number} status changed to {new_status}", notification_type="ORDER_STATUS_CHANGED", object_type="ORDER", object_id=order.id)
    notify_company(db, company_id=order.supplier_company_id, title="Order status updated", message=f"Order {order.order_number} status changed to {new_status}", notification_type="ORDER_STATUS_CHANGED", object_type="ORDER", object_id=order.id)
    db.commit()
    db.refresh(order)
    return order


def add_order_event(db: Session, user: User, order: Order, payload: OrderEventCreate) -> OrderEvent:
    if not is_operator_or_admin(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only operator/admin can add order events")
    event = OrderEvent(
        order_id=order.id,
        event_type=payload.event_type,
        title=payload.title,
        description=payload.description,
        created_by_user_id=user.id,
    )
    db.add(event)
    log_action(db, actor_user_id=user.id, action="ORDER_EVENT_ADDED", object_type="ORDER", object_id=order.id, after_data={"event_type": payload.event_type})
    db.commit()
    db.refresh(event)
    return event


def list_order_events(db: Session, user: User, order: Order) -> list[OrderEvent]:
    require_order_view(user, order)
    return list(db.scalars(select(OrderEvent).where(OrderEvent.order_id == order.id).order_by(OrderEvent.created_at.asc())).all())


def list_my_orders(db: Session, user: User) -> list[Order]:
    if is_operator_or_admin(user):
        return list(db.scalars(select(Order).order_by(Order.created_at.desc())).all())
    company_ids = user_company_ids(user)
    if not company_ids:
        return []
    return list(db.scalars(select(Order).where(
        (Order.customer_company_id.in_(company_ids)) | (Order.supplier_company_id.in_(company_ids))
    ).order_by(Order.created_at.desc())).all())


def serialize_order_event(event: OrderEvent) -> dict:
    return {
        "id": event.id,
        "order_id": event.order_id,
        "event_type": event.event_type,
        "title": event.title,
        "description": event.description,
        "created_by_user_id": event.created_by_user_id,
        "created_at": event.created_at.isoformat(),
    }


def serialize_order(order: Order, *, include_timeline: bool = False, events: list[OrderEvent] | None = None) -> dict:
    data = {
        "id": order.id,
        "order_number": order.order_number,
        "rfq_id": order.rfq_id,
        "quote_id": order.quote_id,
        "landed_cost_id": order.landed_cost_id,
        "customer_company_id": order.customer_company_id,
        "supplier_company_id": order.supplier_company_id,
        "status": order.status,
        "total_amount": float(order.total_amount) if order.total_amount is not None else None,
        "currency": order.currency,
        "payment_terms": order.payment_terms,
        "production_start_date": order.production_start_date.isoformat() if order.production_start_date else None,
        "planned_ready_date": order.planned_ready_date.isoformat() if order.planned_ready_date else None,
        "planned_delivery_date": order.planned_delivery_date.isoformat() if order.planned_delivery_date else None,
        "actual_delivery_date": order.actual_delivery_date.isoformat() if order.actual_delivery_date else None,
        "operator_user_id": order.operator_user_id,
        "notes": order.notes,
        "created_at": order.created_at.isoformat(),
        "updated_at": order.updated_at.isoformat(),
    }
    if include_timeline:
        data["timeline"] = [serialize_order_event(event) for event in (events or [])]
    return data
