from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

"""Smoke test for STEP 012 Notifications & Audit Expansion.
Run from repository root:
    PYTHONPATH=backend python scripts/smoke_notifications.py
"""
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
    login = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert login.status_code == 200, login.text
    return reg.json()["data"], {"Authorization": f"Bearer {login.json()['data']['access_token']}"}


def main() -> None:
    _, operator_headers = register("PLATFORM_OPERATOR", "smoke.operator.notifications")
    _, customer_headers = register("CUSTOMER", "smoke.customer.notifications")

    rfq = client.post("/api/v1/rfqs", json={
        "title": "Smoke notifications RFQ",
        "description": "Notification smoke RFQ",
        "rfq_type": "BY_DRAWING",
        "category": "CNC_PARTS",
        "quantity": 10,
        "unit": "PCS",
    }, headers=customer_headers)
    assert rfq.status_code == 200, rfq.text
    rfq_id = rfq.json()["data"]["id"]
    submitted = client.post(f"/api/v1/rfqs/{rfq_id}/submit", headers=customer_headers)
    assert submitted.status_code == 200, submitted.text

    notifications = client.get("/api/v1/notifications/my", headers=operator_headers)
    assert notifications.status_code == 200, notifications.text
    items = notifications.json()["data"]["items"]
    match = next(item for item in items if item["notification_type"] == "RFQ_SUBMITTED" and item["object_id"] == rfq_id)
    read = client.post(f"/api/v1/notifications/{match['id']}/read", headers=operator_headers)
    assert read.status_code == 200, read.text
    assert read.json()["data"]["is_read"] is True
    print("STEP 012 notifications smoke passed")


if __name__ == "__main__":
    main()
