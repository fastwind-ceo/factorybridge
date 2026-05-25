from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.company import Company, CompanyMember
from app.models.enums import CompanyType, UserRole
from app.models.user import User, UserRoleModel
from app.schemas.auth import RegisterRequest
from app.security.passwords import hash_password, verify_password
from app.services.audit_service import log_action


def normalize_email(email: str) -> str:
    return email.strip().lower()


def user_roles(user: User) -> list[str]:
    return sorted({role.role for role in user.roles})


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == normalize_email(email)))


def get_user_by_id(db: Session, user_id: str) -> User | None:
    return db.get(User, user_id)


def default_role_for_company_type(company_type: CompanyType) -> UserRole:
    if company_type == CompanyType.SUPPLIER:
        return UserRole.SUPPLIER
    if company_type == CompanyType.PLATFORM_OPERATOR:
        return UserRole.OPERATOR
    return UserRole.CUSTOMER


def register_user_with_company(db: Session, payload: RegisterRequest) -> tuple[User, Company]:
    email = normalize_email(payload.email)
    if get_user_by_email(db, email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already registered")

    user = User(
        email=email,
        password_hash=hash_password(payload.password),
        first_name=payload.first_name,
        last_name=payload.last_name,
    )
    company = Company(company_type=payload.company_type.value, name=payload.company_name)
    db.add_all([user, company])
    db.flush()

    db.add(CompanyMember(company_id=company.id, user_id=user.id, position="Primary contact", is_primary_contact=True))
    db.add(UserRoleModel(user_id=user.id, role=default_role_for_company_type(payload.company_type).value))
    log_action(db, actor_user_id=user.id, action="USER_REGISTERED", object_type="USER", object_id=user.id)
    log_action(db, actor_user_id=user.id, action="COMPANY_CREATED", object_type="COMPANY", object_id=company.id)
    db.commit()
    db.refresh(user)
    db.refresh(company)
    return user, company


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")
    return user


def ensure_role(db: Session, user: User, role: str) -> None:
    if role not in user_roles(user):
        db.add(UserRoleModel(user_id=user.id, role=role))
        log_action(db, actor_user_id=user.id, action="ROLE_ASSIGNED", object_type="USER", object_id=user.id, after_data={"role": role})
