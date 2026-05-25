from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.schemas.common import APIResponse
from app.security.dependencies import get_current_user
from app.services.file_service import get_download_url, list_rfq_files, resolve_download, serialize_file, upload_rfq_file

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/rfqs/{rfq_id}", response_model=APIResponse)
def upload_for_rfq(
    rfq_id: str,
    file: UploadFile = File(...),
    file_category: str | None = Form(default=None),
    access_level: str = Form(default="PRIVATE"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    created = upload_rfq_file(db, user=current_user, rfq_id=rfq_id, upload=file, file_category=file_category, access_level=access_level)
    return APIResponse(data=serialize_file(created))


@router.get("/rfqs/{rfq_id}", response_model=APIResponse)
def list_for_rfq(rfq_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    files = list_rfq_files(db, user=current_user, rfq_id=rfq_id)
    return APIResponse(data={"items": [serialize_file(item) for item in files], "total": len(files)})


@router.get("/{file_id}/download-url", response_model=APIResponse)
def create_download_url(file_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    url = get_download_url(db, user=current_user, file_id=file_id)
    return APIResponse(data={"file_id": file_id, "download_url": url, "expires_in_minutes": settings.signed_url_expire_minutes})


@router.get("/{file_id}/download")
def download_file(file_id: str, token: str, db: Session = Depends(get_db)):
    file = resolve_download(db, file_id=file_id, token=token)
    path = Path(file.storage_key)
    if not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stored file not found")
    return FileResponse(path, filename=file.file_name, media_type=file.mime_type or "application/octet-stream")
