# FactoryBridge Pilot Launch Guide

## Purpose
This guide describes how to run the first controlled pilot of FactoryBridge by Fast Wind.

## Pilot Objective
Validate that the platform can process a real manufacturing request from customer RFQ to supplier quote, landed-cost calculation, and order creation.

## Recommended Pilot Scope
- 3–5 customer companies
- 10–20 verified or manually screened Chinese suppliers
- 5–10 RFQs
- 15–30 supplier invitations
- 5–15 submitted quotes
- 1–3 orders or simulated orders

## Pilot Categories
1. CNC machined parts
2. Casting parts
3. Plastic injection-molded parts
4. Rubber/PU parts
5. Special equipment/truck parts

## Pilot Roles
- Admin: platform owner
- Operator: RFQ moderation and tender control
- Customer: RFQ creator
- Supplier: quote submitter

## Recommended First Pilot Scenario
1. Admin creates operator account.
2. Customer registers and creates RFQ.
3. Customer uploads drawing/specification.
4. AI review is run.
5. Operator approves RFQ.
6. Operator invites 3 suppliers.
7. Supplier accepts invitation.
8. Supplier submits quote.
9. Operator creates landed cost calculation.
10. Operator accepts quote and creates order.
11. Team reviews audit log and notifications.

## Pilot Success Criteria
- At least 1 complete RFQ-to-order workflow is completed.
- No RBAC or file access violation occurs.
- Supplier cannot see competitor quote.
- Customer cannot access internal margin data.
- Operator can manage the full workflow.
- Final landed cost is visible to customer.

## Pilot Notes
At pilot stage, supplier onboarding and logistics data can be manually managed by Fast Wind operator. Full automation should be added after real workflow feedback.
