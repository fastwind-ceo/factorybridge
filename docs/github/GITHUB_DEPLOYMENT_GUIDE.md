# FactoryBridge GitHub Deployment Guide

## 1. Create repository
Create a private GitHub repository, for example `factorybridge`.

## 2. Push project
```bash
git init
git add .
git commit -m "FactoryBridge MVP GitHub-ready"
git branch -M main
git remote add origin https://github.com/<OWNER>/<REPO>.git
git push -u origin main
```

## 3. Prepare VPS
Requirements: Ubuntu 22.04/24.04, 2 vCPU, 4 GB RAM, 80 GB SSD minimum.

Run on the VPS:
```bash
sudo bash scripts/github/server_bootstrap_ubuntu.sh
```

## 4. Configure production env files on VPS
In `/opt/factorybridge/infra/env/`, create these from examples:
```text
backend.prod.env
frontend.prod.env
postgres.prod.env
```
Set domain, CORS, database password, secret key and object storage values.

## 5. Add GitHub Actions secrets
Repository → Settings → Secrets and variables → Actions:
```text
VPS_HOST=<server-ip>
VPS_USER=<ssh-user>
VPS_APP_DIR=/opt/factorybridge
VPS_SSH_KEY=<private-ssh-key-content>
```

## 6. Deploy
Use Actions → Deploy FactoryBridge to VPS → Run workflow, or push to `main`.

## 7. SSL
After DNS is pointed to the VPS:
```bash
sudo certbot --nginx -d your-domain.com
```

## 8. Manual fallback
```bash
cd /opt/factorybridge
git pull origin main
docker compose -f infra/docker-compose.prod.yml up -d --build
docker compose -f infra/docker-compose.prod.yml exec backend alembic upgrade head
docker compose -f infra/docker-compose.prod.yml exec backend python -m app.db.seed
curl http://127.0.0.1:8000/api/v1/health
```
