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
        "title": "CNC aluminum bracket with drawing",
        "description": "Need to manufacture according to attached drawing.",
        "rfq_type": "BY_DRAWING",
        "category": "CNC_PARTS",
        "quantity": 100,
        "unit": "PCS",
        "delivery_country": "Russia",
    }
    response = client.post("/api/v1/rfqs", json=payload, headers=headers)
    assert response.status_code == 200, response.text
    return response.json()["data"]


def test_customer_can_upload_list_and_download_rfq_file():
    _, headers = register_and_login("CUSTOMER", "customer.file.step006")
    rfq = create_sample_rfq(headers)

    upload = client.post(
        f"/api/v1/files/rfqs/{rfq['id']}",
        data={"file_category": "DRAWING", "access_level": "PRIVATE"},
        files={"file": ("drawing.pdf", b"%PDF-1.4 fake drawing", "application/pdf")},
        headers=headers,
    )
    assert upload.status_code == 200, upload.text
    file_data = upload.json()["data"]
    assert file_data["file_name"] == "drawing.pdf"
    assert file_data["checksum"]

    listing = client.get(f"/api/v1/files/rfqs/{rfq['id']}", headers=headers)
    assert listing.status_code == 200, listing.text
    assert listing.json()["data"]["total"] == 1

    url_response = client.get(f"/api/v1/files/{file_data['id']}/download-url", headers=headers)
    assert url_response.status_code == 200, url_response.text
    download_url = url_response.json()["data"]["download_url"]
    downloaded = client.get(download_url)
    assert downloaded.status_code == 200, downloaded.text
    assert downloaded.content == b"%PDF-1.4 fake drawing"


def test_other_customer_cannot_access_rfq_file():
    _, owner_headers = register_and_login("CUSTOMER", "customer.file.owner.step006")
    rfq = create_sample_rfq(owner_headers)
    upload = client.post(
        f"/api/v1/files/rfqs/{rfq['id']}",
        data={"file_category": "DRAWING", "access_level": "PRIVATE"},
        files={"file": ("secret.pdf", b"secret", "application/pdf")},
        headers=owner_headers,
    )
    file_id = upload.json()["data"]["id"]

    _, other_headers = register_and_login("CUSTOMER", "customer.file.other.step006")
    listing = client.get(f"/api/v1/files/rfqs/{rfq['id']}", headers=other_headers)
    assert listing.status_code == 403
    url_response = client.get(f"/api/v1/files/{file_id}/download-url", headers=other_headers)
    assert url_response.status_code == 403


def test_invalid_file_extension_is_rejected():
    _, headers = register_and_login("CUSTOMER", "customer.file.invalid.step006")
    rfq = create_sample_rfq(headers)
    upload = client.post(
        f"/api/v1/files/rfqs/{rfq['id']}",
        data={"file_category": "OTHER", "access_level": "PRIVATE"},
        files={"file": ("malware.exe", b"no", "application/octet-stream")},
        headers=headers,
    )
    assert upload.status_code == 400
