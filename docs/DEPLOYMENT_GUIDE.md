# FactoryBridge Deployment Guide

## Status

FactoryBridge MVP is prepared for pilot deployment.

## Target architecture

- Ubuntu VPS
- Docker Compose
- PostgreSQL
- Redis
- FastAPI backend
- Next.js frontend
- Nginx reverse proxy
- SSL certificate

## Deployment flow

1. Prepare VPS.
2. Install Docker and Compose plugin.
3. Clone repository.
4. Copy environment templates to real env files.
5. Fill production secrets.
6. Build and start services.
7. Run health checks.
8. Create demo users.
9. Open public URL.

## Required environment files

- `infra/env/backend.prod.env`
- `infra/env/frontend.prod.env`
- `infra/env/postgres.prod.env`

Never commit real production secrets to GitHub.

## Basic checks

- Backend health endpoint returns status ok.
- Frontend routes return HTTP 200.
- Registration, login and RFQ creation flows work.
- GitHub Actions CI is green.

## Next step

Connect VPS and configure GitHub Secrets for automated deployment.
