# STEP 008 Verification Evidence

## Commands executed

```bash
cd backend
/opt/pyvenv/bin/python -m pytest -q
PYTHONPATH=. /opt/pyvenv/bin/python ../scripts/smoke_tender.py
```

## Results

- Test suite: `23 passed`.
- Smoke test: `STEP 008 tender smoke test passed`.

## Verified scope

- TenderInvitation model registered in SQLAlchemy metadata.
- Tender invitation APIs mounted in FastAPI app.
- Operator/admin invitation workflow works.
- Supplier available RFQ list works.
- Supplier RFQ detail access works only when invited.
- Accept/decline workflow works.
- Customer invitation attempt returns forbidden.
