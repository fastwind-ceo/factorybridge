# FactoryBridge Deployment Guide — STEP 018

## Goal

Deploy FactoryBridge as a production-ready web stack:

- Next.js frontend
- FastAPI backend
- PostgreSQL
- Redis
- Nginx reverse proxy
- HTTPS via Let's Encrypt
- protected local file storage volume for MVP
- backup/restore scripts

## Production prerequisites

Recommended MVP server:

- Ubuntu 22.04/24.04
- 4 vCPU
- 8 GB RAM
- 160+ GB SSD
- Docker + Docker Compose plugin
- domain pointed to server IP

Open firewall ports:

- 80
- 443
- 22

Do not expose:

- 5432 PostgreSQL
- 6379 Redis
- internal backend/frontend ports

## Prepare environment

From project root:

```bash
cd infra
cp env/backend.prod.env.example env/backend.prod.env
cp env/frontend.prod.env.example env/frontend.prod.env
cp env/postgres.prod.env.example env/postgres.prod.env
```

Edit all `CHANGE_ME` values.

Minimum required changes:

- production domain in `BACKEND_CORS_ORIGINS`
- production API URL in `NEXT_PUBLIC_API_URL`
- strong database password
- strong `SECRET_KEY`

## First non-SSL launch

For first server verification you may temporarily replace the mounted config in `docker-compose.prod.yml`:

```yaml
./nginx/factorybridge.no-ssl.conf:/etc/nginx/conf.d/default.conf:ro
```

Then run:

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

Check:

```bash
curl http://YOUR_DOMAIN/api/v1/health
```

## SSL setup

1. Make sure domain resolves to the server.
2. Use no-SSL nginx config for the ACME challenge or any existing webroot flow.
3. Run:

```bash
bash infra/scripts/init_ssl_certbot.sh factorybridge.example.com admin@example.com
```

4. Update `infra/nginx/factorybridge.prod.conf` certificate paths from `factorybridge.example.com` to the real domain.
5. Switch docker-compose back to `factorybridge.prod.conf`.
6. Restart:

```bash
docker compose -f infra/docker-compose.prod.yml up -d nginx
```

## Deploy

```bash
bash infra/scripts/deploy_prod.sh
```

## Database migrations

The deploy script attempts:

```bash
docker compose -f infra/docker-compose.prod.yml exec backend alembic upgrade head
```

If migrations are not yet used in a given step, the command is non-blocking. Later steps can make it strict.

## Backup

Create backup:

```bash
bash infra/scripts/backup_postgres.sh
```

Restore backup:

```bash
bash infra/scripts/restore_postgres.sh backups/factorybridge_YYYYMMDD_HHMMSS.sql.gz
```

## Production smoke checks

After deploy:

```bash
curl https://YOUR_DOMAIN/api/v1/health
python scripts/smoke_production_files.py
```

Manual UI checks:

1. Open public landing page.
2. Register a customer.
3. Register a supplier.
4. Login as operator/admin.
5. Create RFQ.
6. Run AI review.
7. Invite supplier.
8. Submit quote.
9. Create landed cost.
10. Create order.

## Rollback

1. Keep previous archive ZIP.
2. Backup current database.
3. Restore previous code directory.
4. Run previous compose stack.
5. Restore database if schema/data require rollback.

## Production hardening notes

MVP-ready protections included:

- HTTPS-ready Nginx
- internal-only database and Redis
- private backend storage volume
- RBAC in backend
- signed download URL logic
- audit logs
- security checklists

Future hardening:

- external S3-compatible object storage
- Sentry
- Prometheus/Grafana
- rate limiting
- WAF
- automated CI/CD
- 2FA
