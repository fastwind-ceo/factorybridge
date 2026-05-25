from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.company import Company
from app.models.enums import CompanyVerificationStatus, ManufacturingProcess, MaterialType, UserRole
from app.models.supplier import SupplierProfile
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.supplier import SupplierCapabilityCreate, SupplierProfileCreate, SupplierProfileUpdate, SupplierVerifyRequest
from app.security.dependencies import get_current_user, require_roles
from app.services.audit_service import log_action
from app.services.supplier_service import (
    add_capability,
    can_manage_supplier,
    create_supplier_profile,
    get_supplier_profile_by_company,
    serialize_capability,
    serialize_supplier,
    update_supplier_profile,
)

router = APIRouter(prefix="/suppliers", tags=["suppliers"])


@router.get("/dictionaries", response_model=APIResponse)
def supplier_dictionaries(_: User = Depends(get_current_user)):
    return APIResponse(data={
        "manufacturing_processes": [item.value for item in ManufacturingProcess],
        "materials": [item.value for item in MaterialType],
        "verification_statuses": [item.value for item in CompanyVerificationStatus],
    })


@router.post("/profile", response_model=APIResponse)
def create_profile(payload: SupplierProfileCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    profile = create_supplier_profile(db, current_user, payload)
    return APIResponse(data=serialize_supplier(profile))


@router.get("/{supplier_company_id}", response_model=APIResponse)
def get_profile(supplier_company_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not can_manage_supplier(current_user, supplier_company_id):
        # Operators/admins can view via can_manage_supplier; suppliers see only own profile.
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Supplier profile access denied")
    profile = get_supplier_profile_by_company(db, supplier_company_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier profile not found")
    return APIResponse(data=serialize_supplier(profile))


@router.patch("/{supplier_company_id}", response_model=APIResponse)
def patch_profile(supplier_company_id: str, payload: SupplierProfileUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    profile = update_supplier_profile(db, current_user, supplier_company_id, payload)
    return APIResponse(data=serialize_supplier(profile))


@router.post("/{supplier_company_id}/capabilities", response_model=APIResponse)
def create_capability(supplier_company_id: str, payload: SupplierCapabilityCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    capability = add_capability(db, current_user, supplier_company_id, payload)
    return APIResponse(data=serialize_capability(capability))


@router.get("", response_model=APIResponse)
def list_suppliers(
    process: ManufacturingProcess | None = Query(default=None),
    material: MaterialType | None = Query(default=None),
    verified: bool | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    _: User = Depends(require_roles(UserRole.ADMIN.value, UserRole.OPERATOR.value)),
    db: Session = Depends(get_db),
):
    profiles = list(db.scalars(select(SupplierProfile).join(Company).order_by(SupplierProfile.created_at.desc())).all())
    if verified is True:
        profiles = [p for p in profiles if p.company.verification_status == CompanyVerificationStatus.VERIFIED.value or p.verification_level != "UNVERIFIED"]
    if process:
        profiles = [p for p in profiles if any(c.process == process.value for c in p.capabilities)]
    if material:
        profiles = [p for p in profiles if any(material.value in (c.materials or []) for c in p.capabilities)]
    total = len(profiles)
    start = (page - 1) * page_size
    items = profiles[start:start + page_size]
    return APIResponse(data={
        "items": [serialize_supplier(item) for item in items],
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": (total + page_size - 1) // page_size,
    })


@router.post("/{supplier_company_id}/verify", response_model=APIResponse)
def verify_supplier(supplier_company_id: str, payload: SupplierVerifyRequest, current_user: User = Depends(require_roles(UserRole.ADMIN.value, UserRole.OPERATOR.value)), db: Session = Depends(get_db)):
    company = db.get(Company, supplier_company_id)
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    profile = get_supplier_profile_by_company(db, supplier_company_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier profile not found")
    profile.verification_level = payload.verification_level
    if payload.company_verification_status:
        try:
            status_value = CompanyVerificationStatus(payload.company_verification_status).value
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Unknown company verification status") from exc
        company.verification_status = status_value
    if payload.notes:
        profile.notes = payload.notes
    log_action(db, actor_user_id=current_user.id, action="SUPPLIER_VERIFIED", object_type="SUPPLIER", object_id=supplier_company_id, after_data=payload.model_dump())
    db.commit()
    db.refresh(profile)
    return APIResponse(data=serialize_supplier(profile))
