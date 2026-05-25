# STEP 010 — Landed Cost Calculator

## Goal
Implement a working total landed cost calculation layer for FactoryBridge quotes.

## Implemented
- `LandedCost` SQLAlchemy model.
- `LandedCostItem` extension model.
- `LandedCostCreate` and `LandedCostUpdate` schemas.
- Landed cost service with deterministic calculation logic.
- Operator/admin-only calculation creation and update.
- Customer-safe landed cost views with internal margin/platform-fee/risk-reserve fields hidden.
- Supplier access denied to landed cost calculations.
- API endpoints under `/api/v1/landed-costs`.
- Tests for calculation, access control, customer-safe view, and update flow.
- Smoke script: `scripts/smoke_landed_cost.py`.

## Main Formula
Factory price and direct cost components are accumulated into customs base. Duty and VAT are calculated from configured rates. Platform fee, margin and risk reserve are calculated on final internal cost and added to customer-facing total price.

## Verification
- Backend test suite: `28 passed`.
- Landed cost smoke flow: passed.
- Import/metadata registration: passed through full test run.

## Acceptance
STEP 010 is complete when an operator can create a landed cost estimate from a supplier quote, customer can view the final delivered price safely, and supplier cannot access internal landed cost data.

Status: PASSED.
