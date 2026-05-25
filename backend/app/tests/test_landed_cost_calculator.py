from uuid import uuid4

from fastapi.testclient import TestClient

from app.db.init_db import init_db
from app.main import app

client = TestClient(app)


def unique_email(prefix: str) -> str:
    return f"{prefix}.{uuid4().hex[:10]}@example.com"


def register_and_login(company_type: str, prefix: str):
    init_db()
    email = unique_email(prefix)
    password = "StrongPassword123"
    reg = client.post("/api/v1/auth/register", json={"email": email, "password": password, "company_name": f"{prefix} Company", "company_type": company_type})
    assert reg.status_code == 200, reg.text
    token = client.post("/api/v1/auth/login", json={"email": email, "password": password}).json()["data"]["access_token"]
    return reg.json()["data"], {"Authorization": f"Bearer {token}"}


def create_rfq(headers):
    response = client.post("/api/v1/rfqs", json={
        "title": "Landed cost CNC part",
        "description": "Part for landed cost tests.",
        "rfq_type": "BY_DRAWING",
        "category": "CNC_PARTS",
        "quantity": 500,
        "unit": "PCS",
        "delivery_country": "Russia",
        "delivery_city": "Moscow",
    }, headers=headers)
    assert response.status_code == 200, response.text
    return response.json()["data"]


def prepare_submitted_quote():
    _customer_reg, customer_headers = register_and_login("CUSTOMER", "customer.landed.step010")
    supplier_reg, supplier_headers = register_and_login("SUPPLIER", "supplier.landed.step010")
    _operator_reg, operator_headers = register_and_login("PLATFORM_OPERATOR", "operator.landed.step010")
    rfq = create_rfq(customer_headers)
    status_resp = client.post(f"/api/v1/rfqs/{rfq['id']}/status", json={"new_status": "APPROVED_FOR_TENDER", "comment": "Ready"}, headers=operator_headers)
    assert status_resp.status_code == 200, status_resp.text
    invite = client.post(f"/api/v1/tenders/rfqs/{rfq['id']}/invite", json={"supplier_company_ids": [supplier_reg["company_id"]]}, headers=operator_headers)
    assert invite.status_code == 200, invite.text
    quote_resp = client.post(f"/api/v1/quotes/rfqs/{rfq['id']}", json={
        "unit_price": 12.5,
        "currency": "USD",
        "quantity": 500,
        "moq": 100,
        "tooling_cost": 0,
        "sample_cost": 80,
        "packaging_cost": 50,
        "lead_time_mass_days": 25,
        "incoterms": "EXW",
    }, headers=supplier_headers)
    assert quote_resp.status_code == 200, quote_resp.text
    quote = quote_resp.json()["data"]
    submit = client.post(f"/api/v1/quotes/{quote['id']}/submit", headers=supplier_headers)
    assert submit.status_code == 200, submit.text
    return rfq, quote, customer_headers, supplier_headers, operator_headers


def test_operator_creates_landed_cost_and_customer_sees_safe_view():
    rfq, quote, customer_headers, supplier_headers, operator_headers = prepare_submitted_quote()
    denied = client.post(f"/api/v1/landed-costs/quotes/{quote['id']}", json={"china_local_logistics": 200}, headers=customer_headers)
    assert denied.status_code == 403

    create = client.post(f"/api/v1/landed-costs/quotes/{quote['id']}", json={
        "calculation_name": "DDP Moscow estimate",
        "currency": "USD",
        "quantity": 500,
        "factory_unit_price": 12.5,
        "tooling_cost": 0,
        "sample_cost": 80,
        "packaging_cost": 50,
        "china_local_logistics": 200,
        "export_handling_cost": 150,
        "international_freight": 900,
        "insurance_cost": 50,
        "customs_clearance_cost": 250,
        "duty_rate": 5,
        "vat_rate": 20,
        "certification_cost": 0,
        "local_delivery_cost": 180,
        "platform_fee_rate": 5,
        "margin_rate": 15,
        "risk_reserve_rate": 3,
        "notes": "Preliminary calculation",
    }, headers=operator_headers)
    assert create.status_code == 200, create.text
    data = create.json()["data"]
    assert data["factory_total_price"] == 6250.0
    assert data["duty_amount"] > 0
    assert data["vat_amount"] > 0
    assert data["final_customer_total_price"] > data["final_total_cost"]
    assert data["final_customer_unit_price"] > data["factory_unit_price"]

    listed = client.get(f"/api/v1/landed-costs/rfqs/{rfq['id']}/list", headers=customer_headers)
    assert listed.status_code == 200, listed.text
    safe_item = listed.json()["data"]["items"][0]
    assert "margin_rate" not in safe_item
    assert "platform_fee_amount" not in safe_item
    assert safe_item["final_customer_total_price"] == data["final_customer_total_price"]

    supplier_view = client.get(f"/api/v1/landed-costs/{data['id']}", headers=supplier_headers)
    assert supplier_view.status_code == 403


def test_operator_can_update_landed_cost():
    _rfq, quote, _customer_headers, _supplier_headers, operator_headers = prepare_submitted_quote()
    create = client.post(f"/api/v1/landed-costs/quotes/{quote['id']}", json={"international_freight": 100, "vat_rate": 20}, headers=operator_headers)
    assert create.status_code == 200, create.text
    landed_cost_id = create.json()["data"]["id"]
    update = client.patch(f"/api/v1/landed-costs/{landed_cost_id}", json={"international_freight": 500, "margin_rate": 10}, headers=operator_headers)
    assert update.status_code == 200, update.text
    updated = update.json()["data"]
    assert updated["international_freight"] == 500.0
    assert updated["margin_rate"] == 10.0
    assert updated["final_customer_total_price"] > 0
