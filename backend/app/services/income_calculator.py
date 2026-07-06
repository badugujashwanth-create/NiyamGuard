from decimal import Decimal, InvalidOperation


def _positive_decimal(value: str | int | float | Decimal) -> Decimal:
    try:
        amount = Decimal(str(value).replace(",", "").strip())
    except (InvalidOperation, AttributeError) as exc:
        raise ValueError("Income must be a number.") from exc
    if not amount.is_finite() or amount <= 0:
        raise ValueError("Income must be greater than 0.")
    return amount


def _display(amount: Decimal) -> str:
    if amount == amount.to_integral_value():
        return str(int(amount))
    return format(amount.normalize(), "f")


def calculate_annual_income(monthly_income: str | int | float | Decimal) -> str:
    return _display(_positive_decimal(monthly_income) * 12)


def calculate_monthly_income(annual_income: str | int | float | Decimal) -> str:
    return _display(_positive_decimal(annual_income) / 12)
