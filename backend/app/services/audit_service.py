from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def log_action(
    db: Session,
    *,
    actor_user_id: str | None,
    action: str,
    object_type: str,
    object_id: str | None = None,
    before_data: dict | None = None,
    after_data: dict | None = None,
) -> AuditLog:
    entry = AuditLog(
        actor_user_id=actor_user_id,
        action=action,
        object_type=object_type,
        object_id=object_id,
        before_data=before_data,
        after_data=after_data,
    )
    db.add(entry)
    return entry
