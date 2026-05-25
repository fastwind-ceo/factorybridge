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


def make_supplier(prefix="supplier.step004"):
    data, headers = register_and_login("SUPPLIER", prefix)
    profile_payload = {
        "company_id": data["company_id"],
        "chinese_name": "宁波测试制造有限公司",
        "english_name": "Ningbo Test Manufacturing Co., Ltd.",
        "province": "Zhejiang",
        "city": "Ningbo",
        "year_established": 2018,
        "employee_count": 120,
        "export_experience": True,
        "export_countries": "Russia, Kazakhstan",
        "main_industries": "Industrial parts, truck parts",
    }
    response = client.post("/api/v1/suppliers/profile", json=profile_payload, headers=headers)
    assert response.status_code == 200, response.text
    return data, headers, response.json()["data"]


def test_supplier_can_create_profile_and_capability():
    data, headers, profile = make_supplier()
    assert profile["company_id"] == data["company_id"]
    assert profile["verification_level"] == "UNVERIFIED"

    capability_payload = {
        "process": "CNC_MACHINING",
        "materials": ["ALUMINUM", "CARBON_STEEL"],
        "min_order_quantity": 50,
        "max_part_size": "800x500x300 mm",
        "tolerance_level": "±0.05 mm",
        "surface_treatments": ["anodizing", "zinc plating"],
        "has_tooling_capability": True,
        "has_design_support": True,
        "has_qc_team": True,
        "lead_time_sample_days": 7,
        "lead_time_mass_days": 25,
        "description": "CNC machining for industrial parts",
    }
    response = client.post(f"/api/v1/suppliers/{data['company_id']}/capabilities", json=capability_payload, headers=headers)
    assert response.status_code == 200, response.text
    cap = response.json()["data"]
    assert cap["process"] == "CNC_MACHINING"
    assert "ALUMINUM" in cap["materials"]

    loaded = client.get(f"/api/v1/suppliers/{data['company_id']}", headers=headers)
    assert loaded.status_code == 200
    assert len(loaded.json()["data"]["capabilities"]) == 1


def test_operator_can_list_and_verify_suppliers():
    supplier_data, supplier_headers, _ = make_supplier("supplier.operator.step004")
    operator_data, operator_headers = register_and_login("PLATFORM_OPERATOR", "operator.step004")

    list_response = client.get("/api/v1/suppliers", headers=operator_headers)
    assert list_response.status_code == 200, list_response.text
    assert list_response.json()["data"]["total"] >= 1

    verify_response = client.post(
        f"/api/v1/suppliers/{supplier_data['company_id']}/verify",
        json={"verification_level": "BASIC_VERIFIED", "company_verification_status": "VERIFIED", "notes": "Documents checked"},
        headers=operator_headers,
    )
    assert verify_response.status_code == 200, verify_response.text
    verified = verify_response.json()["data"]
    assert verified["verification_level"] == "BASIC_VERIFIED"
    assert verified["company_verification_status"] == "VERIFIED"


def test_customer_cannot_list_suppliers_or_create_supplier_profile():
    customer_data, customer_headers = register_and_login("CUSTOMER", "customer.step004")
    list_response = client.get("/api/v1/suppliers", headers=customer_headers)
    assert list_response.status_code == 403
    create_response = client.post("/api/v1/suppliers/profile", json={"company_id": customer_data["company_id"], "english_name": "Not Supplier"}, headers=customer_headers)
    assert create_response.status_code == 403


def test_supplier_dictionaries_are_available_to_authenticated_users():
    _, headers = register_and_login("SUPPLIER", "dict.step004")
    response = client.get("/api/v1/suppliers/dictionaries", headers=headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert "CNC_MACHINING" in data["manufacturing_processes"]
    assert "ALUMINUM" in data["materials"]
