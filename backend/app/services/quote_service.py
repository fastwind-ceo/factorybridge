from datetime import datetime, timezone, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import QuoteStatus, RFQStatus, UserRole
from app.models.quote import Quote
from app.models.rfq import RFQ, TenderInvitation
from app.models.user import User
from app.schemas.quote import QuoteCreate, QuoteUpdate
from app.services.audit_service import log_action
from app.services.auth_service import user_roles
from app.services.notification_service import notify_company, notify_roles
from app.services.rfq_service import get_rfq_or_404, user_company_ids
from app.services.tender_service import ACTIVE_INVITATION_STATUSES, supplier_company_ids


QUOTE_EDITABLE_STATUSES = {QuoteStatus.DRAFT.value, QuoteStatus.CLARIFICATION_NEEDED.value}


def is_operator_or_admin(user: User) -> bool:
    roles = set(user_roles(user))
    return UserRole.ADMIN.value in roles or UserRole.OPERATOR.value in roles


def generate_quote_number(db: Session) -> str:
    year = datetime.now(timezone.utc).year
    total = len(list(db.scalars(select(Quote.id)).all())) + 1
    return f"FB-QT-{year}-{total:06d}"


def get_quote_or_404(db: Session, quote_id: str) -> Quote:
    quote = db.get(Quote, quote_id)
    if not quote:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quote not found")
    return quote


def supplier_can_quote_rfq(db: Session, user: User, rfq_id: str) -> tuple[bool, str | None]:
    company_ids = supplier_company_ids(user)
    if not company_ids:
        return False, None
    invitation = db.scalar(select(TenderInvitation).where(
        TenderInvitation.rfq_id == rfq_id,
        TenderInvitation.supplier_company_id.in_(company_ids),
        TenderInvitation.status.in_(ACTIVE_INVITATION_STATUSES),
    ))
    if not invitation:
        return False, None
    return True, invitation.supplier_company_id


def serialize_quote(quote: Quote, *, customer_safe: bool = False) -> dict:
    data = {
        "id": quote.id,
        "rfq_id": quote.rfq_id,
        "supplier_company_id": quote.supplier_company_id,
        "quote_number": quote.quote_number,
        "status": quote.status,
        "unit_price": float(quote.unit_price),
        "currency": quote.currency,
        "quantity": float(quote.quantity) if quote.quantity is not None else None,
        "moq": float(quote.moq) if quote.moq is not None else None,
        "tooling_cost": float(quote.tooling_cost) if quote.tooling_cost is not None else None,
        "sample_cost": float(quote.sample_cost) if quote.sample_cost is not None else None,
        "packaging_cost": float(quote.packaging_cost) if quote.packaging_cost is not None else None,
        "lead_time_sample_days": int(quote.lead_time_sample_days) if quote.lead_time_sample_days is not None else None,
        "lead_time_mass_days": int(quote.lead_time_mass_days) if quote.lead_time_mass_days is not None else None,
        "payment_terms": quote.payment_terms,
        "incoterms": quote.incoterms,
        "valid_until": quote.valid_until.isoformat() if quote.valid_until else None,
        "estimated_weight_kg": float(quote.estimated_weight_kg) if quote.estimated_weight_kg is not None else None,
        "estimated_volume_cbm": float(quote.estimated_volume_cbm) if quote.estimated_volume_cbm is not None else None,
        "alternative_material": quote.alternative_material,
        "alternative_process": quote.alternative_process,
        "supplier_comments": quote.supplier_comments,
        "risk_score": int(quote.risk_score) if quote.risk_score is not None else None,
        "created_at": quote.created_at.isoformat(),
        "updated_at": quote.updated_at.isoformat(),
        "submitted_at": quote.submitted_at.isoformat() if quote.submitted_at else None,
    }
    if not customer_safe:
        data["submitted_by_user_id"] = quote.submitted_by_user_id
        data["operator_notes"] = quote.operator_notes
    return data


