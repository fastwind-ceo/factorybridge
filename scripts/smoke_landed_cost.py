from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

"""Smoke test for STEP 010 Landed Cost Calculator.
Run from repository root:
    PYTHONPATH=backend python scripts/smoke_landed_cost.py
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
    _, customer_headers = register("CUSTOMER", "smoke.customer.landed")
    supplier, supplier_headers = register("SUPPLIER", "smoke.supplier.landed")
    _, operator_headers = register("PLATFORM_OPERATOR", "smoke.operator.landed")

    rfq = client.post("/api/v1/rfqs", json={
        "title": "Smoke landed cost part",
        "description": "Landed cost smoke RFQ",
        "rfq_type": "BY_DRAWING",
        "category": "CNC_PARTS",
        "quantity": 100,
        "unit": "PCS",
        "delivery_country": "Russia",
        "delivery_city": "Moscow",
    }, headers=customer_headers).json()["data"]

    client.post(f"/api/v1/rfqs/{rfq['id']}/status", json={"new_status": "APPROVED_FOR_TENDER"}, headers=operator_headers)
    client.post(f"/api/v1/tenders/rfqs/{rfq['id']}/invite", json={"supplier_company_ids": [supplier["company_id"]]}, headers=operator_headers)
    quote = client.post(f"/api/v1/quotes/rfqs/{rfq['id']}", json={"unit_price": 12.5, "currency": "USD", "quantity": 100}, headers=supplier_headers).json()["data"]
    client.post(f"/api/v1/quotes/{quote['id']}/submit", headers=supplier_headers)

    landed = client.post(f"/api/v1/landed-costs/quotes/{quote['id']}", json={
        "quantity": 100,
        "international_freight": 250,
        "duty_rate": 5,
        "vat_rate": 20,
        "platform_fee_rate": 5,
        "margin_rate": 10,
    }, headers=operator_headers)
    assert landed.status_code == 200, landed.text
    data = landed.json()["data"]
    assert data["final_customer_unit_price"] > data["factory_unit_price"]
    print("STEP 010 landed cost smoke OK")


if __name__ == "__main__":
    main()
