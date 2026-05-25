# STEP 017 — Testing, Security & Hardening Report

## Goal
Strengthen FactoryBridge before production packaging by closing access-control gaps, expanding regression coverage, and documenting launch readiness requirements.

## Implemented changes

### Backend hardening
- Added supplier invitation-based RFQ visibility to `/api/v1/rfqs/{rfq_id}`.
- Added supplier file visibility rules by RFQ file `access_level`:
  - `PRIVATE`, `CUSTOMER_ONLY`, `OPERATOR_ONLY`: no supplier access.
  - `SUPPLIER_PREVIEW`: invited supplier access.
  - `NDA_REQUIRED`: invited supplier access only when invitation access level is `NDA_REQUIRED` or `FULL_ACCESS`.
  - `FULL_TENDER_ACCESS`: invited supplier access only when invitation access level is `FULL_ACCESS`.
- Direct download-url requests now enforce the same per-file access logic.
- RFQ relationship now includes tender invitations for consistent access checks.

### Test coverage
- Added `test_security_hardening.py` covering:
  - uninvited supplier RFQ denial;
  - invited supplier RFQ access;
  - supplier file access by access level;
  - direct file ID protection;
  - customer-safe quote comparison hiding internal quote fields.

### Operational artifacts
- Added production readiness checklist.
- Added security readiness matrix.
- Added STEP 017 smoke script.

## Verification

Command executed:

```bash
cd backend
pytest -q
```

Result:

```text
36 passed
```

Additional smoke check:

```bash
python scripts/smoke_security_hardening.py
```

Expected result:

```text
STEP 017 security hardening smoke test passed
```

## Acceptance status

| Area | Result |
|---|---|
| Backend regression tests | PASS |
| RFQ access hardening | PASS |
| File access hardening | PASS |
| Customer-safe quote comparison | PASS |
| Security docs | PASS |
| Smoke script | PASS |

## Known notes
- AI remains rule-based/LLM-ready in MVP to keep local operation deterministic.
- Full NDA document execution and watermarking are planned for a later enhancement step.
- External penetration testing is recommended before high-volume production use.
