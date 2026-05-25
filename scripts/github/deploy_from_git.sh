#!/usr/bin/env bash
set -euo pipefail
APP_DIR="${APP_DIR:-/opt/factorybridge}"
REPO="${REPO:?REPO is required}"
BRANCH="${BRANCH:-main}"
echo "[FactoryBridge] Deploying ${BRANCH} to ${APP_DIR}"
if [ ! -d "${APP_DIR}/.git" ]; then
  mkdir -p "${APP_DIR}"
  git clone --branch "${BRANCH}" "${REPO}" "${APP_DIR}"
else
  cd "${APP_DIR}"
  git fetch origin "${BRANCH}"
  git checkout "${BRANCH}"
  git reset --hard "origin/${BRANCH}"
fi
cd "${APP_DIR}"
if [ ! -f infra/env/backend.prod.env ] || [ ! -f infra/env/frontend.prod.env ] || [ ! -f infra/env/postgres.prod.env ]; then
  echo "Missing production env files in infra/env/. Copy .example files and fill secrets."
  exit 2
fi
docker compose -f infra/docker-compose.prod.yml up -d --build
docker compose -f infra/docker-compose.prod.yml exec -T backend alembic upgrade head
docker compose -f infra/docker-compose.prod.yml exec -T backend python -m app.db.seed || true
sleep 5
curl -fsS http://127.0.0.1:8000/api/v1/health
echo "[FactoryBridge] Deployment complete."
