# STEP 008 — Tender Invitations

## Цель шага
Реализовать управляемый tender invitation flow: оператор/админ приглашает китайских поставщиков в конкретную RFQ, поставщик видит только свои приглашённые заявки, может принять или отклонить участие, а доступ проверяется через RBAC и invitation records.

## Что реализовано
- Модель `TenderInvitation`.
- Pydantic-схемы для приглашений.
- `tender_service.py` с бизнес-логикой:
  - приглашение поставщиков;
  - проверка supplier company;
  - защита от дублей активных приглашений;
  - список приглашений по RFQ для operator/admin;
  - список доступных RFQ для supplier;
  - supplier accept/decline;
  - audit events.
- API `/api/v1/tenders`:
  - `POST /rfqs/{rfq_id}/invite`;
  - `GET /rfqs/{rfq_id}/invitations`;
  - `GET /supplier/rfqs`;
  - `GET /supplier/rfqs/{rfq_id}`;
  - `POST /invitations/{invitation_id}/accept`;
  - `POST /invitations/{invitation_id}/decline`.
- Smoke test `scripts/smoke_tender.py`.
- Tests `test_tender_invitations.py`.

## Проверки
- Backend test suite: `23 passed`.
- Tender smoke test: passed.
- Проверено, что customer не может приглашать suppliers.
- Проверено, что supplier не видит uninvited RFQ.
- Проверено, что supplier видит invited RFQ.
- Проверено, что supplier может accept/decline invitation.

## Acceptance Criteria
- [x] Operator/admin can invite suppliers.
- [x] Supplier sees only invited RFQs.
- [x] Supplier cannot access uninvited RFQs.
- [x] Supplier can accept invitation.
- [x] Supplier can decline invitation.
- [x] Invitations are auditable.
- [x] RFQ can move from approved to published after invitations.

## Следующий шаг
STEP 009 — Quote Engine: supplier quote form/backend, submit quote, status, operator quote list, customer-safe comparison access.
