import pytest

from app.citizen_assistant.field_detector import detect_field


@pytest.mark.parametrize(
    ("message", "expected"),
    [
        ("what is my full name field", "applicant_name"),
        ("thandri peru", "father_name"),
        ("mobile number galat hai", "mobile_number"),
        ("is this number correct", "mobile_number"),
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


def test_current_field_is_used_when_message_has_no_field() -> None:
    assert detect_field("I am stuck", "aadhaar_number", "purpose") == "aadhaar_number"


def test_explicit_message_field_overrides_stale_focus() -> None:
    assert detect_field("help with purpose", "monthly_income") == "purpose"


def test_previous_field_is_used_when_message_and_focus_are_unknown() -> None:
    assert detect_field("what should I type here", None, "address") == "address"


def test_unknown_field() -> None:
    assert detect_field("I need help") is None
