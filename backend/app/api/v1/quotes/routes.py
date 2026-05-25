from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.quote import QuoteCreate, QuoteUpdate
from app.security.dependencies import get_current_user, require_roles
from app.services.quote_service import (
    accept_quote,
    build_customer_safe_comparison,
    can_user_view_quote,
    create_quote,
    get_quote_or_404,
    list_my_supplier_quotes,
    list_quotes_for_rfq,
    reject_quote,
    serialize_quote,
    submit_quote,
    update_quote,
)

router = APIRouter(prefix="/quotes", tags=["quotes"])


@router.post("/rfqs/{rfq_id}", response_model=APIResponse)
def create(
    rfq_id: str,
    payload: QuoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.SUPPLIER.value)),
):
    quote = create_quote(db, current_user, rfq_id, payload)
    return APIResponse(data=serialize_quote(quote))


@router.patch("/{quote_id}", response_model=APIResponse)
def update(
    quote_id: str,
    payload: QuoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    quote = get_quote_or_404(db, quote_id)
    quote = update_quote(db, current_user, quote, payload)
    return APIResponse(data=serialize_quote(quote))


@router.post("/{quote_id}/submit", response_model=APIResponse)
def submit(
    quote_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.SUPPLIER.value)),
):
    quote = get_quote_or_404(db, quote_id)
    quote = submit_quote(db, current_user, quote)
    return APIResponse(data=serialize_quote(quote))


@router.get("/rfqs/{rfq_id}", response_model=APIResponse)
def list_for_rfq(
    rfq_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    quotes = list_quotes_for_rfq(db, current_user, rfq_id)
    return APIResponse(data={"items": [serialize_quote(item) for item in quotes]})


@router.get("/rfqs/{rfq_id}/customer-comparison", response_model=APIResponse)
def customer_comparison(
    rfq_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    quotes = list_quotes_for_rfq(db, current_user, rfq_id)
    return APIResponse(data=build_customer_safe_comparison(quotes))


@router.get("/supplier/my", response_model=APIResponse)
def my_supplier_quotes(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.SUPPLIER.value)),
):
    quotes = list_my_supplier_quotes(db, current_user)
    return APIResponse(data={"items": [serialize_quote(item) for item in quotes]})


@router.get("/{quote_id}", response_model=APIResponse)
def get(
    quote_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    quote = get_quote_or_404(db, quote_id)
    if not can_user_view_quote(db, current_user, quote):
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Quote access denied")
    return APIResponse(data=serialize_quote(quote))


@router.post("/{quote_id}/accept", response_model=APIResponse)
def accept(
    quote_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    quote = get_quote_or_404(db, quote_id)
    return APIResponse(data=serialize_quote(accept_quote(db, current_user, quote)))


@router.post("/{quote_id}/reject", response_model=APIResponse)
def reject(
    quote_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    quote = get_quote_or_404(db, quote_id)
    return APIResponse(data=serialize_quote(reject_quote(db, current_user, quote)))
