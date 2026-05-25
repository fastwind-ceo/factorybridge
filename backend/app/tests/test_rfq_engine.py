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


def create_sample_rfq(headers):
    payload = {
        "title": "CNC aluminum bracket",
        "description": "Manufacture aluminum brackets according to drawing.",
        "rfq_type": "BY_DRAWING",
        "category": "CNC_PARTS",
        "quantity": 500,
        "unit": "PCS",
        "currency": "USD",
        "delivery_country": "Russia",
        "delivery_city": "Moscow",
        "is_confidential": True,
    }
    response = client.post("/api/v1/rfqs", json=payload, headers=headers)
    assert response.status_code == 200, response.text
    return response.json()["data"]


def test_customer_can_create_update_specs_and_submit_rfq():
    _, headers = register_and_login("CUSTOMER", "customer.rfq.step005")
    rfq = create_sample_rfq(headers)
    assert rfq["rfq_number"].startswith("FB-RFQ-")
    assert rfq["status"] == "DRAFT"

    technical = client.put(
        f"/api/v1/rfqs/{rfq['id']}/technical-specs",
        json={
            "suggested_process": "CNC_MACHINING",
            "material": "ALUMINUM",
            "material_grade": "6061-T6",
            "tolerances": "±0.05 mm",
            "drawing_available": True,
            "model_3d_available": True,
            "sample_available": False,
        },
        headers=headers,
    )
    assert technical.status_code == 200, technical.text
    assert technical.json()["data"]["material"] == "ALUMINUM"

    logistics = client.put(
        f"/api/v1/rfqs/{rfq['id']}/logistics-specs",
        json={"destination_country": "Russia", "destination_city": "Moscow", "preferred_incoterms": "DDP", "estimated_weight_kg": 350},
        headers=headers,
    )
    assert logistics.status_code == 200, logistics.text
    assert logistics.json()["data"]["preferred_incoterms"] == "DDP"

    commercial = client.put(
        f"/api/v1/rfqs/{rfq['id']}/commercial-specs",
        json={"target_unit_price": 12.5, "requires_sample": True, "requires_tooling": False, "payment_terms": "30/70"},
        headers=headers,
    )
    assert commercial.status_code == 200, commercial.text
    assert commercial.json()["data"]["target_unit_price"] == 12.5

    submit = client.post(f"/api/v1/rfqs/{rfq['id']}/submit", headers=headers)
    assert submit.status_code == 200, submit.text
    submitted = submit.json()["data"]
    assert submitted["status"] == "SUBMITTED"
    assert len(submitted["status_history"]) >= 2


def test_operator_can_list_and_change_rfq_status():
    _, customer_headers = register_and_login("CUSTOMER", "customer.rfq.operator.step005")
    rfq = create_sample_rfq(customer_headers)
    client.post(f"/api/v1/rfqs/{rfq['id']}/submit", headers=customer_headers)

    _, operator_headers = register_and_login("PLATFORM_OPERATOR", "operator.rfq.step005")
    list_response = client.get("/api/v1/rfqs", headers=operator_headers)
    assert list_response.status_code == 200, list_response.text
    assert list_response.json()["data"]["total"] >= 1

    status_response = client.post(
        f"/api/v1/rfqs/{rfq['id']}/status",
        json={"new_status": "UNDER_OPERATOR_REVIEW", "comment": "Accepted for review"},
        headers=operator_headers,
    )
    assert status_response.status_code == 200, status_response.text
    assert status_response.json()["data"]["status"] == "UNDER_OPERATOR_REVIEW"


def test_customer_cannot_view_other_customer_rfq_or_change_status():
    _, headers_a = register_and_login("CUSTOMER", "customer.a.rfq.step005")
    rfq = create_sample_rfq(headers_a)
    _, headers_b = register_and_login("CUSTOMER", "customer.b.rfq.step005")

    get_other = client.get(f"/api/v1/rfqs/{rfq['id']}", headers=headers_b)
    assert get_other.status_code == 403

    status_change = client.post(f"/api/v1/rfqs/{rfq['id']}/status", json={"new_status": "APPROVED_FOR_TENDER"}, headers=headers_a)
    assert status_change.status_code == 403


def test_rfq_dictionaries_are_available():
    _, headers = register_and_login("CUSTOMER", "customer.dict.rfq.step005")
    response = client.get("/api/v1/rfqs/dictionaries", headers=headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert "BY_DRAWING" in data["rfq_types"]
    assert "CNC_MACHINING" in data["manufacturing_processes"]