def create_quote(db: Session, user: User, rfq_id: str, payload: QuoteCreate) -> Quote:
    rfq = get_rfq_or_404(db, rfq_id)
    can_quote, supplier_company_id = supplier_can_quote_rfq(db, user, rfq_id)
    if not can_quote or not supplier_company_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Supplier is not invited to this RFQ")
    if rfq.status not in {RFQStatus.PUBLISHED.value, RFQStatus.QUOTING.value, RFQStatus.QUOTES_RECEIVED.value}:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="RFQ is not open for quotations")
    quote = Quote(
        rfq_id=rfq_id,
        supplier_company_id=supplier_company_id,
        submitted_by_user_id=user.id,
        quote_number=generate_quote_number(db),
        unit_price=payload.unit_price,
        currency=payload.currency,
        quantity=payload.quantity,
        moq=payload.moq,
        tooling_cost=payload.tooling_cost,
        sample_cost=payload.sample_cost,
        packaging_cost=payload.packaging_cost,
        lead_time_sample_days=payload.lead_time_sample_days,
        lead_time_mass_days=payload.lead_time_mass_days,
        payment_terms=payload.payment_terms,
        incoterms=payload.incoterms,
        valid_until=payload.valid_until,
        estimated_weight_kg=payload.estimated_weight_kg,
        estimated_volume_cbm=payload.estimated_volume_cbm,
        alternative_material=payload.alternative_material,
        alternative_process=payload.alternative_process,
        supplier_comments=payload.supplier_comments,
    )
    if rfq.status == RFQStatus.PUBLISHED.value:
        rfq.status = RFQStatus.QUOTING.value
    db.add(quote)
    log_action(db, actor_user_id=user.id, action="QUOTE_CREATED", object_type="QUOTE", after_data={"rfq_id": rfq_id})
    db.commit()
    db.refresh(quote)
    return quote


def update_quote(db: Session, user: User, quote: Quote, payload: QuoteUpdate) -> Quote:
    if not is_operator_or_admin(user):
        if quote.supplier_company_id not in supplier_company_ids(user):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Quote access denied")
        if quote.status not in QUOTE_EDITABLE_STATUSES:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Quote is not editable")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(quote, key, value)
    log_action(db, actor_user_id=user.id, action="QUOTE_UPDATED", object_type="QUOTE", object_id=quote.id)
    db.commit()
    db.refresh(quote)
    return quote


def submit_quote(db: Session, user: User, quote: Quote) -> Quote:
    if quote.supplier_company_id not in supplier_company_ids(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Quote access denied")
    if quote.status != QuoteStatus.DRAFT.value:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only draft quote can be submitted")
    quote.status = QuoteStatus.SUBMITTED.value
    quote.submitted_at = datetime.now(timezone.utc)
    rfq = db.get(RFQ, quote.rfq_id)
    if rfq:
        rfq.status = RFQStatus.QUOTES_RECEIVED.value
    invitation = db.scalar(select(TenderInvitation).where(
        TenderInvitation.rfq_id == quote.rfq_id,
        TenderInvitation.supplier_company_id == quote.supplier_company_id,
        TenderInvitation.status.in_(ACTIVE_INVITATION_STATUSES),
    ))
    if invitation:
        invitation.status = "QUOTE_SUBMITTED"
    log_action(db, actor_user_id=user.id, action="QUOTE_SUBMITTED", object_type="QUOTE", object_id=quote.id)
    if rfq:
        notify_company(db, company_id=rfq.customer_company_id, title="New supplier quote", message=f"New quote received for {rfq.rfq_number}", notification_type="QUOTE_SUBMITTED", object_type="QUOTE", object_id=quote.id)
    notify_roles(db, roles=[UserRole.ADMIN.value, UserRole.OPERATOR.value], title="New quote submitted", message=f"Quote {quote.quote_number} submitted", notification_type="QUOTE_SUBMITTED", object_type="QUOTE", object_id=quote.id)
    db.commit()
    db.refresh(quote)
    return quote


def can_user_view_quote(db: Session, user: User, quote: Quote) -> bool:
    if is_operator_or_admin(user):
        return True
    if quote.supplier_company_id in supplier_company_ids(user):
        return True
    rfq = db.get(RFQ, quote.rfq_id)
    return bool(rfq and rfq.customer_company_id in user_company_ids(user))


def list_quotes_for_rfq(db: Session, user: User, rfq_id: str) -> list[Quote]:
    rfq = get_rfq_or_404(db, rfq_id)
    if is_operator_or_admin(user):
        pass
    elif rfq.customer_company_id in user_company_ids(user):
        pass
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="RFQ access denied")
    return list(db.scalars(select(Quote).where(Quote.rfq_id == rfq_id).order_by(Quote.created_at.desc())).all())


