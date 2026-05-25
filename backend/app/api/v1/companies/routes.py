from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.company import Company
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.company import CompanyUpdate
from app.security.dependencies import get_current_user, require_roles
from app.services.auth_service import user_roles

router = APIRouter(prefix="/companies", tags=["companies"])


def can_access_company(user: User, company_id: str) -> bool:
    roles = set(user_roles(user))
    if UserRole.ADMIN.value in roles or UserRole.OPERATOR.value in roles:
        return True
    return any(member.company_id == company_id for member in user.memberships)


@router.get("/my", response_model=APIResponse)
def get_my_companies(current_user: User = Depends(get_current_user)):
    items = [
        {
            "id": m.company.id,
            "name": m.company.name,
            "company_type": m.company.company_type,
            "country": m.company.country,
            "city": m.company.city,
            "verification_status": m.company.verification_status,
        }
        for m in current_user.memberships
    ]
    return APIResponse(data=items)


@router.get("/{company_id}", response_model=APIResponse)
def get_company(company_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    company = db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    if not can_access_company(current_user, company_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Company access denied")
    return APIResponse(data={
        "id": company.id,
        "name": company.name,
        "company_type": company.company_type,
        "country": company.country,
        "city": company.city,
        "verification_status": company.verification_status,
        "website": company.website,
        "description": company.description,
    })


@router.patch("/{company_id}", response_model=APIResponse)
def update_company(company_id: str, payload: CompanyUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    company = db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    if not can_access_company(current_user, company_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Company access denied")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(company, key, value)
    db.commit()
    db.refresh(company)
    return APIResponse(data={"id": company.id, "name": company.name})
