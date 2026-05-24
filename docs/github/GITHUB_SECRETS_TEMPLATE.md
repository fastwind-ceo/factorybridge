# GitHub Secrets Template

Configure the following repository secrets before enabling automated deployment.

## Required secrets

- `VPS_HOST`
- `VPS_USER`
- `VPS_SSH_KEY`
- `DEPLOY_PATH`
- `BACKEND_ENV`
- `FRONTEND_ENV`
- `POSTGRES_ENV`

## Notes

- Use a dedicated deployment SSH key.
- Never expose production secrets publicly.
- Prefer separate staging and production environments.
