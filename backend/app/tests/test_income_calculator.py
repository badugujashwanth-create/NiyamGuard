import pytest

from app.services.income_calculator import calculate_annual_income, calculate_monthly_income
from app.services.language_helper import parse_spoken_number


@pytest.mark.parametrize(
    ("spoken", "expected"),
    [
        ("fifteen thousand", 15000),
        ("ten thousand", 10000),
        ("twenty thousand", 20000),
        ("one lakh", 100000),
        ("two lakh", 200000),
        ("one fifty thousand", 150000),
        ("15000 rupees", 15000),
        ("15,000", 15000),
    ],
)
def test_spoken_number_examples(spoken: str, expected: int) -> None:
    assert parse_spoken_number(spoken) == expected


def test_income_calculations() -> None:
    assert calculate_annual_income("15000") == "180000"
    assert calculate_monthly_income("180000") == "15000"


@pytest.mark.parametrize("value", ["0", "-1", "not a number"])
def test_invalid_income(value: str) -> None:
    with pytest.raises(ValueError):
        calculate_annual_income(value)
