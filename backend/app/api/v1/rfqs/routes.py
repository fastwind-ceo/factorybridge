from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.enums import MaterialType, ManufacturingProcess, RFQStatus, RFQType, UserRole
from app.models.rfq import RFQCommercialSpec, RFQLogisticsSpec, RFQTechnicalSpec
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.rfq import (
    RFQCommercialSpecUpsert,
    RFQCreate,
    RFQLogisticsSpecUpsert,
    RFQStatusChange,
    RFQTechnicalSpecUpsert,
    RFQUpdate,
)
from app.security.dependencies import get_current_user, require_roles
from app.services.rfq_service import (
    can_view_rfq,
    change_rfq_status,
    create_rfq,
    get_rfq_or_404,
    list_rfqs_for_user,
    serialize_commercial_spec,
    serialize_logistics_spec,
    serialize_rfq,
    serialize_technical_spec,
    submit_rfq,
    update_rfq,
    upsert_spec,
)
from fastapi import HTTPException, status

router = APIRouter(prefix="/rfqs", tags=["rfqs"])


@router.get("/dictionaries", response_model=APIResponse)
def rfq_dictionaries(_: User = Depends(get_current_user)):
    return APIResponse(data={
        "rfq_types": [item.value for item in RFQType],
        "rfq_statuses": [item.value for item in RFQStatus],
        "manufacturing_processes": [item.value for item in ManufacturingProcess],
        "materials": [item.value for item in MaterialType],
    })


@router.post("", response_model=APIResponse)
def create(payload: RFQCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rfq = create_rfq(db, current_user, payload)
    return APIResponse(data=serialize_rfq(rfq))


@router.get("/my", response_model=APIResponse)
def list_my(
    status_filter: RFQStatus | None = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rfqs = list_rfqs_for_user(db, current_user, status_filter.value if status_filter else None)
    total = len(rfqs)
    start = (page - 1) * page_size
    items = rfqs[start:start + page_size]
    return APIResponse(data={
        "items": [serialize_rfq(item, detailed=False) for item in items],
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": (total + page_size - 1) // page_size,
    })


@router.get("", response_model=APIResponse)
def list_all(
    status_filter: RFQStatus | None = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN.value, UserRole.OPERATOR.value)),
):
    rfqs = list_rfqs_for_user(db, current_user, status_filter.value if status_filter else None)
    total = len(rfqs)
    start = (page - 1) * page_size
    items = rfqs[start:start + page_size]
    return APIResponse(data={
        "items": [serialize_rfq(item, detailed=False) for item in items],
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": (total + page_size - 1) // page_size,
    })


@router.get("/{rfq_id}", response_model=APIResponse)
def get_one(rfq_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rfq = get_rfq_or_404(db, rfq_id)
    if not can_view_rfq(current_user, rfq):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="RFQ access denied")
    return APIResponse(data=serialize_rfq(rfq))


@router.patch("/{rfq_id}", response_model=APIResponse)
def patch_one(rfq_id: str, payload: RFQUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rfq = get_rfq_or_404(db, rfq_id)
    updated = update_rfq(db, current_user, rfq, payload)
    return APIResponse(data=serialize_rfq(updated))


@router.post("/{rfq_id}/submit", response_model=APIResponse)
def submit(rfq_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rfq = get_rfq_or_404(db, rfq_id)
    submitted = submit_rfq(db, current_user, rfq)
    return APIResponse(data=serialize_rfq(submitted))


@router.post("/{rfq_id}/status", response_model=APIResponse)
def status_change(rfq_id: str, payload: RFQStatusChange, db: Session = Depends(get_db), current_user: User = Depends(require_roles(UserRole.ADMIN.value, UserRole.OPERATOR.value))):
    rfq = get_rfq_or_404(db, rfq_id)
    changed = change_rfq_status(db, current_user, rfq, payload.new_status, payload.comment)
    return APIResponse(data=serialize_rfq(changed))


@router.put("/{rfq_id}/technical-specs", response_model=APIResponse)
def upsert_technical(rfq_id: str, payload: RFQTechnicalSpecUpsert, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rfq = get_rfq_or_404(db, rfq_id)
    spec = upsert_spec(db, current_user, rfq, payload, RFQTechnicalSpec, "technical_spec")
    return APIResponse(data=serialize_technical_spec(spec))


@router.put("/{rfq_id}/logistics-specs", response_model=APIResponse)
def upsert_logistics(rfq_id: str, payload: RFQLogisticsSpecUpsert, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rfq = get_rfq_or_404(db, rfq_id)
    spec = upsert_spec(db, current_user, rfq, payload, RFQLogisticsSpec, "logistics_spec")
    return APIResponse(data=serialize_logistics_spec(spec))


@router.put("/{rfq_id}/commercial-specs", response_model=APIResponse)
def upsert_commercial(rfq_id: str, payload: RFQCommercialSpecUpsert, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rfq = get_rfq_or_404(db, rfq_id)
    spec = upsert_spec(db, current_user, rfq, payload, RFQCommercialSpec, "commercial_spec")
    return APIResponse(data=serialize_commercial_spec(spec))
