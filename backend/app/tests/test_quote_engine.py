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
        "title": "Quote engine CNC part",
        "description": "Part for quote engine tests.",
        "rfq_type": "BY_DRAWING",
        "category": "CNC_PARTS",
        "quantity": 250,
        "unit": "PCS",
        "delivery_country": "Russia",
        "delivery_city": "Moscow",
    }, headers=headers)
    assert response.status_code == 200, response.text
    return response.json()["data"]


def prepare_invited_rfq():
    _, customer_headers = register_and_login("CUSTOMER", "customer.quote.step009")
    supplier_reg, supplier_headers = register_and_login("SUPPLIER", "supplier.quote.step009")
    _, operator_headers = register_and_login("PLATFORM_OPERATOR", "operator.quote.step009")
    rfq = create_rfq(customer_headers)
    status_resp = client.post(f"/api/v1/rfqs/{rfq['id']}/status", json={"new_status": "APPROVED_FOR_TENDER", "comment": "Ready"}, headers=operator_headers)
    assert status_resp.status_code == 200, status_resp.text
    invite = client.post(f"/api/v1/tenders/rfqs/{rfq['id']}/invite", json={"supplier_company_ids": [supplier_reg["company_id"]]}, headers=operator_headers)
    assert invite.status_code == 200, invite.text
    return rfq, customer_headers, supplier_headers, operator_headers


def test_supplier_can_create_and_submit_quote_for_invited_rfq():
    rfq, _customer_headers, supplier_headers, operator_headers = prepare_invited_rfq()

    quote_resp = client.post(f"/api/v1/quotes/rfqs/{rfq['id']}", json={
        "unit_price": 12.5,
        "currency": "USD",
        "quantity": 250,
        "moq": 100,
        "sample_cost": 50,
        "lead_time_sample_days": 7,
        "lead_time_mass_days": 25,
        "payment_terms": "30/70",
        "incoterms": "EXW",
        "supplier_comments": "Price based on drawing.",
    }, headers=supplier_headers)
    assert quote_resp.status_code == 200, quote_resp.text
    quote = quote_resp.json()["data"]
    assert quote["status"] == "DRAFT"
    assert quote["unit_price"] == 12.5

    submit = client.post(f"/api/v1/quotes/{quote['id']}/submit", headers=supplier_headers)
    assert submit.status_code == 200, submit.text
    assert submit.json()["data"]["status"] == "SUBMITTED"

    listed = client.get(f"/api/v1/quotes/rfqs/{rfq['id']}", headers=operator_headers)
    assert listed.status_code == 200, listed.text
    assert len(listed.json()["data"]["items"]) >= 1


def test_customer_gets_safe_comparison_and_supplier_cannot_quote_uninvited_rfq():
    rfq, customer_headers, supplier_headers, _operator_headers = prepare_invited_rfq()
    quote_resp = client.post(f"/api/v1/quotes/rfqs/{rfq['id']}", json={"unit_price": 18, "currency": "USD", "lead_time_mass_days": 30}, headers=supplier_headers)
    quote = quote_resp.json()["data"]
    client.post(f"/api/v1/quotes/{quote['id']}/submit", headers=supplier_headers)

    comparison = client.get(f"/api/v1/quotes/rfqs/{rfq['id']}/customer-comparison", headers=customer_headers)
    assert comparison.status_code == 200, comparison.text
    data = comparison.json()["data"]
    assert data["summary"]["quote_count"] >= 1
    assert "operator_notes" not in data["items"][0]
    assert "submitted_by_user_id" not in data["items"][0]

    _, other_supplier_headers = register_and_login("SUPPLIER", "supplier.quote.denied.step009")
    denied = client.post(f"/api/v1/quotes/rfqs/{rfq['id']}", json={"unit_price": 10, "currency": "USD"}, headers=other_supplier_headers)
    assert denied.status_code == 403


def test_customer_can_accept_quote_and_rfq_moves_to_supplier_selected():
    rfq, customer_headers, supplier_headers, _operator_headers = prepare_invited_rfq()
    quote_resp = client.post(f"/api/v1/quotes/rfqs/{rfq['id']}", json={"unit_price": 21, "currency": "USD", "lead_time_mass_days": 20}, headers=supplier_headers)
    quote = quote_resp.json()["data"]
    client.post(f"/api/v1/quotes/{quote['id']}/submit", headers=supplier_headers)

    accept = client.post(f"/api/v1/quotes/{quote['id']}/accept", headers=customer_headers)
    assert accept.status_code == 200, accept.text
    assert accept.json()["data"]["status"] == "ACCEPTED"

    rfq_detail = client.get(f"/api/v1/rfqs/{rfq['id']}", headers=customer_headers)
    assert rfq_detail.status_code == 200
    assert rfq_detail.json()["data"]["status"] == "SUPPLIER_SELECTED"
