"""Static smoke check for STEP 016 full workflow page."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
page = root / "frontend" / "app" / "workflow" / "page.tsx"
text = page.read_text(encoding="utf-8")
required = [
    "Full Workflow Integration",
    "Create RFQ",
    "Review RFQ",
    "Approve & invite",
    "Submit quote",
    "Landed cost",
    "Accept quote",
    "Create order",
]
missing = [item for item in required if item not in text]
assert not missing, f"Missing workflow UI markers: {missing}"
print("STEP 016 smoke frontend workflow OK")
