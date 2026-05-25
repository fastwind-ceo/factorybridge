# STEP 003 — Auth & RBAC Foundation

## Цель шага
Реализовать базовую авторизацию и ролевую модель FactoryBridge для дальнейшего развития RFQ, Supplier и Admin контуров.

## Реализовано

### Backend
- Регистрация пользователя с одновременным созданием компании.
- Назначение роли по типу компании:
  - `CUSTOMER` → роль `CUSTOMER`;
  - `SUPPLIER` → роль `SUPPLIER`;
  - `PLATFORM_OPERATOR` → роль `OPERATOR`.
- Login endpoint.
- Access token и refresh token.
- `/api/v1/auth/me`.
- Защищённые зависимости:
  - `get_current_user`;
  - `require_roles`.
- Company API:
  - список моих компаний;
  - просмотр компании по правам;
  - обновление компании по правам.
- Admin API:
  - dashboard;
  - список пользователей;
  - назначение ролей.
- Password hashing через PBKDF2-HMAC-SHA256 без внешней зависимости.
- JWT-compatible HMAC token implementation без внешней зависимости.
- Seed script для admin пользователя.
- Audit log для registration, login, company creation, role assignment.

### Тесты
- Auth flow: регистрация → login → `/me` → companies.
- RBAC: customer не имеет доступа к admin dashboard.
- Supplier registration получает роль `SUPPLIER`.
- Healthcheck обновлён до версии STEP 003.

## Проверка

Выполнены команды:

```bash
cd backend
python -m compileall app
python -m pytest -q
PYTHONPATH=. python ../scripts/smoke_auth.py
```

Результат:

```text
5 passed
STEP 003 auth smoke passed
```

## Acceptance Criteria

| Критерий | Статус |
|---|---|
| Пользователь может зарегистрироваться | PASS |
| При регистрации создаётся компания | PASS |
| Customer получает роль CUSTOMER | PASS |
| Supplier получает роль SUPPLIER | PASS |
| Login возвращает access/refresh token | PASS |
| `/auth/me` возвращает пользователя, роли и компании | PASS |
| Customer не видит admin dashboard | PASS |
| Admin API защищён ролями | PASS |
| Audit log создаётся для ключевых действий | PASS |

## Ограничения шага
- Полноценная email verification не реализована, будет добавлена позже.
- Password reset не реализован, будет добавлен отдельным шагом.
- 2FA не входит в MVP.
- Токены реализованы self-contained HMAC, production secret должен быть задан через `.env`.

## Следующий шаг
STEP 004 — Company & Supplier Profiles: расширенный профиль поставщика, производственные возможности, материалы, технологии, supplier list для оператора.
