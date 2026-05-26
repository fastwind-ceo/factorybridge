"""Initialize FactoryBridge staging database.

This script is intentionally small and safe for MVP/staging use:
- imports all SQLAlchemy models;
- creates missing tables;
- seeds demo users for customer, supplier and operator roles.

Usage from repository root:
    cd backend
    python scripts/init_db.py
"""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import select

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models import *  # noqa: F401,F403 - required so SQLAlchemy registers all models
from app.models.enums import CompanyType, UserRole
from app.models.user import User
from app.schemas.auth import RegisterRequest
from app.services.auth_service import ensure_role, register_user_with_company

DEMO_PASSWORD = "FactoryBridge2026!"

DEMO_USERS = [
    {
        "email": "customer@factorybridge.demo",
        "first_name": "Demo",
        "last_name": "Customer",
        "company_name": "Demo Customer LLC",
        "company_type": CompanyType.CUSTOMER,
        "role": UserRole.CUSTOMER,
    },
    {
        "email": "supplier@factorybridge.demo",
        "first_name": "Demo",
        "last_name": "Supplier",
        "company_name": "Demo Supplier Factory",
        "company_type": CompanyType.SUPPLIER,
        "role": UserRole.SUPPLIER,
    },
    {
        "email": "operator@factorybridge.demo",
        "first_name": "Demo",
        "last_name": "Operator",
        "company_name": "FactoryBridge Operations",
        "company_type": CompanyType.PLATFORM_OPERATOR,
        "role": UserRole.OPERATOR,
    },
    {
        "email": "admin@factorybridge.demo",
        "first_name": "Demo",
        "last_name": "Admin",
        "company_name": "FactoryBridge Admin",
        "company_type": CompanyType.PLATFORM_OPERATOR,
        "role": UserRole.ADMIN,
    },
]


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


def seed_demo_users() -> None:
    db = SessionLocal()
    try:
        for item in DEMO_USERS:
            existing = db.scalar(select(User).where(User.email == item["email"]))
            if existing:
                ensure_role(db, existing, item["role"].value)
                continue

            payload = RegisterRequest(
                email=item["email"],
                password=DEMO_PASSWORD,
                first_name=item["first_name"],
                last_name=item["last_name"],
                company_name=item["company_name"],
                company_type=item["company_type"],
            )
            user, _company = register_user_with_company(db, payload)
            ensure_role(db, user, item["role"].value)

        db.commit()
    finally:
        db.close()


def main() -> None:
    create_tables()
    seed_demo_users()
    print("FactoryBridge staging database initialized.")
    print("Demo password:", DEMO_PASSWORD)
    for item in DEMO_USERS:
        print(f"- {item['role'].value.lower()}: {item['email']}")


if __name__ == "__main__":
    main()
