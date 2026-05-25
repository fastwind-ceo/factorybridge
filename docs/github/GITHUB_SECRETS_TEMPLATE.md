# FactoryBridge GitHub Secrets Template

Required GitHub Actions secrets:

```text
VPS_HOST=<server-ip>
VPS_USER=<ssh-user>
VPS_APP_DIR=/opt/factorybridge
VPS_SSH_KEY=<private-key-content>
```

Generate a deploy key:

```bash
ssh-keygen -t ed25519 -C "factorybridge-github-actions" -f factorybridge_github_actions
```

Add `.pub` content to VPS `~/.ssh/authorized_keys`; add private key content to `VPS_SSH_KEY`.
