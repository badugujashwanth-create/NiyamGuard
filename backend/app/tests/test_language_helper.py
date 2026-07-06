import pytest

from app.services.language_helper import detect_language


@pytest.mark.parametrize(
    ("message", "selected_language", "expected_language", "expected_code"),
    [
        ("purpose lo scholarship ani rayacha", "english", "telugu", "te-IN"),
        ("monthly income పదిహేను వేలు అయితే ఎంత", "english", "telugu", "te-IN"),
        ("purpose mein scholarship likhna hai kya", "english", "hindi", "hi-IN"),
        ("मेरा monthly income 15000 है", "english", "hindi", "hi-IN"),
        (
            "monthly income fifteen thousand what should I enter",
            "english",
            "english",
            "en-IN",
        ),
        ("help me", "telugu", "telugu", "te-IN"),
        ("help me", "hindi", "hindi", "hi-IN"),
    ],
)
def test_detect_language(
    message: str,
    selected_language: str,
    expected_language: str,
    expected_code: str,
) -> None:
    assert detect_language(message, selected_language) == {
        "language": expected_language,
        "language_code": expected_code,
    }
