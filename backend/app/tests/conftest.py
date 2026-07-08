import json

import pytest
from fastapi.testclient import TestClient

from app.config import SESSION_STORAGE_PATH
from app.main import app
from app.services.auth_service import seed_default_users
from app.services.platform_store import reset_demo_store


@pytest.fixture(autouse=True)
def clean_session_storage() -> None:
    SESSION_STORAGE_PATH.write_text("{}\n", encoding="utf-8")
    reset_demo_store(persist=True)
    seed_default_users()
    yield
    SESSION_STORAGE_PATH.write_text("{}\n", encoding="utf-8")
    reset_demo_store(persist=True)
    seed_default_users()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def _login_headers(client: TestClient, email: str, password: str) -> dict[str, str]:
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def admin_headers(client: TestClient) -> dict[str, str]:
    return _login_headers(client, "admin@niyamguard.local", "Admin@12345")


@pytest.fixture
def reviewer_headers(client: TestClient) -> dict[str, str]:
    return _login_headers(client, "reviewer@niyamguard.local", "Reviewer@12345")


@pytest.fixture
def viewer_headers(client: TestClient) -> dict[str, str]:
    return _login_headers(client, "viewer@niyamguard.local", "Viewer@12345")


@pytest.fixture
def session_id(client: TestClient) -> str:
    response = client.post(
        "/api/sessions",
        json={"form_id": "income_certificate", "language": "english"},
    )
    assert response.status_code == 201
    return response.json()["session_id"]


@pytest.fixture
def complete_form_values() -> dict[str, str]:
    return {
        "applicant_name": "Ravi Kumar",
        "father_name": "Suresh Kumar",
        "mobile_number": "9876543210",
        "aadhaar_number": "123456789012",
        "district": "Hyderabad",
        "mandal": "Ameerpet",
        "village": "Ameerpet",
        "monthly_income": "15000",
        "annual_income": "180000",
        "purpose": "Scholarship",
        "address": "House 1, Ameerpet, Hyderabad",
        "declaration": True,
    }


@pytest.fixture
def complete_uploaded_documents() -> dict[str, dict[str, object]]:
    return {
        "aadhaar": {"name": "aadhaar.pdf", "uploaded": True},
        "income_proof": {"name": "income.pdf", "uploaded": True},
        "address_proof": {"name": "address.pdf", "uploaded": True},
    }