def list_my_supplier_quotes(db: Session, user: User) -> list[Quote]:
    company_ids = supplier_company_ids(user)
    if not company_ids:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not linked to supplier company")
    return list(db.scalars(select(Quote).where(Quote.supplier_company_id.in_(company_ids)).order_by(Quote.created_at.desc())).all())


def accept_quote(db: Session, user: User, quote: Quote) -> Quote:
    rfq = db.get(RFQ, quote.rfq_id)
    if not rfq:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="RFQ not found")
    if not is_operator_or_admin(user) and rfq.customer_company_id not in user_company_ids(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Quote accept access denied")
    quote.status = QuoteStatus.ACCEPTED.value
    rfq.status = RFQStatus.SUPPLIER_SELECTED.value
    # Reject other submitted quotes to keep one clear selected option.
    for other in db.scalars(select(Quote).where(Quote.rfq_id == rfq.id, Quote.id != quote.id)).all():
        if other.status in {QuoteStatus.SUBMITTED.value, QuoteStatus.UNDER_REVIEW.value}:
            other.status = QuoteStatus.REJECTED.value
    log_action(db, actor_user_id=user.id, action="QUOTE_ACCEPTED", object_type="QUOTE", object_id=quote.id)
    notify_company(db, company_id=quote.supplier_company_id, title="Quote accepted", message=f"Your quote {quote.quote_number} was accepted", notification_type="QUOTE_ACCEPTED", object_type="QUOTE", object_id=quote.id)
    notify_roles(db, roles=[UserRole.ADMIN.value, UserRole.OPERATOR.value], title="Quote accepted", message=f"Quote {quote.quote_number} accepted for RFQ {rfq.rfq_number}", notification_type="QUOTE_ACCEPTED", object_type="QUOTE", object_id=quote.id)
    db.commit()
    db.refresh(quote)
    return quote


def reject_quote(db: Session, user: User, quote: Quote) -> Quote:
    if not is_operator_or_admin(user):
        rfq = db.get(RFQ, quote.rfq_id)
        if not rfq or rfq.customer_company_id not in user_company_ids(user):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Quote reject access denied")
    quote.status = QuoteStatus.REJECTED.value
    log_action(db, actor_user_id=user.id, action="QUOTE_REJECTED", object_type="QUOTE", object_id=quote.id)
    db.commit()
    db.refresh(quote)
    return quote


def build_customer_safe_comparison(quotes: list[Quote]) -> dict:
    submitted = [q for q in quotes if q.status in {QuoteStatus.SUBMITTED.value, QuoteStatus.ACCEPTED.value, QuoteStatus.REJECTED.value}]
    items = [serialize_quote(q, customer_safe=True) for q in submitted]
    best_price = min(submitted, key=lambda q: float(q.unit_price), default=None)
    best_delivery = min(submitted, key=lambda q: int(q.lead_time_mass_days or 999999), default=None)
    return {
        "items": items,
        "summary": {
            "quote_count": len(items),
            "best_price_quote_id": best_price.id if best_price else None,
            "best_delivery_quote_id": best_delivery.id if best_delivery else None,
        },
    }
