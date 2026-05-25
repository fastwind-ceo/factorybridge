from datetime import datetime, timezone, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.company import Company
from app.models.enums import CompanyType, RFQStatus, UserRole
from app.models.rfq import RFQ, RFQCommercialSpec, RFQLogisticsSpec, RFQStatusHistory, RFQTechnicalSpec, TenderInvitation
from app.models.user import User
from app.schemas.rfq import RFQCommercialSpecUpsert, RFQCreate, RFQLogisticsSpecUpsert, RFQTechnicalSpecUpsert, RFQUpdate
from app.services.audit_service import log_action
from app.services.auth_service import user_roles
from app.services.notification_service import notify_company, notify_roles

ACTIVE_SUPPLIER_INVITATION_STATUSES = {"INVITED", "VIEWED", "ACCEPTED", "QUOTE_SUBMITTED"}


def is_operator_or_admin(user: User) -> bool:
    roles = set(user_roles(user))
    return UserRole.ADMIN.value in roles or UserRole.OPERATOR.value in roles


def user_company_ids(user: User) -> list[str]:
    return [m.company_id for m in user.memberships]


def resolve_customer_company_id(user: User) -> str:
    customer_companies = [m.company_id for m in user.memberships if m.company.company_type == CompanyType.CUSTOMER.value]
    if customer_companies:
        return customer_companies[0]
    if is_operator_or_admin(user):
        # Operators may create internal/test RFQs only when linked to a customer company later.
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Operator RFQ creation requires a customer company context")
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not linked to customer company")


def generate_rfq_number(db: Session) -> str:
    year = datetime.now(timezone.utc).year
    count = db.scalar(select(RFQ).where(RFQ.rfq_number.like(f"FB-RFQ-{year}-%")).count()) if False else None
    # SQLite-compatible simple sequence based on total RFQ count.
    total = len(list(db.scalars(select(RFQ.id)).all())) + 1
    return f"FB-RFQ-{year}-{total:06d}"


def supplier_company_ids(user: User) -> list[str]:
    return [m.company_id for m in user.memberships if m.company.company_type == CompanyType.SUPPLIER.value]


def can_view_rfq(user: User, rfq: RFQ) -> bool:
    if is_operator_or_admin(user):
        return True
    if rfq.customer_company_id in user_company_ids(user):
        return True
    # Supplier RFQ visibility is invitation-based. Do not expose uninvited RFQs.
    supplier_ids = set(supplier_company_ids(user))
    if not supplier_ids:
        return False
    return any(
        invitation.supplier_company_id in supplier_ids
        and invitation.status in ACTIVE_SUPPLIER_INVITATION_STATUSES
        for invitation in getattr(rfq, "tender_invitations", [])
    )


def can_edit_rfq(user: User, rfq: RFQ) -> bool:
    if is_operator_or_admin(user):
        return True
    return rfq.customer_company_id in user_company_ids(user) and rfq.status in {RFQStatus.DRAFT.value, RFQStatus.NEEDS_CLARIFICATION.value}


def get_rfq_or_404(db: Session, rfq_id: str) -> RFQ:
    rfq = db.get(RFQ, rfq_id)
    if not rfq:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="RFQ not found")
    return rfq


def serialize_technical_spec(spec: RFQTechnicalSpec | None) -> dict | None:
    if not spec:
        return None
    return {
        "suggested_process": spec.suggested_process,
        "material": spec.material,
        "material_grade": spec.material_grade,
        "tolerances": spec.tolerances,
        "surface_finish": spec.surface_finish,
        "heat_treatment": spec.heat_treatment,
        "hardness": spec.hardness,
        "working_environment": spec.working_environment,
        "temperature_range": spec.temperature_range,
        "load_requirements": spec.load_requirements,
        "quality_requirements": spec.quality_requirements,
        "testing_requirements": spec.testing_requirements,
        "packaging_requirements": spec.packaging_requirements,
        "drawing_available": spec.drawing_available,
        "model_3d_available": spec.model_3d_available,
        "sample_available": spec.sample_available,
        "technical_notes": spec.technical_notes,
    }


def serialize_logistics_spec(spec: RFQLogisticsSpec | None) -> dict | None:
    if not spec:
        return None
    return {
        "origin_country": spec.origin_country,
        "origin_city": spec.origin_city,
        "destination_country": spec.destination_country,
        "destination_city": spec.destination_city,
        "destination_address": spec.destination_address,
        "preferred_incoterms": spec.preferred_incoterms,
        "preferred_transport_mode": spec.preferred_transport_mode,
        "estimated_weight_kg": float(spec.estimated_weight_kg) if spec.estimated_weight_kg is not None else None,
        "estimated_volume_cbm": float(spec.estimated_volume_cbm) if spec.estimated_volume_cbm is not None else None,
        "requires_customs_clearance": spec.requires_customs_clearance,
        "requires_certification": spec.requires_certification,
        "certification_notes": spec.certification_notes,
    }


