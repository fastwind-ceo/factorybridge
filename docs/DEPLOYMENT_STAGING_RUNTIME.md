# FactoryBridge Staging Runtime Deployment Checklist

## Purpose

This checklist is the controlled deployment path for the current FactoryBridge staging environment.

It covers two independent runtime layers:

1. Frontend staging update on port 3000.
2. Backend FastAPI staging launch on port 8000.

Do not treat a GitHub merge as a completed deployment. Deployment is complete only after runtime verification.

---

## Current staging targets

- Frontend URL: `http://45.90.34.200:3000`
- Backend URL: `http://45.90.34.200:8000`
- Frontend process manager: PM2
- Backend process manager for first launch: manual Uvicorn, then PM2/systemd later

---

## 1. Pull latest main

Run on VPS:

```bash
cd /root/factorybridge
git pull
```

Expected result:

- Repository updates to latest `main`.
- Latest frontend refactor and backend bootstrap files are present.

Verify:

```bash
git log --oneline -5
ls backend/scripts/init_db.py
ls backend/docs/STAGING_BACKEND_BOOTSTRAP.md
```

---

## 2. Frontend staging update

Run:

```bash
cd /root/factorybridge/frontend
npm install --no-audit --no-fund --legacy-peer-deps
npm run build
pm2 restart factorybridge
pm2 list
```

Expected result:

- `npm run build` succeeds.
- PM2 shows `factorybridge` online.
- `http://45.90.34.200:3000` opens.

Verify in browser:

- Home page opens.
- Public navigation is visible.
- `/customer` opens.
- `/supplier` opens.
- `/operator` opens.
- `/login` opens.
- `/register` opens.

---

## 3. Backend virtual environment

Run:

```bash
cd /root/factorybridge/backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Expected result:

- Virtual environment is created.
- Backend dependencies install successfully.

---

## 4. Backend database bootstrap

Run:

```bash
cd /root/factorybridge/backend
source .venv/bin/activate
python scripts/init_db.py
```

Expected result:

- SQLite database is created.
- Demo users are created idempotently.
- Script prints demo credentials.
- No `ModuleNotFoundError: app` error.

Demo password:

```text
FactoryBridge2026!
```

Demo users:

```text
customer@factorybridge.demo
supplier@factorybridge.demo
operator@factorybridge.demo
admin@factorybridge.demo
```

---

## 5. Backend first runtime launch

Run:

```bash
cd /root/factorybridge/backend
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Keep this terminal open for first runtime verification.

Expected result:

- Uvicorn starts without import errors.
- Backend listens on `0.0.0.0:8000`.

---

## 6. Backend API verification

Open in browser or check with curl:

```text
http://45.90.34.200:8000/api/v1/health
http://45.90.34.200:8000/api/v1/docs
```

Expected result:

- Health endpoint responds.
- OpenAPI docs open.

Login smoke test:

```bash
curl -X POST http://45.90.34.200:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"customer@factorybridge.demo","password":"FactoryBridge2026!"}'
```

Expected result:

- JSON response contains access token and refresh token.

---

## 7. Stop manual backend after verification

If backend was launched manually in terminal, stop with:

```text
CTRL + C
```

Then create a permanent PM2/systemd backend process in a later deployment step.

---

## 8. Success criteria

This deployment is successful only when all items are true:

- Frontend PM2 process is online.
- Frontend staging URL opens.
- New frontend navigation is visible.
- Backend dependencies install.
- `python scripts/init_db.py` runs successfully.
- Backend starts with Uvicorn.
- `/api/v1/health` responds.
- `/api/v1/docs` opens.
- Login returns token for demo user.

---

## 9. Known next step

After successful staging runtime verification, create/continue:

```text
FB-FE-002 — frontend-backend integration
```

Scope:

- login form to backend auth;
- token storage;
- `/auth/me` session check;
- RFQ create form to backend;
- RFQ list from backend;
- role-aware redirect after login.
