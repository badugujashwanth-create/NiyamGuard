from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any

from app.services.language_helper import extract_digits


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    message: str


REQUIRED_TEXT_FIELDS = {
    "applicant_name": "Applicant name",
    "father_name": "Father's name",
    "district": "District",
    "mandal": "Mandal",
    "village": "Village",
    "purpose": "Purpose",
    "address": "Address",
    "mother_name": "Mother name",
    "birth_place": "Birth place",
    "death_place": "Death place",
    "date_of_birth": "Date of birth",
    "date_of_death": "Date of death",
    "relation": "Relation",
    "certificate_type": "Certificate type",
    "new_name": "New name",
    "family_members": "Family members",
    "non_earning_person_name": "No earning person name",
    "land_details": "Land details",
    "residing_since": "Residing since",
    "declaration": "Declaration",
}


def _digit_validation(field_label: str, expected: int, value: Any) -> ValidationResult:
    raw = "" if value is None else str(value).strip()
    digits = extract_digits(raw)
    if not raw:
        return ValidationResult(False, f"{field_label} is required.")
    if any(character.isalpha() for character in raw):
        return ValidationResult(False, f"{field_label} should contain only {expected} digits.")
    if len(digits) != expected:
        return ValidationResult(
            False,
            f"This {field_label.lower()} has only {len(digits)} digits. "
            f"{field_label} should be {expected} digits.",
        )
    return ValidationResult(True, f"{field_label} has {expected} digits and is valid.")


def _income_validation(field_label: str, value: Any) -> ValidationResult:
    raw = "" if value is None else str(value).replace(",", "").strip()
    try:
        amount = Decimal(raw)
    except (InvalidOperation, ValueError):
        return ValidationResult(False, f"{field_label} should be a numeric value greater than 0.")
    if not amount.is_finite() or amount <= 0:
        return ValidationResult(False, f"{field_label} should be greater than 0.")
    return ValidationResult(True, f"{field_label} is valid.")


def validate_field(field: str, value: Any) -> ValidationResult:
    if field == "mobile_number":
        return _digit_validation("Mobile number", 10, value)
    if field == "aadhaar_number":
        return _digit_validation("Aadhaar number", 12, value)
    if field == "monthly_income":
        return _income_validation("Monthly income", value)
    if field == "annual_income":
        return _income_validation("Annual income", value)
    if field in REQUIRED_TEXT_FIELDS:
        label = REQUIRED_TEXT_FIELDS[field]
        if field == "declaration":
            if value is True or str(value).strip().lower() in {"true", "yes", "1", "on"}:
                return ValidationResult(True, "Declaration is confirmed.")
            return ValidationResult(False, "Declaration must be confirmed by the citizen.")
        if value is None or not str(value).strip():
            return ValidationResult(False, f"{label} is required.")
        return ValidationResult(True, f"{label} is valid.")
    if value is None or not str(value).strip():
        return ValidationResult(False, f"{field.replace('_', ' ').title()} is required.")
    return ValidationResult(True, f"{field.replace('_', ' ').title()} is valid.")
