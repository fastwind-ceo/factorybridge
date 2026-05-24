from fastapi import APIRouter
from sqlalchemy import text

from app.core.config import settings
from app.db.session import SessionLocal

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    database_status = "unknown"
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
        database_status = "ok"
    except Exception as exc:
        database_status = f"error: {exc.__class__.__name__}"

    return {
        "status": "ok" if database_status == "ok" else "degraded",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "database": database_status,
        "redis": "not_checked_in_step_002",
        "storage": "not_checked_in_step_002",
    }
