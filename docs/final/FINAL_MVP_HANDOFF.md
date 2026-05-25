# FactoryBridge Final MVP Handoff

## Project Status
MVP_READY_FOR_PILOT

## What is included
FactoryBridge MVP includes:
- Public frontend pages
- Customer portal
- Supplier portal
- Operator/Admin panel
- Auth and RBAC
- Company and supplier profiles
- RFQ engine
- File attachments
- AI review layer
- Tender invitations
- Quote engine
- Landed cost calculator
- Orders MVP
- Notifications
- Audit logs
- Production Docker/Nginx assets
- Deployment documentation
- Pilot launch package

## Main entry points
- Backend: `backend/app/main.py`
- Frontend: `frontend/app/page.tsx`
- Production compose: `infra/docker-compose.prod.yml`
- Dev compose: `infra/docker-compose.dev.yml`
- Deployment guide: `docs/DEPLOYMENT_GUIDE.md`
- Pilot guide: `docs/pilot/PILOT_LAUNCH_GUIDE.md`

## Local development start
```bash
cd infra
docker compose -f docker-compose.dev.yml up --build
```

## Backend tests
```bash
cd backend
pytest
```

## Production deployment
See `docs/DEPLOYMENT_GUIDE.md` and `docs/PRODUCTION_READINESS_CHECKLIST.md`.

## Important limitation
This archive is ready for deployment, but an actual public web launch requires server credentials, production domain, DNS, SSL issuance, environment secrets, and external object-storage/SMTP configuration if used.

## Recommended next action
Deploy to staging server, run smoke tests, onboard pilot suppliers and customers, then proceed to controlled pilot.