def serialize_commercial_spec(spec: RFQCommercialSpec | None) -> dict | None:
    if not spec:
        return None
    return {
        "target_unit_price": float(spec.target_unit_price) if spec.target_unit_price is not None else None,
        "target_total_budget": float(spec.target_total_budget) if spec.target_total_budget is not None else None,
        "current_purchase_price": float(spec.current_purchase_price) if spec.current_purchase_price is not None else None,
        "original_part_price": float(spec.original_part_price) if spec.original_part_price is not None else None,
        "payment_terms": spec.payment_terms,
        "requires_sample": spec.requires_sample,
        "requires_tooling": spec.requires_tooling,
        "expected_tooling_budget": float(spec.expected_tooling_budget) if spec.expected_tooling_budget is not None else None,
        "deadline_for_quotes": spec.deadline_for_quotes.isoformat() if spec.deadline_for_quotes else None,
        "decision_deadline": spec.decision_deadline.isoformat() if spec.decision_deadline else None,
        "commercial_notes": spec.commercial_notes,
    }


def serialize_status_history(item: RFQStatusHistory) -> dict:
    return {
        "id": item.id,
        "old_status": item.old_status,
        "new_status": item.new_status,
        "comment": item.comment,
        "changed_by_user_id": item.changed_by_user_id,
        "created_at": item.created_at.isoformat(),
    }


def serialize_rfq(rfq: RFQ, detailed: bool = True) -> dict:
    data = {
        "id": rfq.id,
        "rfq_number": rfq.rfq_number,
        "customer_company_id": rfq.customer_company_id,
        "created_by_user_id": rfq.created_by_user_id,
        "title": rfq.title,
        "description": rfq.description,
        "rfq_type": rfq.rfq_type,
        "category": rfq.category,
        "status": rfq.status,
        "quantity": float(rfq.quantity) if rfq.quantity is not None else None,
        "unit": rfq.unit,
        "target_price": float(rfq.target_price) if rfq.target_price is not None else None,
        "currency": rfq.currency,
        "delivery_country": rfq.delivery_country,
        "delivery_city": rfq.delivery_city,
        "delivery_address": rfq.delivery_address,
        "delivery_deadline": rfq.delivery_deadline.isoformat() if rfq.delivery_deadline else None,
        "is_recurring": rfq.is_recurring,
        "recurring_frequency": rfq.recurring_frequency,
        "annual_volume": float(rfq.annual_volume) if rfq.annual_volume is not None else None,
        "is_confidential": rfq.is_confidential,
        "allows_alternative_material": rfq.allows_alternative_material,
        "allows_alternative_process": rfq.allows_alternative_process,
        "operator_user_id": rfq.operator_user_id,
        "submitted_at": rfq.submitted_at.isoformat() if rfq.submitted_at else None,
        "created_at": rfq.created_at.isoformat(),
        "updated_at": rfq.updated_at.isoformat(),
    }
    if detailed:
        data["technical_spec"] = serialize_technical_spec(rfq.technical_spec)
        data["logistics_spec"] = serialize_logistics_spec(rfq.logistics_spec)
        data["commercial_spec"] = serialize_commercial_spec(rfq.commercial_spec)
        data["status_history"] = [serialize_status_history(item) for item in sorted(rfq.status_history, key=lambda x: x.created_at)]
    return data


def create_rfq(db: Session, user: User, payload: RFQCreate) -> RFQ:
    company_id = resolve_customer_company_id(user)
    company = db.get(Company, company_id)
    if not company or company.company_type != CompanyType.CUSTOMER.value:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Customer company not found")
    rfq = RFQ(
        rfq_number=generate_rfq_number(db),
        customer_company_id=company_id,
        created_by_user_id=user.id,
        title=payload.title,
        description=payload.description,
        rfq_type=payload.rfq_type.value,
        category=payload.category,
        quantity=payload.quantity,
        unit=payload.unit,
        target_price=payload.target_price,
        currency=payload.currency,
        delivery_country=payload.delivery_country,
        delivery_city=payload.delivery_city,
        delivery_address=payload.delivery_address,
        delivery_deadline=payload.delivery_deadline,
        is_recurring=payload.is_recurring,
        recurring_frequency=payload.recurring_frequency,
        annual_volume=payload.annual_volume,
        is_confidential=payload.is_confidential,
        allows_alternative_material=payload.allows_alternative_material,
        allows_alternative_process=payload.allows_alternative_process,
    )
    db.add(rfq)
    db.flush()
    db.add(RFQStatusHistory(rfq_id=rfq.id, old_status=None, new_status=rfq.status, changed_by_user_id=user.id, comment="RFQ created"))
    log_action(db, actor_user_id=user.id, action="RFQ_CREATED", object_type="RFQ", object_id=rfq.id, after_data={"rfq_number": rfq.rfq_number})
    db.commit()
    db.refresh(rfq)
    return rfq


