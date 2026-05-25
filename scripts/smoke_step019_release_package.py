from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
required = [
    "backend/app/main.py",
    "frontend/app/page.tsx",
    "infra/docker-compose.prod.yml",
    "infra/nginx/factorybridge.conf",
    "docs/DEPLOYMENT_GUIDE.md",
    "docs/pilot/PILOT_LAUNCH_GUIDE.md",
    "docs/final/FINAL_MVP_HANDOFF.md",
    "projectcapsule/MANIFEST.json",
]
missing = [p for p in required if not (ROOT / p).exists()]
if missing:
    raise SystemExit(f"Missing required release files: {missing}")
print("STEP 019 release package smoke test passed")
