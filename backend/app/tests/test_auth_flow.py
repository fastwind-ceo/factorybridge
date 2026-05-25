from uuid import uuid4

from fastapi.testclient import TestClient

from app.db.init_db import init_db
from app.main import app

client = TestClient(app)


def unique_email(prefix: str) -> str:
    return f"{prefix}.{uuid4().hex[:10]}@example.com"


def test_register_login_me_and_company_flow():
    init_db()
    email = unique_email("customer.step003")
    register_payload = {
        "email": email,
        "password": "StrongPassword123",
        "first_name": "Ivan",
        "last_name": "Petrov",
        "company_name": "Step003 Customer LLC",
        "company_type": "CUSTOMER",
    }
    response = client.post("/api/v1/auth/register", json=register_payload)
    assert response.status_code == 200, response.text
    data = response.json()["data"]
    assert data["email"] == register_payload["email"]
    company_id = data["company_id"]

    login_response = client.post("/api/v1/auth/login", json={"email": register_payload["email"], "password": register_payload["password"]})
    assert login_response.status_code == 200, login_response.text
    token = login_response.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    me_response = client.get("/api/v1/auth/me", headers=headers)
    assert me_response.status_code == 200, me_response.text
    me = me_response.json()["data"]
    assert me["roles"] == ["CUSTOMER"]
    assert me["companies"][0]["id"] == company_id

    companies_response = client.get("/api/v1/companies/my", headers=headers)
    assert companies_response.status_code == 200
    assert companies_response.json()["data"][0]["name"] == "Step003 Customer LLC"


def test_customer_cannot_access_admin_dashboard():
    email = unique_email("noadmin.step003")
    password = "StrongPassword123"
    client.post("/api/v1/auth/register", json={"email": email, "password": password, "company_name": "No Admin LLC", "company_type": "CUSTOMER"})
    token = client.post("/api/v1/auth/login", json={"email": email, "password": password}).json()["data"]["access_token"]
    response = client.get("/api/v1/admin/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


def test_supplier_gets_supplier_role():
    email = unique_email("supplier.step003")
    password = "StrongPassword123"
    response = client.post("/api/v1/auth/register", json={"email": email, "password": password, "company_name": "Ningbo Supplier", "company_type": "SUPPLIER"})
    assert response.status_code == 200
    token = client.post("/api/v1/auth/login", json={"email": email, "password": password}).json()["data"]["access_token"]
    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}).json()["data"]
    assert me["roles"] == ["SUPPLIER"]
