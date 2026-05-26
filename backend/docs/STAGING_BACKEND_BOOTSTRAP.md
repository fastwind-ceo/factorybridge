# FactoryBridge Backend Staging Bootstrap

## Purpose

This guide describes the first safe staging backend runtime for FactoryBridge.

The goal of this stage is not final production hardening. The goal is to make the existing FastAPI backend runnable on a staging server with a local SQLite database, demo users and verifiable API endpoints.

## Current mode

- Backend framework: FastAPI
- ORM: SQLAlchemy
- Default database: SQLite
- Production database path: PostgreSQL through `DATABASE_URL`
- API prefix: `/api/v1`
- OpenAPI docs: `/api/v1/docs`

## Staging initialization

Run these commands from the repository root on the server:

1. Enter backend directory.
2. Install Python dependencies from `requirements.txt`.
3. Run `python scripts/init_db.py`.
4. Start FastAPI with Uvicorn on port 8000.

## Demo users

The bootstrap script creates these staging accounts:

| Role | Email | Password |
|---|---|---|
| Customer | `customer@factorybridge.demo` | `FactoryBridge2026!` |
| Supplier | `supplier@factorybridge.demo` | `FactoryBridge2026!` |
| Operator | `operator@factorybridge.demo` | `FactoryBridge2026!` |
| Admin | `admin@factorybridge.demo` | `FactoryBridge2026!` |

## Verification checklist

After backend start, verify:

- Health endpoint responds.
- OpenAPI docs are available.
- Login returns an access token for demo users.
- `/auth/me` works with the returned token.
- RFQ dictionaries endpoint works for authenticated users.

## Staging notes

- SQLite is acceptable only for MVP/staging.
- PostgreSQL remains the planned production database.
- Demo passwords must not be used for production.
- `SECRET_KEY` must be replaced before public production usage.

## Next step

After this backend bootstrap is merged, the next stage is frontend-backend wiring:

- login form to `/auth/login`;
- role-aware navigation after login;
- RFQ create form to `/rfqs`;
- RFQ list page to `/rfqs/my`;
- dictionaries to `/rfqs/dictionaries`.
