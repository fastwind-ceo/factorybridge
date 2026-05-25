# STEP 014 — Frontend Supplier Portal

## Goal
Implement the supplier-facing portal screens required for MVP supplier operations.

## Implemented
- Supplier dashboard at `/supplier`
- Supplier profile editor at `/supplier/profile`
- Manufacturing capabilities display
- Available invited RFQs page at `/supplier/rfqs`
- Supplier RFQ detail and quote submission page at `/supplier/rfqs/[id]`
- Supplier quotes history at `/supplier/quotes`
- Supplier-specific navigation shell
- Supplier mock data layer for frontend integration readiness
- Supplier portal smoke test script

## Verification
- `python scripts/smoke_frontend_supplier_portal.py` — passed
- `python scripts/smoke_frontend_customer_portal.py` — passed
- `cd backend && pytest -q` — 33 passed

## Notes
The supplier portal is currently static/mock-data driven, matching the frontend MVP pattern from STEP 013. Backend APIs for supplier profile, invitations and quotes already exist and will be integrated in a later full workflow integration step.

## Next Step
STEP 015 — Admin / Operator Panel.
