import re
from dataclasses import dataclass, field

from app.services.income_calculator import calculate_annual_income, calculate_monthly_income
from app.services.language_helper import extract_digits, parse_spoken_number
from app.services.validator import validate_field


@dataclass(frozen=True)
class Guidance:
    field: str | None
    reply: str
    suggested_value: str | None = None
    related_values: dict[str, str] = field(default_factory=dict)
    warning: str | None = None
    auto_fill: bool = False
    should_submit: bool = False


def _unknown_guidance() -> Guidance:
    return Guidance(
        field=None,
        reply=(
            "Sure, I will help you. Please tell me which field you are filling now, "
            "for example Mobile Number, Aadhaar Number, Monthly Income, Annual Income, "
            "Purpose, or Address."
        ),
    )


def _income_guidance(message: str, detected_field: str) -> Guidance:
    amount = parse_spoken_number(message)
    if amount is None or amount <= 0:
        return Guidance(
            field=detected_field,
            reply="Please repeat the income amount clearly, for example fifteen thousand or 15000.",
            warning="Income must be a number greater than 0.",
        )

    normalized = message.lower()
    if detected_field == "annual_income":
        if "monthly" in normalized or "per month" in normalized:
            annual = calculate_annual_income(amount)
            return Guidance(
                field="annual_income",
                reply=(
                    f"For {amount} monthly income, annual income is {annual}. "
                    f"You can enter {annual} in the Annual Income field."
                ),
                suggested_value=annual,
                related_values={"monthly_income": str(amount)},
            )
        monthly = calculate_monthly_income(amount)
        return Guidance(
            field="annual_income",
            reply=f"You can enter {amount} in the Annual Income field.",
            suggested_value=str(amount),
            related_values={"monthly_income": monthly},
        )

    annual = calculate_annual_income(amount)
    return Guidance(
        field="monthly_income",
        reply=(
            f"You can enter {amount} in the Monthly Income field. If the form also asks "
            f"Annual Income, you can enter {annual} because {amount} multiplied by 12 is {annual}."
        ),
        suggested_value=str(amount),
        related_values={"annual_income": annual},
    )


def _identity_number_guidance(message: str, field_name: str) -> Guidance:
    digits = extract_digits(message)
    expected = 10 if field_name == "mobile_number" else 12
    label = "Mobile number" if field_name == "mobile_number" else "Aadhaar number"
    if not digits:
        return Guidance(
            field=field_name,
            reply=f"Please say or type the {expected}-digit {label.lower()} clearly.",
            warning=f"{label} must be {expected} digits.",
        )

    validation = validate_field(field_name, digits)
    if not validation.valid:
        return Guidance(
            field=field_name,
            reply=f"{validation.message} Please check and enter the correct {expected}-digit {label.lower()}.",
            warning=f"{label} must be {expected} digits.",
        )
    return Guidance(
        field=field_name,
        reply=f"This {label.lower()} has {expected} digits. You can type it manually after checking it.",
        suggested_value=digits,
    )


def _purpose_guidance(message: str) -> Guidance:
    purposes = {
        "scholarship": "Scholarship",
        "college admission": "College Admission",
        "admission": "College Admission",
        "job": "Job",
        "pension": "Pension",
    }
    normalized = message.lower()
    selected = next((value for key, value in purposes.items() if key in normalized), None)
    if selected:
        return Guidance(
            field="purpose",
            reply=(
                f"Yes. If you need the income certificate for {selected.lower()}, "
                f"you can enter {selected} in the Purpose of Certificate field."
            ),
            suggested_value=selected,
        )
    return Guidance(
        field="purpose",
        reply=(
            "Purpose means why you need the certificate. You can type a short reason such as "
            "Scholarship, College Admission, Job, or Pension."
        ),
    )


def _simple_field_guidance(field_name: str) -> Guidance:
    replies = {
        "address": (
            "In the Address field, enter your house number, street name, village or city, "
            "mandal, district, and pin code. Example: House No 1-2-33, Main Road, "
            "Ameerpet, Hyderabad, 500016."
        ),
        "applicant_name": "Enter your full name as it appears on Aadhaar or another official record.",
        "father_name": "Enter your father's full name as it appears on official records.",
        "district": "Enter the name of the district where you live.",
        "mandal": "Enter the name of the mandal where you live.",
        "village": "Enter your village or town name.",
    }
    return Guidance(field=field_name, reply=replies[field_name])


def generate_guidance(message: str, detected_field: str | None) -> Guidance:
    if detected_field is None:
        return _unknown_guidance()
    if detected_field in {"monthly_income", "annual_income"}:
        return _income_guidance(message, detected_field)
    if detected_field in {"mobile_number", "aadhaar_number"}:
        return _identity_number_guidance(message, detected_field)
    if detected_field == "purpose":
        return _purpose_guidance(message)
    return _simple_field_guidance(detected_field)
