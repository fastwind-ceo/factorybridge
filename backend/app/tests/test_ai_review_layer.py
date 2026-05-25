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


def create_rfq(headers, *, title="CNC aluminum bracket", description="Manufacture aluminum brackets according to drawing."):
    response = client.post(
        "/api/v1/rfqs",
        json={
            "title": title,
            "description": description,
            "rfq_type": "BY_DRAWING",
            "category": "CNC_PARTS",
            "quantity": 500,
            "unit": "PCS",
            "currency": "USD",
            "delivery_country": "Russia",
            "delivery_city": "Moscow",
            "is_confidential": True,
        },
        headers=headers,
    )
    assert response.status_code == 200, response.text
    return response.json()["data"]


def test_ai_completeness_review_creates_structured_review_and_updates_status_after_submit():
    _, headers = register_and_login("CUSTOMER", "customer.ai.step007")
    rfq = create_rfq(headers)
    technical = client.put(
        f"/api/v1/rfqs/{rfq['id']}/technical-specs",
        json={
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
    client.post(f"/api/v1/rfqs/{rfq['id']}/submit", headers=headers)

    response = client.post(f"/api/v1/ai/rfqs/{rfq['id']}/completeness-check", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()["data"]
    review = data["review"]
    assert data["status_updated"] is True
    assert review["review_type"] == "COMPLETENESS_CHECK"
    assert review["completeness_score"] >= 70
    assert review["suggested_process"] in {"CNC_MACHINING", "UNKNOWN"}
    assert "supplier_brief_en" in review and "unit price" in review["supplier_brief_en"]

    rfq_after = client.get(f"/api/v1/rfqs/{rfq['id']}", headers=headers).json()["data"]
    assert rfq_after["status"] == "AI_REVIEWED"


def test_ai_review_detects_missing_data_and_risks_for_raw_request():
    _, headers = register_and_login("CUSTOMER", "customer.ai.raw.step007")
    rfq = create_rfq(headers, title="Unknown spare part", description="Need this part by photo")

    response = client.post(f"/api/v1/ai/rfqs/{rfq['id']}/completeness-check", headers=headers)
    assert response.status_code == 200, response.text
    review = response.json()["data"]["review"]
    assert review["completeness_score"] < 80
    missing_fields = {item["field"] for item in review["missing_fields"]}
    assert "technical_spec" in missing_fields
    assert any(flag["type"] == "TECHNICAL_INCOMPLETE" for flag in review["risk_flags"])


def test_process_classification_and_supplier_brief_endpoints_work():
    _, headers = register_and_login("CUSTOMER", "customer.ai.classifier.step007")
    rfq = create_rfq(headers)

    classification = client.post(f"/api/v1/ai/rfqs/{rfq['id']}/process-classification", headers=headers)
    assert classification.status_code == 200, classification.text
    assert classification.json()["data"]["suggested_process"] == "CNC_MACHINING"

    brief = client.post(f"/api/v1/ai/rfqs/{rfq['id']}/supplier-brief", headers=headers)
    assert brief.status_code == 200, brief.text
    data = brief.json()["data"]
    assert "supplier_brief_ru" in data
    assert "supplier_brief_en" in data
    assert "supplier_brief_cn" in data


def test_customer_cannot_run_ai_review_for_other_customer_rfq():
    _, headers_a = register_and_login("CUSTOMER", "customer.ai.a.step007")
    rfq = create_rfq(headers_a)
    _, headers_b = register_and_login("CUSTOMER", "customer.ai.b.step007")

    response = client.post(f"/api/v1/ai/rfqs/{rfq['id']}/completeness-check", headers=headers_b)
    assert response.status_code == 403
