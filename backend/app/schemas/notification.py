from datetime import datetime

from pydantic import BaseModel


class NotificationOut(BaseModel):
    id: str
    user_id: str
    title: str
    message: str
    notification_type: str
    is_read: bool
    object_type: str | None = None
    object_id: str | None = None
    created_at: datetime
    read_at: datetime | None = None


class NotificationListOut(BaseModel):
    items: list[NotificationOut]
    unread_count: int
