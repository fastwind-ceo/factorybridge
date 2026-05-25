# STEP 005 — RFQ Engine

## Goal
Implement the core RFQ engine for FactoryBridge: RFQ lifecycle, specs, status transitions, access rules, dictionaries and tests.

## Implemented
- RFQ CRUD endpoints.
- Customer-owned RFQ visibility.
- Operator/admin RFQ list and status control.
- RFQ technical specs upsert.
- RFQ logistics specs upsert.
- RFQ commercial specs upsert.
- RFQ status history.
- RFQ dictionaries endpoint.
- Audit logging for RFQ actions.
- Tests for customer flow, operator status change, access isolation and dictionaries.

## API added
- `POST /api/v1/rfqs`
- `GET /api/v1/rfqs/my`
- `GET /api/v1/rfqs`
- `GET /api/v1/rfqs/{rfq_id}`
- `PATCH /api/v1/rfqs/{rfq_id}`
- `POST /api/v1/rfqs/{rfq_id}/submit`
- `POST /api/v1/rfqs/{rfq_id}/status`
- `PUT /api/v1/rfqs/{rfq_id}/technical-specs`
- `PUT /api/v1/rfqs/{rfq_id}/logistics-specs`
- `PUT /api/v1/rfqs/{rfq_id}/commercial-specs`
- `GET /api/v1/rfqs/dictionaries`

## Verification
- `PYTHONPATH=backend pytest -q backend/app/tests`
- Result: `13 passed`
- `PYTHONPATH=backend python scripts/smoke_rfq.py`
- Result: `STEP 005 RFQ smoke passed`

## Notes
File upload is still planned for STEP 006. RFQ file model exists from the foundation, but storage and signed access will be implemented in the next step.
