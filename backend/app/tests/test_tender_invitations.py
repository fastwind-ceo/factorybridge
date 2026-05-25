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
        "title": "Tender invitation CNC part",
        "description": "Part for supplier invitation tests.",
        "rfq_type": "BY_DRAWING",
        "category": "CNC_PARTS",
        "quantity": 100,
        "unit": "PCS",
        "delivery_country": "Russia",
        "delivery_city": "Moscow",
    }, headers=headers)
    assert response.status_code == 200, response.text
    return response.json()["data"]


def approve_for_tender(rfq_id: str, operator_headers):
    response = client.post(f"/api/v1/rfqs/{rfq_id}/status", json={"new_status": "APPROVED_FOR_TENDER", "comment": "Ready for supplier invitation"}, headers=operator_headers)
    assert response.status_code == 200, response.text
    return response.json()["data"]


def test_operator_can_invite_supplier_and_supplier_accepts_invitation():
    _, customer_headers = register_and_login("CUSTOMER", "customer.tender.step008")
    supplier_reg, supplier_headers = register_and_login("SUPPLIER", "supplier.tender.step008")
    _, operator_headers = register_and_login("PLATFORM_OPERATOR", "operator.tender.step008")

    rfq = create_rfq(customer_headers)
    approve_for_tender(rfq["id"], operator_headers)

    invite = client.post(f"/api/v1/tenders/rfqs/{rfq['id']}/invite", json={
        "supplier_company_ids": [supplier_reg["company_id"]],
        "access_level": "PREVIEW",
        "message": "Please submit your quotation.",
    }, headers=operator_headers)
    assert invite.status_code == 200, invite.text
    invitation = invite.json()["data"]["items"][0]
    assert invitation["status"] == "INVITED"

    available = client.get("/api/v1/tenders/supplier/rfqs", headers=supplier_headers)
    assert available.status_code == 200, available.text
    assert any(item["rfq"]["id"] == rfq["id"] for item in available.json()["data"]["items"])

    detail = client.get(f"/api/v1/tenders/supplier/rfqs/{rfq['id']}", headers=supplier_headers)
    assert detail.status_code == 200, detail.text
    assert detail.json()["data"]["id"] == rfq["id"]

    accept = client.post(f"/api/v1/tenders/invitations/{invitation['id']}/accept", headers=supplier_headers)
    assert accept.status_code == 200, accept.text
    assert accept.json()["data"]["status"] == "ACCEPTED"


def test_supplier_cannot_see_uninvited_rfq_and_customer_cannot_invite():
    _, customer_headers = register_and_login("CUSTOMER", "customer.tender.denied.step008")
    supplier_reg, supplier_headers = register_and_login("SUPPLIER", "supplier.tender.denied.step008")
    _, operator_headers = register_and_login("PLATFORM_OPERATOR", "operator.tender.denied.step008")

    rfq = create_rfq(customer_headers)
    approve_for_tender(rfq["id"], operator_headers)

    uninvited_detail = client.get(f"/api/v1/tenders/supplier/rfqs/{rfq['id']}", headers=supplier_headers)
    assert uninvited_detail.status_code == 403

    customer_invite = client.post(f"/api/v1/tenders/rfqs/{rfq['id']}/invite", json={"supplier_company_ids": [supplier_reg["company_id"]]}, headers=customer_headers)
    assert customer_invite.status_code == 403


def test_supplier_can_decline_invitation():
    _, customer_headers = register_and_login("CUSTOMER", "customer.tender.decline.step008")
    supplier_reg, supplier_headers = register_and_login("SUPPLIER", "supplier.tender.decline.step008")
    _, operator_headers = register_and_login("PLATFORM_OPERATOR", "operator.tender.decline.step008")

    rfq = create_rfq(customer_headers)
    approve_for_tender(rfq["id"], operator_headers)
    invite = client.post(f"/api/v1/tenders/rfqs/{rfq['id']}/invite", json={"supplier_company_ids": [supplier_reg["company_id"]]}, headers=operator_headers)
    invitation = invite.json()["data"]["items"][0]

    decline = client.post(f"/api/v1/tenders/invitations/{invitation['id']}/decline", json={"reason": "No capacity"}, headers=supplier_headers)
    assert decline.status_code == 200, decline.text
    assert decline.json()["data"]["status"] == "DECLINED"
