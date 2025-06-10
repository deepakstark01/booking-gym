# test for Booking API
from fastapi.testclient import TestClient
from src.api import app  # Adjust import if your FastAPI app is elsewhere

client = TestClient(app)

def test_get_classes():
    response = client.get("/api/v1/classes")
    assert response.status_code == 200
    assert isinstance(response.json(), list)