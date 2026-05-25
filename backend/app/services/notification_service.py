from datetime import datetime, timezone, timezone
from typing import Iterable

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.company import CompanyMember
from app.models.notification import Notification
from app.models.user import User, UserRoleModel


def serialize_notification(notification: Notification) -> dict:
    return {
        "id": notification.id,
        "user_id": notification.user_id,
        "title": notification.title,
        "message": notification.message,
        "notification_type": notification.notification_type,
        "is_read": notification.is_read,
        "object_type": notification.object_type,
        "object_id": notification.object_id,
        "created_at": notification.created_at.isoformat(),
        "read_at": notification.read_at.isoformat() if notification.read_at else None,
    }


def create_notification(
    db: Session,
    *,
    user_id: str,
    title: str,
    message: str,
    notification_type: str,
    object_type: str | None = None,
    object_id: str | None = None,
) -> Notification:
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        notification_type=notification_type,
        object_type=object_type,
        object_id=object_id,
    )
    db.add(notification)
    return notification


def create_notifications(
    db: Session,
    *,
    user_ids: Iterable[str],
    title: str,
    message: str,
    notification_type: str,
    object_type: str | None = None,
    object_id: str | None = None,
) -> list[Notification]:
    created: list[Notification] = []
    for user_id in sorted(set(user_ids)):
        created.append(create_notification(
            db,
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            object_type=object_type,
            object_id=object_id,
        ))
    return created


def user_ids_for_company(db: Session, company_id: str) -> list[str]:
    return list(db.scalars(select(CompanyMember.user_id).where(CompanyMember.company_id == company_id)).all())


def user_ids_for_roles(db: Session, roles: Iterable[str]) -> list[str]:
    return list(db.scalars(select(UserRoleModel.user_id).where(UserRoleModel.role.in_(list(roles)))).all())


def notify_company(
    db: Session,
    *,
    company_id: str,
    title: str,
    message: str,
    notification_type: str,
    object_type: str | None = None,
    object_id: str | None = None,
) -> list[Notification]:
    return create_notifications(
        db,
        user_ids=user_ids_for_company(db, company_id),
        title=title,
        message=message,
        notification_type=notification_type,
        object_type=object_type,
        object_id=object_id,
    )


def notify_roles(
    db: Session,
    *,
    roles: Iterable[str],
    title: str,
    message: str,
    notification_type: str,
    object_type: str | None = None,
    object_id: str | None = None,
) -> list[Notification]:
    return create_notifications(
        db,
        user_ids=user_ids_for_roles(db, roles),
        title=title,
        message=message,
        notification_type=notification_type,
        object_type=object_type,
        object_id=object_id,
    )


def list_my_notifications(db: Session, user: User, *, unread_only: bool = False) -> tuple[list[Notification], int]:
    query = select(Notification).where(Notification.user_id == user.id)
    if unread_only:
        query = query.where(Notification.is_read.is_(False))
    items = list(db.scalars(query.order_by(Notification.created_at.desc())).all())
    unread_count = db.scalar(select(func.count(Notification.id)).where(Notification.user_id == user.id, Notification.is_read.is_(False))) or 0
    return items, int(unread_count)


def mark_notification_read(db: Session, user: User, notification_id: str) -> Notification:
    notification = db.get(Notification, notification_id)
    if not notification or notification.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    if not notification.is_read:
        notification.is_read = True
        notification.read_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(notification)
    return notification


def mark_all_notifications_read(db: Session, user: User) -> int:
    items, _ = list_my_notifications(db, user, unread_only=True)
    now = datetime.now(timezone.utc)
    for item in items:
        item.is_read = True
        item.read_at = now
    db.commit()
    return len(items)
