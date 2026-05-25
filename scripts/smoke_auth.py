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


def main() -> None:
    init_db()
    client = TestClient(app)
    email = f"smoke.{uuid4().hex[:8]}@example.com"
    password = "StrongPassword123"
    register = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "company_name": "Smoke Customer", "company_type": "CUSTOMER"},
    )
    assert register.status_code == 200, register.text
    login = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert login.status_code == 200, login.text
    token = login.json()["data"]["access_token"]
    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200, me.text
    assert me.json()["data"]["roles"] == ["CUSTOMER"]
    print("STEP 003 auth smoke passed")


if __name__ == "__main__":
    main()
