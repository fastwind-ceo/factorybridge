#!/usr/bin/env bash
set -euo pipefail
APP_USER="${APP_USER:-factorybridge}"
APP_DIR="${APP_DIR:-/opt/factorybridge}"
SSH_PORT="${SSH_PORT:-22}"
echo "[FactoryBridge] Updating OS packages..."
apt-get update -y
apt-get upgrade -y
echo "[FactoryBridge] Installing packages..."
apt-get install -y ca-certificates curl gnupg git ufw nginx certbot python3-certbot-nginx
if ! command -v docker >/dev/null 2>&1; then
  echo "[FactoryBridge] Installing Docker Engine..."
  install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  chmod a+r /etc/apt/keyrings/docker.gpg
  . /etc/os-release
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu ${VERSION_CODENAME} stable" > /etc/apt/sources.list.d/docker.list
  apt-get update -y
  apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
fi
if ! id "${APP_USER}" >/dev/null 2>&1; then
  useradd -m -s /bin/bash "${APP_USER}"
fi
usermod -aG docker "${APP_USER}"
mkdir -p "${APP_DIR}"
chown -R "${APP_USER}:${APP_USER}" "${APP_DIR}"
ufw allow "${SSH_PORT}/tcp"
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
echo "[FactoryBridge] Bootstrap complete."
