# STEP 005 Verification

## Checks performed

```bash
rm -f factorybridge_dev.db
PYTHONPATH=backend pytest -q backend/app/tests
```

Result:

```text
13 passed
```

Smoke test:

```bash
PYTHONPATH=backend python scripts/smoke_rfq.py
```

Result:

```text
STEP 005 RFQ smoke passed
```

## Verified scope
- RFQ creation.
- RFQ technical specs.
- RFQ logistics specs.
- RFQ commercial specs.
- RFQ submit flow.
- Operator RFQ list.
- Operator RFQ status change.
- Customer isolation: customer cannot view another customer's RFQ.
- Customer cannot perform operator status change.
