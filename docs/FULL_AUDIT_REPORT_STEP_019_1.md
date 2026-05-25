# FactoryBridge Full Audit Report

Version: `0.19.1-audit-fix`

## Scope

Independent re-check of the STEP 019 Final MVP package after the user requested full verification and testing.

Checked areas:

- archive extraction and package structure;
- backend compilation and regression tests;
- backend smoke scripts;
- frontend production build;
- frontend smoke scripts;
- production deployment file presence and YAML parse validation;
- release/package smoke test;
- security/access smoke tests;
- generated artifact hygiene.

## Findings and Fixes

### Finding 1 — Frontend production build failed on Next.js 15 dynamic route typing

Status: fixed.

Details:

- `app/admin/rfqs/[id]/page.tsx` used sync `params` typing.
- Next.js 15 expected `params` as a Promise in this build context.

Fix:

- Converted page to async function and awaited `params`.

### Finding 2 — Frontend production build failed on wrong prop name

Status: fixed.

Details:

- `MetricCard` expects `hint`, while admin dashboard passed `note`.

Fix:

- Replaced `note={m.note}` with `hint={m.note}`.

### Finding 3 — Smoke scripts failed when launched from project root

Status: fixed.

Details:

- Backend smoke scripts imported `app.*` without adding `backend/` to `sys.path`.
- They worked only when launched from the backend folder or specific environment.

Fix:

- Added robust root detection and backend path injection to backend smoke scripts.

### Finding 4 — Deployment script did not explicitly initialize DB tables/admin after migrations

Status: fixed.

Details:

- Existing Alembic migration is a foundation marker.
- `app.db.seed` contains `init_db()` and admin seeding.

Fix:

- Updated `infra/scripts/deploy_prod.sh` to run:
  - `alembic upgrade head`
  - `python -m app.db.seed`

### Finding 5 — Archive contained generated local artifacts

Status: fixed in refreshed archive.

Removed before refreshed packaging:

- `__pycache__`
- `*.pyc`
- local SQLite `.db` files
- `.pytest_cache`
- `.next`
- `node_modules`

Kept:

- source code;
- tests;
- scripts;
- package metadata;
- package-lock if present;
- docs;
- infra files.

## Test Results

### Backend

Command:

```bash
cd backend && python -m pytest -q
```

Result:

```text
36 passed
```

Notes:

- No failed tests.
- Warnings are deprecation warnings around `datetime.utcnow()` and pytest-asyncio fixture defaults; these are not blocking for MVP, but should be cleaned in future hardening.

### Python compilation

Command:

```bash
cd backend && python -m compileall -q app
```

Result: PASS.

### Frontend production build

Command:

```bash
cd frontend && npm run build
```

Result: PASS.

Built routes include:

- public landing;
- customer dashboard/RFQ pages;
- supplier portal;
- admin/operator pages;
- dynamic RFQ detail pages.

### Smoke Scripts

Executed and passed:

- `smoke_backend.py`
- `smoke_auth.py`
- `smoke_supplier.py`
- `smoke_rfq.py`
- `smoke_files.py`
- `smoke_ai.py`
- `smoke_tender.py`
- `smoke_quote.py`
- `smoke_landed_cost.py`
- `smoke_notifications.py`
- `smoke_full_workflow.py`
- `smoke_security_hardening.py`
- `smoke_frontend_customer_portal.py`
- `smoke_frontend_supplier_portal.py`
- `smoke_frontend_admin_operator_panel.py`
- `smoke_frontend_full_workflow.py`
- `smoke_production_files.py`
- `smoke_step019_release_package.py`

### Docker/YAML Validation

Docker CLI was not available in the current execution environment, so real container startup could not be executed here.

Alternative performed:

- YAML parse validation with Python/PyYAML;
- service list validation for dev/staging/prod compose files;
- production file presence smoke test.

Validated compose service sets:

- dev: `backend`, `frontend`, `minio`, `postgres`, `redis`
- staging: `backend`, `frontend`, `postgres`, `redis`
- prod: `backend`, `frontend`, `nginx`, `postgres`, `redis`

## Final Audit Status

`PASS_WITH_ENV_LIMITATION`

The codebase, tests, frontend build, workflow scripts and package structure pass local verification.

The only limitation: real Docker container startup was not possible in this sandbox because Docker is not installed in the environment. The project includes production Docker/Nginx deployment files and deployment scripts, and those files passed static/package validation.

## Recommended Next Action

Use the refreshed audit-fixed archive for the next step. On a real server, execute:

```bash
cd infra
cp env/backend.prod.env.example env/backend.prod.env
cp env/frontend.prod.env.example env/frontend.prod.env
cp env/postgres.prod.env.example env/postgres.prod.env
# fill secrets and domain
bash scripts/deploy_prod.sh
```

Then open:

```text
https://YOUR_DOMAIN/api/v1/health
https://YOUR_DOMAIN
```
