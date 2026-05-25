from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from uuid import uuid4

from fastapi.testclient import TestClient

from app.db.init_db import init_db
from app.main import app

client = TestClient(app)


def register(company_type: str, prefix: str):
    init_db()
    email = f"{prefix}.{uuid4().hex[:8]}@example.com"
    password = "StrongPassword123"
    r = client.post("/api/v1/auth/register", json={"email": email, "password": password, "company_name": f"{prefix} Company", "company_type": company_type})
    assert r.status_code == 200, r.text
    token = client.post("/api/v1/auth/login", json={"email": email, "password": password}).json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def main():
    headers = register("CUSTOMER", "smoke.files.step006")
    rfq = client.post("/api/v1/rfqs", json={
        "title": "Smoke RFQ with drawing",
        "description": "File smoke test",
        "rfq_type": "BY_DRAWING",
        "quantity": 10,
        "unit": "PCS"
    }, headers=headers).json()["data"]
    upload = client.post(
        f"/api/v1/files/rfqs/{rfq['id']}",
        data={"file_category": "DRAWING", "access_level": "PRIVATE"},
        files={"file": ("drawing.pdf", b"smoke-pdf", "application/pdf")},
        headers=headers,
    )
    assert upload.status_code == 200, upload.text
    file_id = upload.json()["data"]["id"]
    url = client.get(f"/api/v1/files/{file_id}/download-url", headers=headers).json()["data"]["download_url"]
    downloaded = client.get(url)
    assert downloaded.status_code == 200, downloaded.text
    assert downloaded.content == b"smoke-pdf"
    print("STEP 006 file storage smoke test passed")


if __name__ == "__main__":
    main()
