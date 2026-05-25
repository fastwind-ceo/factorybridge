#!/usr/bin/env bash
set -euo pipefail
if [ $# -lt 2 ]; then
  echo "Usage: $0 domain email"
  exit 1
fi
DOMAIN="$1"
EMAIL="$2"
cd "$(dirname "$0")/.."
mkdir -p certbot/www certbot/conf

echo "[FactoryBridge] Temporarily use no-SSL nginx config for ACME challenge if needed."
echo "[FactoryBridge] Requesting Let's Encrypt certificate for $DOMAIN"
docker run --rm \
  -v "$(pwd)/certbot/conf:/etc/letsencrypt" \
  -v "$(pwd)/certbot/www:/var/www/certbot" \
  certbot/certbot certonly --webroot \
  --webroot-path=/var/www/certbot \
  --email "$EMAIL" --agree-tos --no-eff-email \
  -d "$DOMAIN"

echo "[FactoryBridge] Certificate issued. Update nginx/factorybridge.prod.conf domain paths if necessary and restart nginx."
