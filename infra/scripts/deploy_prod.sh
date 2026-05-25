#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

echo "[FactoryBridge] Checking production env files..."
for f in env/backend.prod.env env/frontend.prod.env env/postgres.prod.env; do
  if [ ! -f "$f" ]; then
    echo "Missing $f. Copy from $f.example and fill secrets."
    exit 1
  fi
done

echo "[FactoryBridge] Building and starting production stack..."
docker compose -f docker-compose.prod.yml up -d --build

echo "[FactoryBridge] Applying database migrations..."
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head

echo "[FactoryBridge] Initializing database tables and seed admin..."
docker compose -f docker-compose.prod.yml exec backend python -m app.db.seed

echo "[FactoryBridge] Running production smoke test..."
python3 ../scripts/smoke_production_files.py

echo "[FactoryBridge] Deployment command finished. Check https://YOUR_DOMAIN and /api/v1/health."
