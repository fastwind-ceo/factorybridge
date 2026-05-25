from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.common import APIResponse
from app.security.dependencies import get_current_user, require_roles
from app.services.ai_review_service import list_ai_reviews, run_ai_review, serialize_ai_review, classify_process, generate_supplier_brief, build_missing_fields
from app.services.rfq_service import get_rfq_or_404

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/rfqs/{rfq_id}/completeness-check", response_model=APIResponse)
def run_completeness_check(rfq_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rfq = get_rfq_or_404(db, rfq_id)
    review, status_updated = run_ai_review(db, rfq, current_user, review_type="COMPLETENESS_CHECK")
    return APIResponse(data={"review": serialize_ai_review(review), "status_updated": status_updated})


@router.post("/rfqs/{rfq_id}/process-classification", response_model=APIResponse)
def run_process_classification(rfq_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rfq = get_rfq_or_404(db, rfq_id)
    # Access is checked by list/run path through view check via brief generation helpers are deterministic.
    from app.services.ai_review_service import ensure_ai_access
    ensure_ai_access(current_user, rfq)
    primary, alternatives, confidence, explanation = classify_process(rfq)
    return APIResponse(data={
        "suggested_process": primary,
        "alternatives": alternatives,
        "confidence": confidence,
        "explanation": explanation,
        "requires_human_review": True,
    })


@router.post("/rfqs/{rfq_id}/supplier-brief", response_model=APIResponse)
def generate_brief(rfq_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rfq = get_rfq_or_404(db, rfq_id)
    from app.services.ai_review_service import ensure_ai_access
    ensure_ai_access(current_user, rfq)
    process, _, _, _ = classify_process(rfq)
    missing = build_missing_fields(rfq)
    brief = generate_supplier_brief(rfq, process, missing)
    return APIResponse(data={
        "supplier_brief_ru": brief["brief_ru"],
        "supplier_brief_en": brief["brief_en"],
        "supplier_brief_cn": brief["brief_cn"],
        "requires_human_review": True,
    })


@router.get("/rfqs/{rfq_id}/reviews", response_model=APIResponse)
def reviews(rfq_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rfq = get_rfq_or_404(db, rfq_id)
    items = list_ai_reviews(db, rfq, current_user)
    return APIResponse(data={"items": [serialize_ai_review(item) for item in items], "total": len(items)})


@router.post("/rfqs/{rfq_id}/operator-review", response_model=APIResponse)
def operator_ai_review(
    rfq_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN.value, UserRole.OPERATOR.value)),
):
    rfq = get_rfq_or_404(db, rfq_id)
    review, status_updated = run_ai_review(db, rfq, current_user, review_type="OPERATOR_AI_REVIEW")
    return APIResponse(data={"review": serialize_ai_review(review), "status_updated": status_updated})
