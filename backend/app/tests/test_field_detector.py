import pytest

from app.services.field_detector import detect_field


@pytest.mark.parametrize(
    ("message", "expected"),
    [
        ("what is my full name field", "applicant_name"),
        ("thandri peru", "father_name"),
        ("mobile number galat hai", "mobile_number"),
        ("aadhar number kitna digit hota hai", "aadhaar_number"),
        ("monthly income entha rayali", "monthly_income"),
        ("what is annual income", "annual_income"),
        ("certificate enduku kavali", "purpose"),
        ("which jilla", "district"),
        ("my mandal", "mandal"),
        ("village or town", "village"),
        ("chirunama emi rayali", "address"),
    ],
)
def test_field_detection(message: str, expected: str) -> None:
    assert detect_field(message) == expected


def test_current_field_fallback() -> None:
    assert detect_field("what should I write", "purpose") == "purpose"


def test_unknown_field() -> None:
    assert detect_field("I need help") is None
