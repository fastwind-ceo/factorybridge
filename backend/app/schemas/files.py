from pydantic import BaseModel


class RFQFileRead(BaseModel):
    id: str
    rfq_id: str
    uploaded_by_user_id: str
    file_name: str
    file_type: str | None = None
    mime_type: str | None = None
    file_size: int | None = None
    storage_bucket: str | None = None
    storage_key: str
    file_category: str | None = None
    access_level: str
    checksum: str | None = None
    created_at: str


class DownloadURLRead(BaseModel):
    file_id: str
    download_url: str
    expires_in_minutes: int
