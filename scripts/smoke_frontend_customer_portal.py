from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"
required = [
    FRONTEND / "app" / "page.tsx",
    FRONTEND / "app" / "login" / "page.tsx",
    FRONTEND / "app" / "register" / "page.tsx",
    FRONTEND / "app" / "dashboard" / "page.tsx",
    FRONTEND / "app" / "rfqs" / "page.tsx",
    FRONTEND / "app" / "rfqs" / "new" / "page.tsx",
    FRONTEND / "app" / "rfqs" / "[id]" / "page.tsx",
    FRONTEND / "app" / "quotes" / "page.tsx",
    FRONTEND / "app" / "landed-costs" / "page.tsx",
    FRONTEND / "app" / "notifications" / "page.tsx",
    FRONTEND / "components" / "AppShell.tsx",
    FRONTEND / "components" / "RFQTable.tsx",
    FRONTEND / "lib" / "api.ts",
]
missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
if missing:
    raise SystemExit("Missing frontend files: " + ", ".join(missing))

checks = {
    "RFQ wizard": FRONTEND / "app" / "rfqs" / "new" / "page.tsx",
    "quote comparison": FRONTEND / "app" / "rfqs" / "[id]" / "page.tsx",
    "landed cost": FRONTEND / "app" / "landed-costs" / "page.tsx",
    "notifications": FRONTEND / "app" / "notifications" / "page.tsx",
}
for label, path in checks.items():
    text = path.read_text(encoding="utf-8")
    if label.lower().split()[0] not in text.lower():
        raise SystemExit(f"Expected {label} content in {path}")
print("STEP 013 frontend customer portal smoke test passed")
