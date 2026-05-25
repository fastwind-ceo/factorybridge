# STEP 004 — Company & Supplier Profiles

## Цель
Реализовать backend-модуль профилей китайских исполнителей и их производственных возможностей.

## Что реализовано
- API `/api/v1/suppliers/profile` для создания supplier profile.
- API `/api/v1/suppliers/{company_id}` для чтения/обновления supplier profile.
- API `/api/v1/suppliers/{company_id}/capabilities` для добавления производственных возможностей.
- API `/api/v1/suppliers` для operator/admin списка поставщиков с фильтрами по технологии и материалу.
- API `/api/v1/suppliers/{company_id}/verify` для operator/admin верификации поставщика.
- API `/api/v1/suppliers/dictionaries` для справочников технологий и материалов.
- RBAC: customer не может создавать supplier profile или смотреть operator supplier list.
- Audit log для supplier profile/capability/verification actions.

## Проверка
- Backend compile: PASS.
- Pytest: PASS.
- Supplier smoke flow: PASS.

## Следующий шаг
STEP 005 — RFQ Engine: создание заявок, technical/logistics/commercial specs, статусы и история.
