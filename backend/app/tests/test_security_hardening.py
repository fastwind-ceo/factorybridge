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
    reg = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "company_name": f"{prefix} Company",
            "company_type": company_type,
        },
    )
    assert reg.status_code == 200, reg.text
    token = client.post("/api/v1/auth/login", json={"email": email, "password": password}).json()["data"]["access_token"]
    return reg.json()["data"], {"Authorization": f"Bearer {token}"}


def create_rfq(customer_headers):
    resp = client.post(
        "/api/v1/rfqs",
        json={
            "title": "Confidential CNC bracket",
            "description": "RFQ with mixed file access levels.",
            "rfq_type": "BY_DRAWING",
            "category": "CNC_PARTS",
            "quantity": 100,
            "unit": "PCS",
            "delivery_country": "Russia",
        },
        headers=customer_headers,
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["data"]


def upload_file(customer_headers, rfq_id, name, content, access_level):
    resp = client.post(
        f"/api/v1/files/rfqs/{rfq_id}",
        data={"file_category": "DRAWING", "access_level": access_level},
        files={"file": (name, content, "application/pdf")},
        headers=customer_headers,
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["data"]


def test_supplier_rfq_and_file_access_is_invitation_and_access_level_based():
    customer, customer_headers = register_and_login("CUSTOMER", "customer.security.step017")
    preview_supplier, preview_headers = register_and_login("SUPPLIER", "supplier.security.preview.step017")
    full_supplier, full_headers = register_and_login("SUPPLIER", "supplier.security.full.step017")
    _, operator_headers = register_and_login("PLATFORM_OPERATOR", "operator.security.step017")

    rfq = create_rfq(customer_headers)
    private_file = upload_file(customer_headers, rfq["id"], "private.pdf", b"private", "PRIVATE")
    preview_file = upload_file(customer_headers, rfq["id"], "preview.pdf", b"preview", "SUPPLIER_PREVIEW")
    nda_file = upload_file(customer_headers, rfq["id"], "nda.pdf", b"nda", "NDA_REQUIRED")
    full_file = upload_file(customer_headers, rfq["id"], "full.pdf", b"full", "FULL_TENDER_ACCESS")

    # Uninvited supplier cannot access the RFQ or files.
    assert client.get(f"/api/v1/rfqs/{rfq['id']}", headers=preview_headers).status_code == 403
    assert client.get(f"/api/v1/files/rfqs/{rfq['id']}", headers=preview_headers).status_code == 403

    approved = client.post(
        f"/api/v1/rfqs/{rfq['id']}/status",
        json={"new_status": "APPROVED_FOR_TENDER", "comment": "Security hardening test approval."},
        headers=operator_headers,
    )
    assert approved.status_code == 200, approved.text

    preview_invite = client.post(
        f"/api/v1/tenders/rfqs/{rfq['id']}/invite",
        json={"supplier_company_ids": [preview_supplier["company_id"]], "access_level": "PREVIEW"},
        headers=operator_headers,
    )
    assert preview_invite.status_code == 200, preview_invite.text

    full_invite = client.post(
        f"/api/v1/tenders/rfqs/{rfq['id']}/invite",
        json={"supplier_company_ids": [full_supplier["company_id"]], "access_level": "FULL_ACCESS"},
        headers=operator_headers,
    )
    assert full_invite.status_code == 200, full_invite.text

    # Invited suppliers can view the RFQ, but file visibility is per access level.
    invited_rfq = client.get(f"/api/v1/rfqs/{rfq['id']}", headers=preview_headers)
    assert invited_rfq.status_code == 200, invited_rfq.text

    preview_listing = client.get(f"/api/v1/files/rfqs/{rfq['id']}", headers=preview_headers)
    assert preview_listing.status_code == 200, preview_listing.text
    preview_names = {item["file_name"] for item in preview_listing.json()["data"]["items"]}
    assert preview_names == {"preview.pdf"}

    full_listing = client.get(f"/api/v1/files/rfqs/{rfq['id']}", headers=full_headers)
    assert full_listing.status_code == 200, full_listing.text
    full_names = {item["file_name"] for item in full_listing.json()["data"]["items"]}
    assert full_names == {"preview.pdf", "nda.pdf", "full.pdf"}

    # Direct URL requests remain protected even when file IDs are guessed or leaked.
    assert client.get(f"/api/v1/files/{private_file['id']}/download-url", headers=full_headers).status_code == 403
    assert client.get(f"/api/v1/files/{nda_file['id']}/download-url", headers=preview_headers).status_code == 403
    assert client.get(f"/api/v1/files/{full_file['id']}/download-url", headers=preview_headers).status_code == 403

    preview_url = client.get(f"/api/v1/files/{preview_file['id']}/download-url", headers=preview_headers)
    assert preview_url.status_code == 200, preview_url.text
    assert client.get(preview_url.json()["data"]["download_url"]).content == b"preview"

    full_url = client.get(f"/api/v1/files/{full_file['id']}/download-url", headers=full_headers)
    assert full_url.status_code == 200, full_url.text
    assert client.get(full_url.json()["data"]["download_url"]).content == b"full"


def test_customer_safe_quote_comparison_hides_internal_quote_fields():
    customer, customer_headers = register_and_login("CUSTOMER", "customer.security.quote.step017")
    supplier, supplier_headers = register_and_login("SUPPLIER", "supplier.security.quote.step017")
    _, operator_headers = register_and_login("PLATFORM_OPERATOR", "operator.security.quote.step017")
    rfq = create_rfq(customer_headers)
    client.post(f"/api/v1/rfqs/{rfq['id']}/status", json={"new_status": "APPROVED_FOR_TENDER"}, headers=operator_headers)
    client.post(f"/api/v1/tenders/rfqs/{rfq['id']}/invite", json={"supplier_company_ids": [supplier["company_id"]]}, headers=operator_headers)
    quote = client.post(
        f"/api/v1/quotes/rfqs/{rfq['id']}",
        json={"unit_price": 10, "currency": "USD", "quantity": 100, "moq": 100, "lead_time_mass_days": 20, "operator_notes": "hidden"},
        headers=supplier_headers,
    )
    assert quote.status_code == 200, quote.text
    submitted = client.post(f"/api/v1/quotes/{quote.json()['data']['id']}/submit", headers=supplier_headers)
    assert submitted.status_code == 200, submitted.text

    comparison = client.get(f"/api/v1/quotes/rfqs/{rfq['id']}/customer-comparison", headers=customer_headers)
    assert comparison.status_code == 200, comparison.text
    item = comparison.json()["data"]["items"][0]
    assert "operator_notes" not in item
    assert "submitted_by_user_id" not in item
