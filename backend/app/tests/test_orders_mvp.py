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
        "title": "Order flow CNC part",
        "description": "Part for order tests.",
        "rfq_type": "BY_DRAWING",
        "category": "CNC_PARTS",
        "quantity": 100,
        "unit": "PCS",
        "delivery_country": "Russia",
        "delivery_city": "Moscow",
    }, headers=headers)
    assert response.status_code == 200, response.text
    return response.json()["data"]


def prepare_accepted_quote_with_landed_cost():
    _customer_reg, customer_headers = register_and_login("CUSTOMER", "customer.order.step011")
    supplier_reg, supplier_headers = register_and_login("SUPPLIER", "supplier.order.step011")
    _operator_reg, operator_headers = register_and_login("PLATFORM_OPERATOR", "operator.order.step011")
    rfq = create_rfq(customer_headers)
    status_resp = client.post(f"/api/v1/rfqs/{rfq['id']}/status", json={"new_status": "APPROVED_FOR_TENDER", "comment": "Ready"}, headers=operator_headers)
    assert status_resp.status_code == 200, status_resp.text
    invite = client.post(f"/api/v1/tenders/rfqs/{rfq['id']}/invite", json={"supplier_company_ids": [supplier_reg["company_id"]]}, headers=operator_headers)
    assert invite.status_code == 200, invite.text
    quote_resp = client.post(f"/api/v1/quotes/rfqs/{rfq['id']}", json={
        "unit_price": 10,
        "currency": "USD",
        "quantity": 100,
        "moq": 100,
        "sample_cost": 50,
        "lead_time_mass_days": 20,
        "payment_terms": "30/70",
        "incoterms": "EXW",
    }, headers=supplier_headers)
    assert quote_resp.status_code == 200, quote_resp.text
    quote = quote_resp.json()["data"]
    submit = client.post(f"/api/v1/quotes/{quote['id']}/submit", headers=supplier_headers)
    assert submit.status_code == 200, submit.text
    accept = client.post(f"/api/v1/quotes/{quote['id']}/accept", headers=customer_headers)
    assert accept.status_code == 200, accept.text
    landed = client.post(f"/api/v1/landed-costs/quotes/{quote['id']}", json={
        "quantity": 100,
        "factory_unit_price": 10,
        "international_freight": 200,
        "vat_rate": 20,
        "platform_fee_rate": 5,
        "margin_rate": 10,
    }, headers=operator_headers)
    assert landed.status_code == 200, landed.text
    return rfq, quote, landed.json()["data"], customer_headers, supplier_headers, operator_headers


def test_operator_creates_order_from_accepted_quote_and_timeline_is_visible():
    rfq, quote, landed, customer_headers, supplier_headers, operator_headers = prepare_accepted_quote_with_landed_cost()

    denied = client.post(f"/api/v1/orders/from-quote/{quote['id']}", json={"landed_cost_id": landed["id"]}, headers=customer_headers)
    assert denied.status_code == 403

    create = client.post(f"/api/v1/orders/from-quote/{quote['id']}", json={
        "landed_cost_id": landed["id"],
        "payment_terms": "50% deposit, 50% before shipment",
        "planned_ready_date": "2026-07-15",
        "planned_delivery_date": "2026-08-10",
        "notes": "First pilot order",
    }, headers=operator_headers)
    assert create.status_code == 200, create.text
    order = create.json()["data"]
    assert order["order_number"].startswith("FB-ORD-")
    assert order["status"] == "CREATED"
    assert order["rfq_id"] == rfq["id"]
    assert order["quote_id"] == quote["id"]
    assert order["landed_cost_id"] == landed["id"]
    assert order["total_amount"] == landed["final_customer_total_price"]
    assert len(order["timeline"]) == 1
    assert order["timeline"][0]["event_type"] == "ORDER_CREATED"

    customer_get = client.get(f"/api/v1/orders/{order['id']}", headers=customer_headers)
    assert customer_get.status_code == 200, customer_get.text
    supplier_get = client.get(f"/api/v1/orders/{order['id']}", headers=supplier_headers)
    assert supplier_get.status_code == 200, supplier_get.text

    duplicate = client.post(f"/api/v1/orders/from-quote/{quote['id']}", json={"landed_cost_id": landed["id"]}, headers=operator_headers)
    assert duplicate.status_code == 409


def test_operator_changes_order_status_and_adds_events():
    _rfq, quote, landed, _customer_headers, _supplier_headers, operator_headers = prepare_accepted_quote_with_landed_cost()
    create = client.post(f"/api/v1/orders/from-quote/{quote['id']}", json={"landed_cost_id": landed["id"]}, headers=operator_headers)
    assert create.status_code == 200, create.text
    order_id = create.json()["data"]["id"]

    status_change = client.post(f"/api/v1/orders/{order_id}/status", json={"new_status": "SAMPLE_PRODUCTION", "comment": "Sample started"}, headers=operator_headers)
    assert status_change.status_code == 200, status_change.text
    order = status_change.json()["data"]
    assert order["status"] == "SAMPLE_PRODUCTION"
    assert any(item["event_type"] == "STATUS_CHANGED" for item in order["timeline"])

    custom_event = client.post(f"/api/v1/orders/{order_id}/events", json={"event_type": "SUPPLIER_UPDATE", "title": "Supplier sent production photos", "description": "Photos received."}, headers=operator_headers)
    assert custom_event.status_code == 200, custom_event.text
    assert custom_event.json()["data"]["event_type"] == "SUPPLIER_UPDATE"

    listed = client.get("/api/v1/orders/my", headers=operator_headers)
    assert listed.status_code == 200, listed.text
    assert any(item["id"] == order_id for item in listed.json()["data"]["items"])


def test_order_requires_accepted_quote():
    _customer_reg, customer_headers = register_and_login("CUSTOMER", "customer.order.unaccepted")
    supplier_reg, supplier_headers = register_and_login("SUPPLIER", "supplier.order.unaccepted")
    _operator_reg, operator_headers = register_and_login("PLATFORM_OPERATOR", "operator.order.unaccepted")
    rfq = create_rfq(customer_headers)
    client.post(f"/api/v1/rfqs/{rfq['id']}/status", json={"new_status": "APPROVED_FOR_TENDER"}, headers=operator_headers)
    client.post(f"/api/v1/tenders/rfqs/{rfq['id']}/invite", json={"supplier_company_ids": [supplier_reg["company_id"]]}, headers=operator_headers)
    quote = client.post(f"/api/v1/quotes/rfqs/{rfq['id']}", json={"unit_price": 10, "quantity": 10}, headers=supplier_headers).json()["data"]
    client.post(f"/api/v1/quotes/{quote['id']}/submit", headers=supplier_headers)
    create = client.post(f"/api/v1/orders/from-quote/{quote['id']}", json={}, headers=operator_headers)
    assert create.status_code == 409
