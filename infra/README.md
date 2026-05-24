# FactoryBridge Infrastructure Layer

This directory contains deployment and runtime infrastructure templates.

## Included

- Production environment examples
- Docker Compose placeholders
- Nginx placeholders
- Deployment guides
- GitHub Actions deployment workflow skeleton

## Recommended runtime stack

- Ubuntu 22.04 or 24.04
- Docker Engine
- Docker Compose plugin
- PostgreSQL
- Redis
- Nginx
- Certbot SSL

## Deployment flow

1. Prepare VPS
2. Configure DNS
3. Configure environment files
4. Build containers
5. Run smoke checks
6. Enable SSL
7. Launch pilot environment
