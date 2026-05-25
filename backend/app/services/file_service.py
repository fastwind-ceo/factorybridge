from __future__ import annotations

import hashlib
from datetime import datetime, timezone, timedelta, timezone
from pathlib import Path
from typing import BinaryIO
from urllib.parse import quote
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.enums import CompanyType, UserRole
from app.models.rfq import RFQ, RFQFile, TenderInvitation
from app.models.user import User
from app.security.jwt import decode_token, encode_token, TokenError
from app.services.audit_service import log_action
from app.services.auth_service import user_roles
from app.services.rfq_service import get_rfq_or_404, user_company_ids

ALLOWED_FILE_EXTENSIONS = {
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".png", ".jpg", ".jpeg", ".step", ".stp", ".iges", ".igs", ".dxf", ".dwg", ".zip", ".txt", ".csv"
}


def is_operator_or_admin(user: User) -> bool:
    roles = set(user_roles(user))
    return UserRole.ADMIN.value in roles or UserRole.OPERATOR.value in roles


def user_supplier_company_ids(user: User) -> list[str]:
    return [m.company_id for m in user.memberships if m.company.company_type == CompanyType.SUPPLIER.value]


ACTIVE_FILE_INVITATION_STATUSES = {"INVITED", "VIEWED", "ACCEPTED", "QUOTE_SUBMITTED"}
SUPPLIER_FILE_ACCESS_LEVELS = {"SUPPLIER_PREVIEW", "NDA_REQUIRED", "FULL_TENDER_ACCESS"}


def _supplier_invitation_for_rfq(user: User, rfq: RFQ) -> TenderInvitation | None:
    supplier_ids = user_supplier_company_ids(user)
    if not supplier_ids:
        return None
    # Use loaded relationship when available; fall back to DB query is not possible here without Session.
    for invitation in getattr(rfq, "tender_invitations", []):
        if invitation.supplier_company_id in supplier_ids and invitation.status in ACTIVE_FILE_INVITATION_STATUSES:
            return invitation
    return None


def can_access_rfq_file(user: User, rfq: RFQ, file: RFQFile | None = None) -> bool:
    if is_operator_or_admin(user):
        return True
    if rfq.customer_company_id in user_company_ids(user):
        return True

    invitation = _supplier_invitation_for_rfq(user, rfq)
    if not invitation:
        return False
    if file is None:
        # Supplier may list RFQ files only after invitation, but per-file access is filtered.
        return True

    access_level = file.access_level or "PRIVATE"
    if access_level == "SUPPLIER_PREVIEW":
        return True
    if access_level == "NDA_REQUIRED":
        return invitation.access_level in {"NDA_REQUIRED", "FULL_ACCESS"}
    if access_level == "FULL_TENDER_ACCESS":
        return invitation.access_level == "FULL_ACCESS"
    return False


def get_file_or_404(db: Session, file_id: str) -> RFQFile:
    file = db.get(RFQFile, file_id)
    if not file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    return file


def ensure_upload_allowed(upload: UploadFile) -> None:
    filename = upload.filename or ""
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_FILE_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"File type is not allowed: {extension or 'unknown'}")


def _rfq_storage_dir(rfq_id: str) -> Path:
    root = Path(settings.local_storage_path).resolve()
    target = root / "rfqs" / rfq_id
    target.mkdir(parents=True, exist_ok=True)
    return target


def _copy_and_hash(source: BinaryIO, destination: Path) -> tuple[int, str]:
    hasher = hashlib.sha256()
    total = 0
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    with destination.open("wb") as out:
        while True:
            chunk = source.read(1024 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > max_bytes:
                out.close()
                destination.unlink(missing_ok=True)
                raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File is too large")
            hasher.update(chunk)
            out.write(chunk)
    return total, hasher.hexdigest()


def upload_rfq_file(
    db: Session,
    *,
    user: User,
    rfq_id: str,
    upload: UploadFile,
    file_category: str | None,
    access_level: str,
) -> RFQFile:
    rfq = get_rfq_or_404(db, rfq_id)
    if not can_access_rfq_file(user, rfq):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="RFQ file upload denied")
    ensure_upload_allowed(upload)
    original_name = upload.filename or "uploaded_file"
    extension = Path(original_name).suffix.lower()
    storage_name = f"{uuid4().hex}{extension}"
    storage_dir = _rfq_storage_dir(rfq.id)
    destination = storage_dir / storage_name
    size, checksum = _copy_and_hash(upload.file, destination)
    file = RFQFile(
        rfq_id=rfq.id,
        uploaded_by_user_id=user.id,
        file_name=original_name,
        file_type=extension.lstrip("."),
        mime_type=upload.content_type,
        file_size=size,
        storage_bucket="local",
        storage_key=str(destination),
        file_category=file_category,
        access_level=access_level,
        checksum=checksum,
    )
    db.add(file)
    db.flush()
    log_action(db, actor_user_id=user.id, action="FILE_UPLOADED", object_type="RFQ_FILE", object_id=file.id, after_data={"rfq_id": rfq.id, "file_name": file.file_name, "size": size})
    db.commit()
    db.refresh(file)
    return file


def list_rfq_files(db: Session, *, user: User, rfq_id: str) -> list[RFQFile]:
    rfq = get_rfq_or_404(db, rfq_id)
    if not can_access_rfq_file(user, rfq):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="RFQ file access denied")
    visible_files = [file for file in rfq.files if can_access_rfq_file(user, rfq, file)]
    return sorted(visible_files, key=lambda f: f.created_at)


def create_download_token(file_id: str, user_id: str) -> str:
    now = datetime.now(timezone.utc)
    return encode_token({
        "sub": user_id,
        "type": "file_download",
        "file_id": file_id,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.signed_url_expire_minutes)).timestamp()),
    })


def get_download_url(db: Session, *, user: User, file_id: str) -> str:
    file = get_file_or_404(db, file_id)
    rfq = get_rfq_or_404(db, file.rfq_id)
    if not can_access_rfq_file(user, rfq, file):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="RFQ file download denied")
    token = create_download_token(file.id, user.id)
    safe_name = quote(file.file_name)
    log_action(db, actor_user_id=user.id, action="FILE_DOWNLOAD_URL_CREATED", object_type="RFQ_FILE", object_id=file.id, after_data={"rfq_id": rfq.id})
    db.commit()
    return f"/api/v1/files/{file.id}/download?token={token}&filename={safe_name}"


def resolve_download(db: Session, *, file_id: str, token: str) -> RFQFile:
    try:
        payload = decode_token(token)
    except TokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired file token") from exc
    if payload.get("type") != "file_download" or payload.get("file_id") != file_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="File token does not match requested file")
    file = get_file_or_404(db, file_id)
    log_action(db, actor_user_id=payload.get("sub"), action="FILE_DOWNLOADED", object_type="RFQ_FILE", object_id=file.id, after_data={"rfq_id": file.rfq_id})
    db.commit()
    return file


def serialize_file(file: RFQFile) -> dict:
    return {
        "id": file.id,
        "rfq_id": file.rfq_id,
        "uploaded_by_user_id": file.uploaded_by_user_id,
        "file_name": file.file_name,
        "file_type": file.file_type,
        "mime_type": file.mime_type,
        "file_size": int(file.file_size) if file.file_size is not None else None,
        "storage_bucket": file.storage_bucket,
        "storage_key": file.storage_key,
        "file_category": file.file_category,
        "access_level": file.access_level,
        "checksum": file.checksum,
        "created_at": file.created_at.isoformat(),
    }
