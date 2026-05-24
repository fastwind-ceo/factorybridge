# FactoryBridge by Fast Wind

AI-assisted industrial RFQ and manufacturing tender platform connecting customers with verified Chinese manufacturing suppliers.

## Current release

MVP version: `v0.20.0 GitHub CI/CD Ready`

## Core capabilities

- Customer RFQ intake and RFQ wizard
- Technical, commercial and logistics specification structure
- Supplier profiles and manufacturing capabilities
- Tender invitations and supplier quote flow
- AI-assisted RFQ completeness review and process classification
- Quote comparison and landed cost calculation
- Orders MVP workflow
- Notifications and audit trail
- Docker/Nginx production deployment layer
- GitHub CI/CD workflow templates

## Repository layout

```text
backend/       FastAPI backend
frontend/      Next.js frontend
infra/         Docker, Nginx, env and deployment files
docs/          Project, deployment and pilot documentation
scripts/       Smoke, release and GitHub helper scripts
demo_data/     Demo launch data and examples
projectcapsule/ ProjectCapsule and release evidence
```

## Status

`MVP_READY_FOR_PILOT`

## Next stage

Public test deployment on VPS with Docker Compose, Nginx and SSL.
