from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

"""Smoke test for STEP 008 tender invitation flow."""
from uuid import uuid4

from fastapi.testclient import TestClient

from app.db.init_db import init_db
from app.main import app

client = TestClient(app)


def register(company_type: str, prefix: str):
    init_db()
    email = f"{prefix}.{uuid4().hex[:8]}@example.com"
    password = "StrongPassword123"
    reg = client.post("/api/v1/auth/register", json={
        "email": email,
        "password": password,
        "company_name": f"{prefix} Company",
        "company_type": company_type,
    })
    assert reg.status_code == 200, reg.text
    token = client.post("/api/v1/auth/login", json={"email": email, "password": password}).json()["data"]["access_token"]
    return reg.json()["data"], {"Authorization": f"Bearer {token}"}


def main() -> None:
    _, customer_headers = register("CUSTOMER", "smoke.customer.tender")
    supplier, supplier_headers = register("SUPPLIER", "smoke.supplier.tender")
    _, operator_headers = register("PLATFORM_OPERATOR", "smoke.operator.tender")

    rfq = client.post("/api/v1/rfqs", json={
        "title": "Smoke tender RFQ",
        "description": "Tender invitation smoke test.",
        "rfq_type": "BY_DRAWING",
        "category": "CNC_PARTS",
        "quantity": 25,
        "unit": "PCS",
    }, headers=customer_headers).json()["data"]

    status = client.post(f"/api/v1/rfqs/{rfq['id']}/status", json={"new_status": "APPROVED_FOR_TENDER"}, headers=operator_headers)
    assert status.status_code == 200, status.text

    invitation = client.post(f"/api/v1/tenders/rfqs/{rfq['id']}/invite", json={"supplier_company_ids": [supplier["company_id"]]}, headers=operator_headers)
    assert invitation.status_code == 200, invitation.text
    invitation_id = invitation.json()["data"]["items"][0]["id"]

    available = client.get("/api/v1/tenders/supplier/rfqs", headers=supplier_headers)
    assert available.status_code == 200, available.text
    assert any(item["rfq"]["id"] == rfq["id"] for item in available.json()["data"]["items"])

    accepted = client.post(f"/api/v1/tenders/invitations/{invitation_id}/accept", headers=supplier_headers)
    assert accepted.status_code == 200, accepted.text
    assert accepted.json()["data"]["status"] == "ACCEPTED"

    print("STEP 008 tender smoke test passed")


if __name__ == "__main__":
    main()
