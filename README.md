# FactoryBridge by Fast Wind — STEP 016

## Step title
Full Workflow Integration

## Result
This archive contains the FactoryBridge project updated through STEP 016.

Implemented in this step:

- end-to-end backend integration test covering customer → AI → operator → supplier → quote → landed cost → order;
- full workflow smoke script: `scripts/smoke_full_workflow.py`;
- operator-accessible audit API endpoint: `/api/v1/admin/audit/logs`;
- frontend workflow overview page: `/workflow`;
- frontend workflow smoke test: `scripts/smoke_frontend_full_workflow.py`;
- documentation and ProjectCapsule evidence updated;
- all backend and frontend functionality from STEP 001–015 preserved.

## Verification

Performed checks:

```bash
cd backend && PYTHONPATH=. pytest -q
PYTHONPATH=backend python scripts/smoke_full_workflow.py
PYTHONPATH=backend python scripts/smoke_frontend_full_workflow.py
```

Result:

```text
34 passed
STEP 016 smoke full workflow OK
STEP 016 smoke frontend workflow OK
```

## Next step
STEP 017 — Testing, Security & Hardening.

## STEP 018 Production Deployment

Production deployment assets are now included:

- `infra/docker-compose.prod.yml`
- `infra/nginx/factorybridge.prod.conf`
- `infra/env/*.example`
- `infra/scripts/deploy_prod.sh`
- `infra/scripts/backup_postgres.sh`
- `docs/DEPLOYMENT_GUIDE.md`

Run local structural verification:

```bash
python scripts/smoke_production_files.py
```

## GitHub CI/CD

Added GitHub-ready automation:

- `.github/workflows/ci.yml` — backend tests, frontend build, deployment file checks.
- `.github/workflows/deploy-vps.yml` — deploy to VPS over SSH.
- `scripts/github/server_bootstrap_ubuntu.sh` — prepares Ubuntu VPS.
- `scripts/github/deploy_from_git.sh` — deploy script executed on server.
- `docs/github/GITHUB_DEPLOYMENT_GUIDE.md` — GitHub deployment guide.
- `docs/github/GITHUB_SECRETS_TEMPLATE.md` — required secrets.
