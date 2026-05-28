# FB-FE-002 Auth Integration Verification

## Scope

This checklist verifies the first real frontend-backend auth integration step.

## Backend contract

Register endpoint:

```text
POST /api/v1/auth/register
```

Payload:

```json
{
  "email": "user@example.com",
  "password": "password123",
  "company_name": "Example Company",
  "company_type": "CUSTOMER"
}
```

Login endpoint:

```text
POST /api/v1/auth/login
```

Payload:

```json
{
  "email": "customer@factorybridge.demo",
  "password": "FactoryBridge2026!"
}
```

## Frontend behavior

### Register page

- Role dropdown changes current onboarding role.
- Role cards update selected role instead of navigating away.
- Submit sends backend registration request.
- Tokens are saved to localStorage.
- Success redirects according to selected role:
  - customer -> `/customer`
  - supplier -> `/supplier`
  - operator -> `/operator`
- Backend errors are shown in the UI.

### Login page

- Preferred portal dropdown controls preferred login redirect.
- Demo buttons set demo email and portal role.
- Submit sends backend login request.
- Tokens are saved to localStorage.
- Backend roles remain the source of truth for redirect.
- Backend errors are shown in the UI.

## Staging verification

Frontend:

```text
http://45.90.34.200:3000/register
http://45.90.34.200:3000/login
```

Backend:

```text
http://45.90.34.200:8000/api/v1/health
http://45.90.34.200:8000/api/v1/docs
```

## Expected localStorage keys

```text
factorybridge.access_token
factorybridge.refresh_token
factorybridge.user
```

## Demo password

```text
FactoryBridge2026!
```

## Acceptance criteria

- Frontend build passes.
- CI passes.
- Register creates a backend user.
- Login works for demo accounts.
- Incorrect password shows visible UI error.
- Role dropdown and role cards no longer contradict each other.
- Staging verification succeeds after merge and deploy.
