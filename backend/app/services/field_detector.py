import re

VALID_FIELDS = {
    "applicant_name",
    "father_name",
    "mobile_number",
    "aadhaar_number",
    "district",
    "mandal",
    "village",
    "monthly_income",
    "annual_income",
    "purpose",
    "address",
}

FIELD_PATTERNS: list[tuple[str, tuple[str, ...]]] = [
    ("father_name", ("father name", "father", "parent name", "thandri peru", "pita ka naam")),
    ("aadhaar_number", ("aadhaar", "aadhar", "uid")),
    ("mobile_number", ("mobile number", "phone number", "contact number", "mobile", "phone", "contact")),
    ("annual_income", ("annual income", "yearly income", "annual", "yearly")),
    (
        "monthly_income",
        ("monthly income", "monthly salary", "income", "salary", "monthly", "sampadinchadam"),
    ),
    ("purpose", ("why certificate", "purpose", "reason", "enduku", "kis liye")),
    ("district", ("district", "jilla")),
    ("mandal", ("mandal",)),
    ("village", ("village", "town", "ooru", "gaon")),
    ("address", ("door number", "house number", "address", "house", "street", "chirunama", "pata")),
    ("applicant_name", ("applicant name", "full name", "name", "peru", "naam")),
]


def _contains_phrase(message: str, phrase: str) -> bool:
    return re.search(rf"(?<!\w){re.escape(phrase)}(?!\w)", message) is not None


def detect_field(message: str, current_field: str | None = None) -> str | None:
    normalized = " ".join(message.lower().split())
    for field, phrases in FIELD_PATTERNS:
        if any(_contains_phrase(normalized, phrase) for phrase in phrases):
            return field
    return current_field if current_field in VALID_FIELDS else None
