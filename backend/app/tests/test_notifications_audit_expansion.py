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
        "title": "Notification test CNC part",
        "description": "Part for notification tests.",
        "rfq_type": "BY_DRAWING",
        "category": "CNC_PARTS",
        "quantity": 50,
        "unit": "PCS",
        "delivery_country": "Russia",
        "delivery_city": "Moscow",
    }, headers=headers)
    assert response.status_code == 200, response.text
    return response.json()["data"]


def test_operator_receives_rfq_submitted_notification_and_can_mark_it_read():
    _operator_reg, operator_headers = register_and_login("PLATFORM_OPERATOR", "operator.notifications.step012")
    _customer_reg, customer_headers = register_and_login("CUSTOMER", "customer.notifications.step012")
    rfq = create_rfq(customer_headers)

    submit = client.post(f"/api/v1/rfqs/{rfq['id']}/submit", headers=customer_headers)
    assert submit.status_code == 200, submit.text

    notifications = client.get("/api/v1/notifications/my", headers=operator_headers)
    assert notifications.status_code == 200, notifications.text
    payload = notifications.json()["data"]
    match = next(item for item in payload["items"] if item["notification_type"] == "RFQ_SUBMITTED" and item["object_id"] == rfq["id"])
    assert match["is_read"] is False

    marked = client.post(f"/api/v1/notifications/{match['id']}/read", headers=operator_headers)
    assert marked.status_code == 200, marked.text
    assert marked.json()["data"]["is_read"] is True


def test_supplier_invitation_and_landed_cost_notifications_are_created():
    _customer_reg, customer_headers = register_and_login("CUSTOMER", "customer.notifications.flow")
    supplier_reg, supplier_headers = register_and_login("SUPPLIER", "supplier.notifications.flow")
    _operator_reg, operator_headers = register_and_login("PLATFORM_OPERATOR", "operator.notifications.flow")
    rfq = create_rfq(customer_headers)
    approved = client.post(f"/api/v1/rfqs/{rfq['id']}/status", json={"new_status": "APPROVED_FOR_TENDER"}, headers=operator_headers)
    assert approved.status_code == 200, approved.text
    invite = client.post(f"/api/v1/tenders/rfqs/{rfq['id']}/invite", json={"supplier_company_ids": [supplier_reg["company_id"]]}, headers=operator_headers)
    assert invite.status_code == 200, invite.text

    supplier_notifications = client.get("/api/v1/notifications/my", headers=supplier_headers).json()["data"]["items"]
    assert any(item["notification_type"] == "SUPPLIER_INVITED" and item["object_id"] == rfq["id"] for item in supplier_notifications)

    quote = client.post(f"/api/v1/quotes/rfqs/{rfq['id']}", json={"unit_price": 12, "quantity": 50, "moq": 50}, headers=supplier_headers)
    assert quote.status_code == 200, quote.text
    quote_id = quote.json()["data"]["id"]
    submitted = client.post(f"/api/v1/quotes/{quote_id}/submit", headers=supplier_headers)
    assert submitted.status_code == 200, submitted.text
    landed = client.post(f"/api/v1/landed-costs/quotes/{quote_id}", json={"quantity": 50, "factory_unit_price": 12, "platform_fee_rate": 5}, headers=operator_headers)
    assert landed.status_code == 200, landed.text

    customer_notifications = client.get("/api/v1/notifications/my", headers=customer_headers).json()["data"]["items"]
    assert any(item["notification_type"] == "QUOTE_SUBMITTED" and item["object_id"] == quote_id for item in customer_notifications)
    assert any(item["notification_type"] == "LANDED_COST_CREATED" and item["object_id"] == landed.json()["data"]["id"] for item in customer_notifications)

    read_all = client.post("/api/v1/notifications/read-all", headers=customer_headers)
    assert read_all.status_code == 200, read_all.text
    assert read_all.json()["data"]["marked_read"] >= 2
