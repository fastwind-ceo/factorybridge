from app.db.base import Base
from app.models import Company, RFQ, SupplierProfile, User  # noqa: F401


def test_foundation_tables_registered():
    required = {
        "users",
        "user_roles",
        "companies",
        "company_members",
        "supplier_profiles",
        "supplier_capabilities",
        "rfqs",
        "rfq_technical_specs",
        "rfq_files",
        "rfq_ai_reviews",
        "rfq_logistics_specs",
        "rfq_commercial_specs",
        "rfq_status_history",
        "audit_logs",
        "notifications",
    }
    assert required.issubset(set(Base.metadata.tables.keys()))
