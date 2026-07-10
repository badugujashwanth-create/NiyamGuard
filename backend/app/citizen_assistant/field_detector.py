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
    "date_of_birth",
    "gender",
    "document_upload",
    "declaration",
    "relation",
    "certificate_type",
}

FIELD_PATTERNS: list[tuple[str, tuple[str, ...]]] = [
    (
        "father_name",
        (
            "father name",
            "father",
            "parent name",
            "thandri peru",
            "pita ka naam",
            "father peru",
        ),
    ),
    ("aadhaar_number", ("aadhaar", "aadhar", "uid")),
    (
        "mobile_number",
        (
            "mobile number",
            "phone number",
            "contact number",
            "mobile",
            "phone",
            "contact",
            "number",
        ),
    ),
    (
        "annual_income",
        (
            "annual income",
            "yearly income",
            "year income",
            "yearly salary",
            "samvatsara income",
            "saal ka income",
            "annual",
            "yearly",
        ),
    ),
    (
        "monthly_income",
        (
            "monthly income",
            "month income",
            "monthly salary",
            "month ki income",
            "nela income",
            "month ki kamai",
            "income",
            "salary",
            "monthly",
            "sampadinchadam",
        ),
    ),
    (
        "purpose",
        (
            "why certificate",
            "purpose",
            "reason",
            "enduku",
            "kis liye",
            "scholarship",
            "job",
            "pension",
            "college admission",
        ),
    ),
    ("district", ("district", "jilla", "zila")),
    ("mandal", ("mandal",)),
    ("village", ("village", "town", "ooru", "gaon")),
    ("address", ("door number", "house number", "address", "house", "street", "chirunama", "pata")),
    (
        "date_of_birth",
        (
            "date of birth",
            "birth date",
            "dob",
            "puttina thedi",
            "janam din",
            "janm tarikh",
        ),
    ),
    ("gender", ("gender", "male", "female", "lingam", "ling", "purush", "mahila")),
    (
        "document_upload",
        (
            "document",
            "upload",
            "proof",
            "income proof",
            "aadhaar upload",
            "photo",
            "file",
            "upload cheyali",
            "document upload karna",
        ),
    ),
    (
        "declaration",
        (
            "declaration",
            "declare",
            "checkbox",
            "agree",
            "signature",
            "santakam",
            "ghoshana",
        ),
    ),
    ("relation", ("relation", "relationship", "bandham", "rishta", "wife", "husband", "son", "daughter")),
    (
        "certificate_type",
        (
            "certificate type",
            "type of certificate",
            "caste type",
            "community",
            "category",
        ),
    ),
    ("applicant_name", ("applicant name", "full name", "name", "peru", "naam")),
]


def _contains_phrase(message: str, phrase: str) -> bool:
    return re.search(rf"(?<!\w){re.escape(phrase)}(?!\w)", message) is not None


def detect_field(
    message: str,
    current_field: str | None = None,
    previous_field: str | None = None,
) -> str | None:
    normalized = " ".join(message.lower().split())
    for field, phrases in FIELD_PATTERNS:
        if any(_contains_phrase(normalized, phrase) for phrase in phrases):
            return field
    if current_field in VALID_FIELDS:
        return current_field
    return previous_field if previous_field in VALID_FIELDS else None
