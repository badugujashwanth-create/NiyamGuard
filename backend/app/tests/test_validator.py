import pytest
from fastapi.testclient import TestClient

from app.services.validator import validate_field


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("mobile_number", "9876543210"),
        ("aadhaar_number", "123456789012"),
        ("monthly_income", "15000"),
        ("annual_income", "180000"),
        ("purpose", "Scholarship"),
    ],
)
def test_valid_values(field: str, value: str) -> None:
    assert validate_field(field, value).valid is True


@pytest.mark.parametrize(
    ("field", "value", "message_fragment"),
    [
        ("mobile_number", "987654321", "only 9 digits"),
        ("aadhaar_number", "12345678901", "only 11 digits"),
        ("monthly_income", "zero", "numeric value"),
        ("annual_income", "0", "greater than 0"),
        ("purpose", "", "required"),
    ],
)
def test_invalid_values(field: str, value: str, message_fragment: str) -> None:
    result = validate_field(field, value)
    assert result.valid is False
    assert message_fragment in result.message


def test_validate_endpoint_returns_safety_flags(client: TestClient) -> None:
    response = client.post(
        "/api/assistant/validate",
        json={"field": "mobile_number", "value": "987654321"},
    )
    body = response.json()
    assert response.status_code == 200
    assert body["valid"] is False
    assert body["auto_fill"] is False
    assert body["should_submit"] is False
