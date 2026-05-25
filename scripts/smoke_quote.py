from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

"""Smoke test for STEP 009 Quote Engine.
Run from repository root:
    PYTHONPATH=backend python scripts/smoke_quote.py
"""
from uuid import uuid4

from fastapi.testclient import TestClient

from app.db.init_db import init_db
from app.main import app

client = TestClient(app)


def unique_email(prefix: str) -> str:
    return f"{prefix}.{uuid4().hex[:8]}@example.com"


def register(company_type: str, prefix: str):
    init_db()
    email = unique_email(prefix)
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
    _, customer_headers = register("CUSTOMER", "smoke.customer.quote")
    supplier, supplier_headers = register("SUPPLIER", "smoke.supplier.quote")
    _, operator_headers = register("PLATFORM_OPERATOR", "smoke.operator.quote")

    rfq_resp = client.post("/api/v1/rfqs", json={
        "title": "Smoke quote part",
        "description": "Quote smoke test RFQ",
        "rfq_type": "BY_DRAWING",
        "category": "CNC_PARTS",
        "quantity": 100,
        "unit": "PCS",
        "delivery_country": "Russia",
        "delivery_city": "Moscow",
    }, headers=customer_headers)
    assert rfq_resp.status_code == 200, rfq_resp.text
    rfq = rfq_resp.json()["data"]

    approved = client.post(f"/api/v1/rfqs/{rfq['id']}/status", json={"new_status": "APPROVED_FOR_TENDER", "comment": "Smoke approve"}, headers=operator_headers)
    assert approved.status_code == 200, approved.text

    invited = client.post(f"/api/v1/tenders/rfqs/{rfq['id']}/invite", json={"supplier_company_ids": [supplier["company_id"]]}, headers=operator_headers)
    assert invited.status_code == 200, invited.text

    quote_resp = client.post(f"/api/v1/quotes/rfqs/{rfq['id']}", json={"unit_price": 15.75, "currency": "USD", "lead_time_mass_days": 21}, headers=supplier_headers)
    assert quote_resp.status_code == 200, quote_resp.text
    quote = quote_resp.json()["data"]

    submitted = client.post(f"/api/v1/quotes/{quote['id']}/submit", headers=supplier_headers)
    assert submitted.status_code == 200, submitted.text
    assert submitted.json()["data"]["status"] == "SUBMITTED"

    comparison = client.get(f"/api/v1/quotes/rfqs/{rfq['id']}/customer-comparison", headers=customer_headers)
    assert comparison.status_code == 200, comparison.text
    assert comparison.json()["data"]["summary"]["quote_count"] >= 1

    print("STEP 009 smoke quote OK")


if __name__ == "__main__":
    main()
