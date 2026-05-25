from app.db.base import Base
from app.db.session import engine

# Import models so SQLAlchemy registers table metadata.
from app.models import audit_log, company, enums, landed_cost, notification, order, quote, rfq, supplier, user  # noqa: F401


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
