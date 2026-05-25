from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from fastapi.testclient import TestClient

from app.db.init_db import init_db
from app.main import app

client = TestClient(app)


def main() -> None:
    init_db()
    email = "smoke.supplier.step004@example.com"
    password = "StrongPassword123"
    reg = client.post("/api/v1/auth/register", json={
        "email": email,
        "password": password,
        "company_name": "Smoke Supplier Step004",
        "company_type": "SUPPLIER",
    })
    if reg.status_code not in (200, 409):
        raise SystemExit(f"Register failed: {reg.status_code} {reg.text}")
    if reg.status_code == 409:
        # Existing local smoke user: use /me after login to discover company.
        login = client.post("/api/v1/auth/login", json={"email": email, "password": password})
        token = login.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        company_id = client.get("/api/v1/auth/me", headers=headers).json()["data"]["companies"][0]["id"]
    else:
        company_id = reg.json()["data"]["company_id"]
        login = client.post("/api/v1/auth/login", json={"email": email, "password": password})
        token = login.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

    profile = client.post("/api/v1/suppliers/profile", json={
        "company_id": company_id,
        "english_name": "Smoke Supplier Manufacturing Co., Ltd.",
        "city": "Ningbo",
        "export_experience": True,
    }, headers=headers)
    if profile.status_code not in (200, 409):
        raise SystemExit(f"Profile failed: {profile.status_code} {profile.text}")

    cap = client.post(f"/api/v1/suppliers/{company_id}/capabilities", json={
        "process": "CNC_MACHINING",
        "materials": ["ALUMINUM"],
        "min_order_quantity": 10,
        "has_qc_team": True,
    }, headers=headers)
    if cap.status_code != 200:
        raise SystemExit(f"Capability failed: {cap.status_code} {cap.text}")
    loaded = client.get(f"/api/v1/suppliers/{company_id}", headers=headers)
    if loaded.status_code != 200:
        raise SystemExit(f"Supplier load failed: {loaded.status_code} {loaded.text}")
    print("supplier smoke ok")


if __name__ == "__main__":
    main()
