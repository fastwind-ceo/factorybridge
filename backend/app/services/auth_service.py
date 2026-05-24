from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.company import Company, CompanyMember
from app.models.enums import UserRole
from app.models.user import User, UserRoleModel
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, TokenUser
from app.security.jwt import create_access_token
from app.security.passwords import hash_password, verify_password


class AuthenticationError(Exception):
    pass


class RegistrationError(Exception):
    pass


class AuthService:
    @staticmethod
    def register(db: Session, payload: RegisterRequest) -> TokenResponse:
        existing = db.scalar(select(User).where(User.email == payload.email.lower()))
        if existing:
            raise RegistrationError("Email already registered")

        user = User(
            email=payload.email.lower(),
            password_hash=hash_password(payload.password),
            first_name=payload.first_name,
            last_name=payload.last_name,
        )
        db.add(user)
        db.flush()

        role = UserRole.SUPPLIER if payload.company_type == "SUPPLIER" else UserRole.CUSTOMER
        db.add(UserRoleModel(user_id=user.id, role=role.value))

        company = Company(
            company_type=payload.company_type.value,
            name=payload.company_name,
        )
        db.add(company)
        db.flush()

        db.add(CompanyMember(company_id=company.id, user_id=user.id, is_primary_contact=True))
        db.commit()
        db.refresh(user)

        roles = [role.value]
        access_token = create_access_token(subject=user.id, roles=roles)

        return TokenResponse(
            access_token=access_token,
            refresh_token=access_token,
            user=TokenUser(id=user.id, email=user.email, roles=roles),
        )

    @staticmethod
    def login(db: Session, payload: LoginRequest) -> TokenResponse:
        user = db.scalar(select(User).where(User.email == payload.email.lower()))
        if user is None or not verify_password(payload.password, user.password_hash):
            raise AuthenticationError("Invalid credentials")

        roles = [role.role for role in user.roles]
        access_token = create_access_token(subject=user.id, roles=roles)

        return TokenResponse(
            access_token=access_token,
            refresh_token=access_token,
            user=TokenUser(id=user.id, email=user.email, roles=roles),
        )
