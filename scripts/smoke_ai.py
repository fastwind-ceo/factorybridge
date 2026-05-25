from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from uuid import uuid4

from fastapi.testclient import TestClient

from app.db.init_db import init_db
from app.main import app


def main() -> None:
    init_db()
    client = TestClient(app)
    email = f"smoke.ai.{uuid4().hex[:8]}@example.com"
    password = "StrongPassword123"
    reg = client.post("/api/v1/auth/register", json={
        "email": email,
        "password": password,
        "company_name": "Smoke AI Customer",
        "company_type": "CUSTOMER",
    })
    assert reg.status_code == 200, reg.text
    token = client.post("/api/v1/auth/login", json={"email": email, "password": password}).json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    rfq = client.post("/api/v1/rfqs", json={
        "title": "Smoke CNC aluminum bracket",
        "description": "Manufacture aluminum brackets according to drawing.",
        "rfq_type": "BY_DRAWING",
        "category": "CNC_PARTS",
        "quantity": 100,
        "unit": "PCS",
        "delivery_country": "Russia",
        "delivery_city": "Moscow",
    }, headers=headers)
    assert rfq.status_code == 200, rfq.text
    rfq_id = rfq.json()["data"]["id"]
    tech = client.put(f"/api/v1/rfqs/{rfq_id}/technical-specs", json={
        "material": "ALUMINUM",
        "material_grade": "6061-T6",
        "tolerances": "±0.05 mm",
        "drawing_available": True,
    }, headers=headers)
    assert tech.status_code == 200, tech.text
    submit = client.post(f"/api/v1/rfqs/{rfq_id}/submit", headers=headers)
    assert submit.status_code == 200, submit.text
    review = client.post(f"/api/v1/ai/rfqs/{rfq_id}/completeness-check", headers=headers)
    assert review.status_code == 200, review.text
    data = review.json()["data"]["review"]
    assert data["completeness_score"] >= 70
    assert data["supplier_brief_en"]
    assert data["suggested_process"] in {"CNC_MACHINING", "UNKNOWN"}
    print("STEP 007 AI review smoke passed")


if __name__ == "__main__":
    main()
