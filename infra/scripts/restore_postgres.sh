#!/usr/bin/env bash
set -euo pipefail
if [ $# -ne 1 ]; then
  echo "Usage: $0 /path/to/backup.sql.gz"
  exit 1
fi
BACKUP="$1"
cd "$(dirname "$0")/.."
echo "[FactoryBridge] Restoring PostgreSQL backup: $BACKUP"
gunzip -c "$BACKUP" | docker compose -f docker-compose.prod.yml exec -T postgres sh -c 'psql -U "$POSTGRES_USER" "$POSTGRES_DB"'
echo "[FactoryBridge] Restore finished."
