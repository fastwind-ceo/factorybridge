# STEP 006 — File Storage & RFQ Attachments Report

## Status

Completed.

## Implemented

- RFQ file upload endpoint: `POST /api/v1/files/rfqs/{rfq_id}`.
- RFQ file list endpoint: `GET /api/v1/files/rfqs/{rfq_id}`.
- Signed download URL endpoint: `GET /api/v1/files/{file_id}/download-url`.
- Token-protected download endpoint: `GET /api/v1/files/{file_id}/download`.
- Local storage backend for development/MVP.
- File metadata persisted in `rfq_files`.
- SHA-256 checksum generation.
- File extension validation.
- Upload size guard.
- RBAC-based RFQ file access for customer/operator/admin.
- Audit events:
  - `FILE_UPLOADED`
  - `FILE_DOWNLOAD_URL_CREATED`
  - `FILE_DOWNLOADED`
- File smoke script: `scripts/smoke_files.py`.

## Security Notes

- Files are not served directly from storage.
- Downloads require short-lived signed tokens.
- Customers can access only files for their own RFQs.
- Supplier file access is intentionally deferred until Tender Invitations/NDA step.

## Verification

Executed:

```bash
cd backend
pytest -q
```

Result:

```text
16 passed
```

Executed:

```bash
PYTHONPATH=backend python3 scripts/smoke_files.py
```

Result:

```text
STEP 006 file storage smoke test passed
```

## Next Step

STEP 007 — AI Review Layer: completeness check, missing fields, process classification, supplier brief and basic risk flags.
