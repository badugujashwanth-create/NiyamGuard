import json

import pytest
from fastapi.testclient import TestClient

from app.config import SESSION_STORAGE_PATH
from app.main import app


@pytest.fixture(autouse=True)
def clean_session_storage() -> None:
    SESSION_STORAGE_PATH.write_text("{}\n", encoding="utf-8")
    yield
    SESSION_STORAGE_PATH.write_text("{}\n", encoding="utf-8")


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


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
