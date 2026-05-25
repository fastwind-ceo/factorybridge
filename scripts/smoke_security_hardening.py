"""STEP 017 smoke checks: security docs and backend tests are present."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
required = [
    root / "backend/app/tests/test_security_hardening.py",
    root / "docs/STEP_017_TESTING_SECURITY_HARDENING_REPORT.md",
    root / "docs/SECURITY_READINESS_MATRIX.md",
    root / "docs/PRODUCTION_READINESS_CHECKLIST.md",
]
missing = [str(path.relative_to(root)) for path in required if not path.exists()]
if missing:
    raise SystemExit(f"Missing STEP 017 artifacts: {missing}")
print("STEP 017 security hardening smoke test passed")
