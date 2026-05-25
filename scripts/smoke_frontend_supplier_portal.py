from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"
required = [
    FRONTEND / "app" / "supplier" / "page.tsx",
    FRONTEND / "app" / "supplier" / "profile" / "page.tsx",
    FRONTEND / "app" / "supplier" / "rfqs" / "page.tsx",
    FRONTEND / "app" / "supplier" / "rfqs" / "[id]" / "page.tsx",
    FRONTEND / "app" / "supplier" / "quotes" / "page.tsx",
    FRONTEND / "components" / "SupplierShell.tsx",
    FRONTEND / "lib" / "supplierMockData.ts",
]
missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
if missing:
    raise SystemExit("Missing supplier portal files: " + ", ".join(missing))
checks = {
    "supplier dashboard": FRONTEND / "app" / "supplier" / "page.tsx",
    "manufacturing capability": FRONTEND / "app" / "supplier" / "profile" / "page.tsx",
    "invited manufacturing tenders": FRONTEND / "app" / "supplier" / "rfqs" / "page.tsx",
    "submit quotation": FRONTEND / "app" / "supplier" / "rfqs" / "[id]" / "page.tsx",
    "submitted supplier quotations": FRONTEND / "app" / "supplier" / "quotes" / "page.tsx",
}
for label, path in checks.items():
    text = path.read_text(encoding="utf-8").lower()
    if label not in text:
        raise SystemExit(f"Expected {label!r} content in {path}")
print("STEP 014 frontend supplier portal smoke test passed")
