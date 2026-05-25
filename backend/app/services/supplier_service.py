from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.company import Company
from app.models.enums import CompanyType, UserRole
from app.models.supplier import SupplierCapability, SupplierProfile
from app.models.user import User
from app.schemas.supplier import SupplierCapabilityCreate, SupplierProfileCreate, SupplierProfileUpdate
from app.services.audit_service import log_action
from app.services.auth_service import user_roles


def user_company_ids(user: User) -> list[str]:
    return [membership.company_id for membership in user.memberships]


def is_operator_or_admin(user: User) -> bool:
    roles = set(user_roles(user))
    return UserRole.ADMIN.value in roles or UserRole.OPERATOR.value in roles


def resolve_supplier_company_id(user: User, requested_company_id: str | None) -> str:
    if requested_company_id and is_operator_or_admin(user):
        return requested_company_id
    supplier_companies = [
        membership.company_id
        for membership in user.memberships
        if membership.company.company_type == CompanyType.SUPPLIER.value
    ]
    if not supplier_companies:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not linked to supplier company")
    if requested_company_id and requested_company_id not in supplier_companies:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Supplier company access denied")
    return requested_company_id or supplier_companies[0]


def can_manage_supplier(user: User, company_id: str) -> bool:
    return is_operator_or_admin(user) or company_id in user_company_ids(user)


def get_supplier_profile_by_company(db: Session, company_id: str) -> SupplierProfile | None:
    return db.scalar(select(SupplierProfile).where(SupplierProfile.company_id == company_id))


def serialize_capability(capability: SupplierCapability) -> dict:
    return {
        "id": capability.id,
        "process": capability.process,
        "materials": capability.materials or [],
        "min_order_quantity": capability.min_order_quantity,
        "max_part_size": capability.max_part_size,
        "tolerance_level": capability.tolerance_level,
        "surface_treatments": capability.surface_treatments or [],
        "has_tooling_capability": capability.has_tooling_capability,
        "has_design_support": capability.has_design_support,
        "has_qc_team": capability.has_qc_team,
        "lead_time_sample_days": capability.lead_time_sample_days,
        "lead_time_mass_days": capability.lead_time_mass_days,
        "description": capability.description,
    }


def serialize_supplier(profile: SupplierProfile, include_capabilities: bool = True) -> dict:
    company = profile.company
    data = {
        "company_id": profile.company_id,
        "company_name": company.name if company else None,
        "company_verification_status": company.verification_status if company else None,
        "supplier_profile_id": profile.id,
        "chinese_name": profile.chinese_name,
        "english_name": profile.english_name,
        "province": profile.province,
        "city": profile.city,
        "factory_address": profile.factory_address,
        "year_established": profile.year_established,
        "employee_count": profile.employee_count,
        "export_experience": profile.export_experience,
        "export_countries": profile.export_countries,
        "main_industries": profile.main_industries,
        "rating": float(profile.rating) if profile.rating is not None else None,
        "verification_level": profile.verification_level,
        "is_available": profile.is_available,
        "notes": profile.notes,
    }
    if include_capabilities:
        data["capabilities"] = [serialize_capability(item) for item in profile.capabilities]
    return data


def create_supplier_profile(db: Session, user: User, payload: SupplierProfileCreate) -> SupplierProfile:
    company_id = resolve_supplier_company_id(user, payload.company_id)
    company = db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    if company.company_type != CompanyType.SUPPLIER.value:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Company is not a supplier company")
    existing = get_supplier_profile_by_company(db, company_id)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Supplier profile already exists")
    profile = SupplierProfile(
        company_id=company_id,
        chinese_name=payload.chinese_name,
        english_name=payload.english_name,
        province=payload.province,
        city=payload.city,
        factory_address=payload.factory_address,
        year_established=payload.year_established,
        employee_count=payload.employee_count,
        export_experience=payload.export_experience,
        export_countries=payload.export_countries,
        main_industries=payload.main_industries,
        notes=payload.notes,
    )
    db.add(profile)
    log_action(db, actor_user_id=user.id, action="SUPPLIER_PROFILE_CREATED", object_type="SUPPLIER", object_id=company_id)
    db.commit()
    db.refresh(profile)
    return profile


def update_supplier_profile(db: Session, user: User, company_id: str, payload: SupplierProfileUpdate) -> SupplierProfile:
    if not can_manage_supplier(user, company_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Supplier profile access denied")
    profile = get_supplier_profile_by_company(db, company_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier profile not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, key, value)
    log_action(db, actor_user_id=user.id, action="SUPPLIER_PROFILE_UPDATED", object_type="SUPPLIER", object_id=company_id)
    db.commit()
    db.refresh(profile)
    return profile


def add_capability(db: Session, user: User, company_id: str, payload: SupplierCapabilityCreate) -> SupplierCapability:
    if not can_manage_supplier(user, company_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Supplier capability access denied")
    profile = get_supplier_profile_by_company(db, company_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier profile not found")
    capability = SupplierCapability(
        supplier_profile_id=profile.id,
        process=payload.process.value,
        materials=[item.value for item in payload.materials],
        min_order_quantity=payload.min_order_quantity,
        max_part_size=payload.max_part_size,
        tolerance_level=payload.tolerance_level,
        surface_treatments=payload.surface_treatments,
        has_tooling_capability=payload.has_tooling_capability,
        has_design_support=payload.has_design_support,
        has_qc_team=payload.has_qc_team,
        lead_time_sample_days=payload.lead_time_sample_days,
        lead_time_mass_days=payload.lead_time_mass_days,
        description=payload.description,
    )
    db.add(capability)
    log_action(db, actor_user_id=user.id, action="SUPPLIER_CAPABILITY_ADDED", object_type="SUPPLIER", object_id=company_id, after_data={"process": capability.process})
    db.commit()
    db.refresh(capability)
    return capability
