import os

from sqlalchemy import select

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.models.company import Company, CompanyMember
from app.models.enums import CompanyType, UserRole
from app.models.user import User, UserRoleModel
from app.security.passwords import hash_password


def seed_admin() -> None:
    init_db()
    email = os.getenv("FACTORYBRIDGE_ADMIN_EMAIL", "admin@factorybridge.local").strip().lower()
    password = os.getenv("FACTORYBRIDGE_ADMIN_PASSWORD", "AdminPassword123")
    with SessionLocal() as db:
        existing = db.scalar(select(User).where(User.email == email))
        if existing:
            return
        user = User(email=email, password_hash=hash_password(password), first_name="FactoryBridge", last_name="Admin")
        company = Company(company_type=CompanyType.PLATFORM_OPERATOR.value, name="FactoryBridge Operator")
        db.add_all([user, company])
        db.flush()
        db.add(CompanyMember(company_id=company.id, user_id=user.id, position="Administrator", is_primary_contact=True))
        db.add(UserRoleModel(user_id=user.id, role=UserRole.ADMIN.value))
        db.add(UserRoleModel(user_id=user.id, role=UserRole.OPERATOR.value))
        db.commit()
        print(f"Seeded admin user: {email}")


if __name__ == "__main__":
    seed_admin()
