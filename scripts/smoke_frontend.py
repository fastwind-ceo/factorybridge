from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"
required = [
    FRONTEND / "app" / "page.tsx",
    FRONTEND / "app" / "login" / "page.tsx",
    FRONTEND / "app" / "register" / "page.tsx",
    FRONTEND / "app" / "dashboard" / "page.tsx",
    FRONTEND / "app" / "supplier" / "page.tsx",
    FRONTEND / "app" / "admin" / "page.tsx",
    FRONTEND / "app" / "workflow" / "page.tsx",
]
missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
if missing:
    raise SystemExit("Missing frontend files: " + ", ".join(missing))

print("Frontend smoke check passed")
