from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
response = client.get("/api/v1/health")
print(response.status_code)
print(response.json())
assert response.status_code == 200
assert response.json()["status"] in {"ok", "degraded"}
