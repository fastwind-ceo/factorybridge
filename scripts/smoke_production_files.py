from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
required = [
    "infra/docker-compose.prod.yml",
    "infra/docker-compose.staging.yml",
    "infra/nginx/factorybridge.prod.conf",
    "infra/nginx/factorybridge.no-ssl.conf",
    "infra/env/backend.prod.env.example",
    "infra/env/frontend.prod.env.example",
    "infra/env/postgres.prod.env.example",
    "infra/scripts/deploy_prod.sh",
    "infra/scripts/backup_postgres.sh",
    "infra/scripts/restore_postgres.sh",
    "backend/Dockerfile.prod",
    "frontend/Dockerfile.prod",
    "docs/DEPLOYMENT_GUIDE.md",
    "docs/STEP_018_PRODUCTION_DEPLOYMENT_REPORT.md",
]
missing = [path for path in required if not (ROOT / path).exists()]
if missing:
    raise SystemExit(f"Missing production files: {missing}")
compose = (ROOT / "infra/docker-compose.prod.yml").read_text()
for service in ["postgres", "redis", "backend", "frontend", "nginx"]:
    if f"  {service}:" not in compose:
        raise SystemExit(f"Missing service in production compose: {service}")
nginx = (ROOT / "infra/nginx/factorybridge.prod.conf").read_text()
for needle in ["/api/v1/", "proxy_pass http://backend:8000", "proxy_pass http://frontend:3000", "client_max_body_size 200M"]:
    if needle not in nginx:
        raise SystemExit(f"Nginx production config missing: {needle}")
print("production deployment smoke: OK")