def update_rfq(db: Session, user: User, rfq: RFQ, payload: RFQUpdate) -> RFQ:
    if not can_edit_rfq(user, rfq):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="RFQ is not editable for this user")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(rfq, key, value)
    log_action(db, actor_user_id=user.id, action="RFQ_UPDATED", object_type="RFQ", object_id=rfq.id)
    db.commit()
    db.refresh(rfq)
    return rfq


def change_rfq_status(db: Session, user: User, rfq: RFQ, new_status: RFQStatus, comment: str | None = None) -> RFQ:
    if not is_operator_or_admin(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only operator/admin can change RFQ status")
    old = rfq.status
    rfq.status = new_status.value
    if new_status == RFQStatus.PUBLISHED:
        rfq.published_at = datetime.now(timezone.utc)
    if new_status in {RFQStatus.CLOSED, RFQStatus.CANCELLED, RFQStatus.REJECTED}:
        rfq.closed_at = datetime.now(timezone.utc)
    db.add(RFQStatusHistory(rfq_id=rfq.id, old_status=old, new_status=rfq.status, changed_by_user_id=user.id, comment=comment))
    log_action(db, actor_user_id=user.id, action="RFQ_STATUS_CHANGED", object_type="RFQ", object_id=rfq.id, before_data={"status": old}, after_data={"status": rfq.status})
    notify_company(db, company_id=rfq.customer_company_id, title="RFQ status updated", message=f"{rfq.rfq_number} status changed to {rfq.status}", notification_type="RFQ_STATUS_CHANGED", object_type="RFQ", object_id=rfq.id)
    db.commit()
    db.refresh(rfq)
    return rfq


def submit_rfq(db: Session, user: User, rfq: RFQ) -> RFQ:
    if rfq.customer_company_id not in user_company_ids(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="RFQ access denied")
    if rfq.status not in {RFQStatus.DRAFT.value, RFQStatus.NEEDS_CLARIFICATION.value}:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="RFQ cannot be submitted from current status")
    old = rfq.status
    rfq.status = RFQStatus.SUBMITTED.value
    rfq.submitted_at = datetime.now(timezone.utc)
    db.add(RFQStatusHistory(rfq_id=rfq.id, old_status=old, new_status=rfq.status, changed_by_user_id=user.id, comment="Submitted by customer"))
    log_action(db, actor_user_id=user.id, action="RFQ_SUBMITTED", object_type="RFQ", object_id=rfq.id)
    notify_roles(db, roles=[UserRole.ADMIN.value, UserRole.OPERATOR.value], title="New RFQ submitted", message=f"{rfq.rfq_number} is waiting for operator review", notification_type="RFQ_SUBMITTED", object_type="RFQ", object_id=rfq.id)
    db.commit()
    db.refresh(rfq)
    return rfq


def upsert_spec(db: Session, user: User, rfq: RFQ, payload, model_cls, attr_name: str):
    if not can_edit_rfq(user, rfq):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="RFQ specs are not editable for this user")
    spec = getattr(rfq, attr_name)
    values = payload.model_dump()
    # Convert enums to raw strings for SQLAlchemy String columns.
    for key, value in list(values.items()):
        if hasattr(value, "value"):
            values[key] = value.value
    if spec is None:
        spec = model_cls(rfq_id=rfq.id, **values)
        db.add(spec)
    else:
        for key, value in values.items():
            setattr(spec, key, value)
    log_action(db, actor_user_id=user.id, action=f"RFQ_{attr_name.upper()}_UPSERTED", object_type="RFQ", object_id=rfq.id)
    db.commit()
    db.refresh(rfq)
    return getattr(rfq, attr_name)


def list_rfqs_for_user(db: Session, user: User, status_filter: str | None = None) -> list[RFQ]:
    stmt = select(RFQ).order_by(RFQ.created_at.desc())
    if not is_operator_or_admin(user):
        company_ids = user_company_ids(user)
        stmt = stmt.where(RFQ.customer_company_id.in_(company_ids))
    if status_filter:
        stmt = stmt.where(RFQ.status == status_filter)
    return list(db.scalars(stmt).all())
