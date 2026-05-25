from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"
required = [
    FRONTEND / "app" / "admin" / "page.tsx",
    FRONTEND / "app" / "admin" / "rfqs" / "page.tsx",
    FRONTEND / "app" / "admin" / "rfqs" / "[id]" / "page.tsx",
    FRONTEND / "app" / "admin" / "suppliers" / "page.tsx",
    FRONTEND / "app" / "admin" / "tenders" / "page.tsx",
    FRONTEND / "app" / "admin" / "quotes" / "page.tsx",
    FRONTEND / "app" / "admin" / "landed-costs" / "page.tsx",
    FRONTEND / "app" / "admin" / "audit" / "page.tsx",
    FRONTEND / "components" / "AdminShell.tsx",
    FRONTEND / "lib" / "adminMockData.ts",
]
missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
if missing:
    raise SystemExit("Missing admin/operator panel files: " + ", ".join(missing))
checks = {
    "admin / operator panel": FRONTEND / "app" / "admin" / "page.tsx",
    "rfq moderation queue": FRONTEND / "app" / "admin" / "rfqs" / "page.tsx",
    "supplier matching panel": FRONTEND / "app" / "admin" / "rfqs" / "[id]" / "page.tsx",
    "supplier verification": FRONTEND / "app" / "admin" / "suppliers" / "page.tsx",
    "tender control panel": FRONTEND / "app" / "admin" / "tenders" / "page.tsx",
    "quote review": FRONTEND / "app" / "admin" / "quotes" / "page.tsx",
    "landed cost builder": FRONTEND / "app" / "admin" / "landed-costs" / "page.tsx",
    "audit logs": FRONTEND / "app" / "admin" / "audit" / "page.tsx",
}
for label, path in checks.items():
    text = path.read_text(encoding="utf-8").lower()
    if label not in text:
        raise SystemExit(f"Expected {label!r} content in {path}")
print("STEP 015 frontend admin/operator panel smoke test passed")
