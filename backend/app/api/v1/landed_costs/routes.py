from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.landed_cost import LandedCostCreate, LandedCostUpdate
from app.security.dependencies import get_current_user
from app.services.landed_cost_service import (
    can_view_landed_cost,
    create_landed_cost,
    get_landed_cost_or_404,
    list_landed_costs_for_rfq,
    serialize_landed_cost,
    update_landed_cost,
    is_operator_or_admin,
)

router = APIRouter(prefix="/landed-costs", tags=["landed-costs"])


@router.post("/quotes/{quote_id}", response_model=APIResponse)
def create(
    quote_id: str,
    payload: LandedCostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    landed_cost = create_landed_cost(db, current_user, quote_id, payload)
    return APIResponse(data=serialize_landed_cost(landed_cost))


@router.get("/{landed_cost_id}", response_model=APIResponse)
def get(
    landed_cost_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    landed_cost = get_landed_cost_or_404(db, landed_cost_id)
    if not can_view_landed_cost(db, current_user, landed_cost):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Landed cost access denied")
    return APIResponse(data=serialize_landed_cost(landed_cost, customer_safe=not is_operator_or_admin(current_user)))


@router.get("/rfqs/{rfq_id}/list", response_model=APIResponse)
def list_for_rfq(
    rfq_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = list_landed_costs_for_rfq(db, current_user, rfq_id)
    return APIResponse(data={"items": [serialize_landed_cost(item, customer_safe=not is_operator_or_admin(current_user)) for item in items]})


@router.patch("/{landed_cost_id}", response_model=APIResponse)
def update(
    landed_cost_id: str,
    payload: LandedCostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    landed_cost = get_landed_cost_or_404(db, landed_cost_id)
    landed_cost = update_landed_cost(db, current_user, landed_cost, payload)
    return APIResponse(data=serialize_landed_cost(landed_cost))
