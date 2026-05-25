from datetime import datetime, timezone, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.company import Company
from app.models.enums import CompanyType, RFQStatus, UserRole
from app.models.rfq import RFQ, TenderInvitation
from app.models.user import User
from app.schemas.tender import TenderInviteCreate
from app.services.audit_service import log_action
from app.services.auth_service import user_roles
from app.services.notification_service import notify_company
from app.services.rfq_service import get_rfq_or_404, serialize_rfq, user_company_ids

ACTIVE_INVITATION_STATUSES = {"INVITED", "VIEWED", "ACCEPTED", "QUOTE_SUBMITTED"}
TERMINAL_INVITATION_STATUSES = {"DECLINED", "EXPIRED", "REVOKED"}


def is_operator_or_admin(user: User) -> bool:
    roles = set(user_roles(user))
    return UserRole.ADMIN.value in roles or UserRole.OPERATOR.value in roles


def supplier_company_ids(user: User) -> list[str]:
    return [m.company_id for m in user.memberships if m.company.company_type == CompanyType.SUPPLIER.value]


def serialize_invitation(invitation: TenderInvitation, include_rfq: bool = False) -> dict:
    data = {
        "id": invitation.id,
        "rfq_id": invitation.rfq_id,
        "supplier_company_id": invitation.supplier_company_id,
        "invited_by_user_id": invitation.invited_by_user_id,
        "status": invitation.status,
        "access_level": invitation.access_level,
        "deadline": invitation.deadline.isoformat() if invitation.deadline else None,
        "message": invitation.message,
        "created_at": invitation.created_at.isoformat(),
        "responded_at": invitation.responded_at.isoformat() if invitation.responded_at else None,
    }
    if include_rfq:
        data["rfq"] = serialize_rfq(invitation.rfq, detailed=False) if hasattr(invitation, "rfq") else None
    return data


def invite_suppliers(db: Session, user: User, rfq_id: str, payload: TenderInviteCreate) -> list[TenderInvitation]:
    if not is_operator_or_admin(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only operator/admin can invite suppliers")
    rfq = get_rfq_or_404(db, rfq_id)
    if rfq.status not in {RFQStatus.APPROVED_FOR_TENDER.value, RFQStatus.PUBLISHED.value, RFQStatus.QUOTING.value}:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="RFQ must be approved or published before supplier invitation")

    created: list[TenderInvitation] = []
    for supplier_company_id in payload.supplier_company_ids:
        company = db.get(Company, supplier_company_id)
        if not company or company.company_type != CompanyType.SUPPLIER.value:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Supplier company not found: {supplier_company_id}")
        existing = db.scalar(select(TenderInvitation).where(
            TenderInvitation.rfq_id == rfq_id,
            TenderInvitation.supplier_company_id == supplier_company_id,
            TenderInvitation.status.notin_(TERMINAL_INVITATION_STATUSES),
        ))
        if existing:
            created.append(existing)
            continue
        invitation = TenderInvitation(
            rfq_id=rfq_id,
            supplier_company_id=supplier_company_id,
            invited_by_user_id=user.id,
            deadline=payload.deadline,
            access_level=payload.access_level,
            message=payload.message,
        )
        db.add(invitation)
        notify_company(db, company_id=supplier_company_id, title="New RFQ invitation", message=f"You are invited to quote {rfq.rfq_number}", notification_type="SUPPLIER_INVITED", object_type="RFQ", object_id=rfq_id)
        created.append(invitation)
    if rfq.status == RFQStatus.APPROVED_FOR_TENDER.value:
        rfq.status = RFQStatus.PUBLISHED.value
        rfq.published_at = datetime.now(timezone.utc)
    log_action(db, actor_user_id=user.id, action="SUPPLIERS_INVITED", object_type="RFQ", object_id=rfq_id, after_data={"supplier_company_ids": payload.supplier_company_ids})
    db.commit()
    for item in created:
        db.refresh(item)
    return created


def list_invitations_for_rfq(db: Session, user: User, rfq_id: str) -> list[TenderInvitation]:
    if not is_operator_or_admin(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only operator/admin can list RFQ invitations")
    return list(db.scalars(select(TenderInvitation).where(TenderInvitation.rfq_id == rfq_id).order_by(TenderInvitation.created_at.desc())).all())


def get_invitation_or_404(db: Session, invitation_id: str) -> TenderInvitation:
    invitation = db.get(TenderInvitation, invitation_id)
    if not invitation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tender invitation not found")
    return invitation


def ensure_supplier_owns_invitation(user: User, invitation: TenderInvitation) -> None:
    if invitation.supplier_company_id not in supplier_company_ids(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invitation access denied")


def accept_invitation(db: Session, user: User, invitation: TenderInvitation) -> TenderInvitation:
    ensure_supplier_owns_invitation(user, invitation)
    if invitation.status in TERMINAL_INVITATION_STATUSES:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Invitation is not active")
    invitation.status = "ACCEPTED"
    invitation.responded_at = datetime.now(timezone.utc)
    log_action(db, actor_user_id=user.id, action="TENDER_INVITATION_ACCEPTED", object_type="TENDER_INVITATION", object_id=invitation.id)
    rfq = db.get(RFQ, invitation.rfq_id)
    if rfq:
        notify_company(db, company_id=rfq.customer_company_id, title="Supplier accepted invitation", message=f"A supplier accepted invitation for {rfq.rfq_number}", notification_type="INVITATION_ACCEPTED", object_type="RFQ", object_id=rfq.id)
    db.commit()
    db.refresh(invitation)
    return invitation


def decline_invitation(db: Session, user: User, invitation: TenderInvitation, reason: str | None = None) -> TenderInvitation:
    ensure_supplier_owns_invitation(user, invitation)
    if invitation.status in TERMINAL_INVITATION_STATUSES:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Invitation is not active")
    invitation.status = "DECLINED"
    invitation.responded_at = datetime.now(timezone.utc)
    log_action(db, actor_user_id=user.id, action="TENDER_INVITATION_DECLINED", object_type="TENDER_INVITATION", object_id=invitation.id, after_data={"reason": reason})
    db.commit()
    db.refresh(invitation)
    return invitation


def supplier_available_invitations(db: Session, user: User) -> list[TenderInvitation]:
    company_ids = supplier_company_ids(user)
    if not company_ids:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not linked to supplier company")
    return list(db.scalars(select(TenderInvitation).where(
        TenderInvitation.supplier_company_id.in_(company_ids),
        TenderInvitation.status.in_(ACTIVE_INVITATION_STATUSES),
    ).order_by(TenderInvitation.created_at.desc())).all())


def supplier_can_view_rfq(db: Session, user: User, rfq_id: str) -> bool:
    company_ids = supplier_company_ids(user)
    if not company_ids:
        return False
    invitation = db.scalar(select(TenderInvitation).where(
        TenderInvitation.rfq_id == rfq_id,
        TenderInvitation.supplier_company_id.in_(company_ids),
        TenderInvitation.status.in_(ACTIVE_INVITATION_STATUSES),
    ))
    return invitation is not None
