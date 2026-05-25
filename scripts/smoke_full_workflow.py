from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

"""End-to-end smoke test for STEP 016 Full Workflow Integration.
Run from repository root:
    PYTHONPATH=backend python scripts/smoke_full_workflow.py
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
    _, customer_headers = register("CUSTOMER", "smoke.customer.full")
    supplier, supplier_headers = register("SUPPLIER", "smoke.supplier.full")
    _, operator_headers = register("PLATFORM_OPERATOR", "smoke.operator.full")

    profile = client.post("/api/v1/suppliers/profile", json={"company_id": supplier["company_id"], "english_name": "Smoke CNC Supplier", "city": "Ningbo"}, headers=supplier_headers)
    assert profile.status_code == 200, profile.text
    capability = client.post(f"/api/v1/suppliers/{supplier['company_id']}/capabilities", json={"process": "CNC_MACHINING", "materials": ["ALUMINUM"], "min_order_quantity": 50}, headers=supplier_headers)
    assert capability.status_code == 200, capability.text

    rfq_resp = client.post("/api/v1/rfqs", json={
        "title": "Smoke full workflow bracket",
        "description": "End-to-end RFQ smoke test",
        "rfq_type": "BY_DRAWING",
        "category": "CNC_PARTS",
        "quantity": 100,
        "unit": "PCS",
        "delivery_country": "Russia",
        "delivery_city": "Moscow",
    }, headers=customer_headers)
    assert rfq_resp.status_code == 200, rfq_resp.text
    rfq = rfq_resp.json()["data"]

    tech = client.put(f"/api/v1/rfqs/{rfq['id']}/technical-specs", json={"suggested_process": "CNC_MACHINING", "material": "ALUMINUM", "drawing_available": True}, headers=customer_headers)
    assert tech.status_code == 200, tech.text
    assert client.post(f"/api/v1/rfqs/{rfq['id']}/submit", headers=customer_headers).status_code == 200
    assert client.post(f"/api/v1/ai/rfqs/{rfq['id']}/completeness-check", headers=operator_headers).status_code == 200
    assert client.post(f"/api/v1/rfqs/{rfq['id']}/status", json={"new_status": "APPROVED_FOR_TENDER"}, headers=operator_headers).status_code == 200

    invite = client.post(f"/api/v1/tenders/rfqs/{rfq['id']}/invite", json={"supplier_company_ids": [supplier["company_id"]]}, headers=operator_headers)
    assert invite.status_code == 200, invite.text
    invitation_id = invite.json()["data"]["items"][0]["id"]
    assert client.post(f"/api/v1/tenders/invitations/{invitation_id}/accept", headers=supplier_headers).status_code == 200

    quote_resp = client.post(f"/api/v1/quotes/rfqs/{rfq['id']}", json={"unit_price": 10.0, "quantity": 100, "currency": "USD", "lead_time_mass_days": 20}, headers=supplier_headers)
    assert quote_resp.status_code == 200, quote_resp.text
    quote = quote_resp.json()["data"]
    assert client.post(f"/api/v1/quotes/{quote['id']}/submit", headers=supplier_headers).status_code == 200

    landed = client.post(f"/api/v1/landed-costs/quotes/{quote['id']}", json={"quantity": 100, "factory_unit_price": 10, "international_freight": 100, "vat_rate": 20, "platform_fee_rate": 5, "margin_rate": 10}, headers=operator_headers)
    assert landed.status_code == 200, landed.text
    assert client.post(f"/api/v1/quotes/{quote['id']}/accept", headers=customer_headers).status_code == 200
    order = client.post(f"/api/v1/orders/from-quote/{quote['id']}", json={"landed_cost_id": landed.json()["data"]["id"]}, headers=operator_headers)
    assert order.status_code == 200, order.text
    assert order.json()["data"]["status"] == "CREATED"
    print("STEP 016 smoke full workflow OK")


if __name__ == "__main__":
    main()
