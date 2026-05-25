#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
TS=$(date +%Y%m%d_%H%M%S)
mkdir -p ../backups
OUT="../backups/factorybridge_${TS}.sql.gz"
echo "[FactoryBridge] Creating PostgreSQL backup: $OUT"
docker compose -f docker-compose.prod.yml exec -T postgres sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' | gzip > "$OUT"
echo "[FactoryBridge] Backup created: $OUT"
