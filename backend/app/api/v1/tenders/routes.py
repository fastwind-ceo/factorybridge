from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.tender import TenderInvitationDecision, TenderInviteCreate
from app.security.dependencies import get_current_user, require_roles
from app.services.rfq_service import serialize_rfq
from app.services.tender_service import (
    accept_invitation,
    decline_invitation,
    get_invitation_or_404,
    invite_suppliers,
    list_invitations_for_rfq,
    serialize_invitation,
    supplier_available_invitations,
)

router = APIRouter(prefix="/tenders", tags=["tenders"])


@router.post("/rfqs/{rfq_id}/invite", response_model=APIResponse)
def invite(
    rfq_id: str,
    payload: TenderInviteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN.value, UserRole.OPERATOR.value)),
):
    invitations = invite_suppliers(db, current_user, rfq_id, payload)
    return APIResponse(data={"items": [serialize_invitation(item) for item in invitations]})


@router.get("/rfqs/{rfq_id}/invitations", response_model=APIResponse)
def list_for_rfq(
    rfq_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN.value, UserRole.OPERATOR.value)),
):
    invitations = list_invitations_for_rfq(db, current_user, rfq_id)
    return APIResponse(data={"items": [serialize_invitation(item) for item in invitations]})


@router.post("/invitations/{invitation_id}/accept", response_model=APIResponse)
def accept(
    invitation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.SUPPLIER.value)),
):
    invitation = get_invitation_or_404(db, invitation_id)
    return APIResponse(data=serialize_invitation(accept_invitation(db, current_user, invitation)))


@router.post("/invitations/{invitation_id}/decline", response_model=APIResponse)
def decline(
    invitation_id: str,
    payload: TenderInvitationDecision | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.SUPPLIER.value)),
):
    invitation = get_invitation_or_404(db, invitation_id)
    reason = payload.reason if payload else None
    return APIResponse(data=serialize_invitation(decline_invitation(db, current_user, invitation, reason)))


@router.get("/supplier/rfqs", response_model=APIResponse)
def supplier_rfqs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.SUPPLIER.value)),
):
    invitations = supplier_available_invitations(db, current_user)
    items = []
    for invitation in invitations:
        item = serialize_invitation(invitation)
        item["rfq"] = serialize_rfq(invitation.rfq, detailed=False)
        items.append(item)
    return APIResponse(data={"items": items})


@router.get("/supplier/rfqs/{rfq_id}", response_model=APIResponse)
def supplier_rfq_detail(
    rfq_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.SUPPLIER.value)),
):
    invitations = [item for item in supplier_available_invitations(db, current_user) if item.rfq_id == rfq_id]
    if not invitations:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Supplier is not invited to this RFQ")
    return APIResponse(data=serialize_rfq(invitations[0].rfq, detailed=True))
