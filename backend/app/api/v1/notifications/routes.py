from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.common import APIResponse
from app.security.dependencies import get_current_user
from app.services.notification_service import (
    list_my_notifications,
    mark_all_notifications_read,
    mark_notification_read,
    serialize_notification,
)

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/my", response_model=APIResponse)
def my_notifications(
    unread_only: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, unread_count = list_my_notifications(db, current_user, unread_only=unread_only)
    return APIResponse(data={"items": [serialize_notification(item) for item in items], "unread_count": unread_count})


@router.post("/{notification_id}/read", response_model=APIResponse)
def read_notification(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = mark_notification_read(db, current_user, notification_id)
    return APIResponse(data=serialize_notification(item))


@router.post("/read-all", response_model=APIResponse)
def read_all_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    count = mark_all_notifications_read(db, current_user)
    return APIResponse(data={"marked_read": count})
