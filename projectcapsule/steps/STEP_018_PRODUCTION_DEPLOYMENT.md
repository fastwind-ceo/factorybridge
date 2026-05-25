# STEP 018 — Production Docker / Nginx / Deployment

Status: DONE

Artifacts:

- backend/Dockerfile.prod
- frontend/Dockerfile.prod
- infra/docker-compose.prod.yml
- infra/docker-compose.staging.yml
- infra/nginx/factorybridge.prod.conf
- infra/nginx/factorybridge.no-ssl.conf
- infra/env/*.example
- infra/scripts/deploy_prod.sh
- infra/scripts/backup_postgres.sh
- infra/scripts/restore_postgres.sh
- infra/scripts/init_ssl_certbot.sh
- docs/DEPLOYMENT_GUIDE.md
- docs/STEP_018_PRODUCTION_DEPLOYMENT_REPORT.md
- scripts/smoke_production_files.py

Verification:

- backend tests pass
- production deployment smoke passes
