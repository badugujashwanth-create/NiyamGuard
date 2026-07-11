import re

VALID_FIELDS = {
    "applicant_name",
    "father_name",
    "mobile_number",
    "aadhaar_number",
    "district",
    "mandal",
    "occupation",
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
    "eligibility",
    "validity",
    "status",
}

FIELD_PATTERNS: list[tuple[str, tuple[str, ...]]] = [
    (
        "validity",
        (
            "validity",
            "how many months valid",
            "kitne mahine valid",
            "कितने महीने valid",
            "చెల్లుబాటు",
        ),
    ),
    (
        "eligibility",
        ("eligibility", "eligible", "qualify", "అర్హత", "पात्रता"),
    ),
    (
        "status",
        ("application status", "track application", "tracking status", "స్థితి", "आवेदन स्थिति"),
    ),
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
            "वार्षिक आय",
            "సంవత్సర ఆదాయం",
        ),
    ),
    (
        "monthly_income",
        (
            "monthly income",
            "manual income",
            "manul income",
            "మెన్యువల్ ఇన్కమ్",
            "मैन्युअल इनकम",
            "मंथली इनकम",
            "నెలవారీ ఆదాయం",
            "month income",
            "monthly salary",
            "month ki income",
            "nela income",
            "month ki kamai",
            "salary",
            "monthly",
            "sampadinchadam",
        ),
    ),
    (
        "occupation",
        (
            "occupation",
            "job field",
            "work field",
            "profession",
            "employment",
            "व्यवसाय",
            "ऑक्यूपेशन",
            "ఉద్యోగం",
            "వృత్తి",
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
    ("mandal", ("mandal", "mandalam", "మండలం", "మండల", "मंडल")),
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
            "documents",
            "required documents",
            "documents enti",
            "documents కావాలి",
            "documents चाहिए",
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


NORMALIZED_FIELD_INTENTS = {
    "mandal": "mandal",
    "occupation": "occupation",
    "monthly_income": "monthly_income",
    "annual_income": "annual_income",
    "aadhaar_number": "aadhaar",
    "mobile_number": "mobile",
    "address": "address",
    "purpose": "purpose",
    "document_upload": "documents",
    "eligibility": "eligibility",
    "validity": "validity",
    "status": "status",
}
INTENT_FIELDS = {intent: field for field, intent in NORMALIZED_FIELD_INTENTS.items()}


def normalize_field_intent(
    message: str,
    current_field: str | None = None,
    previous_field: str | None = None,
) -> str:
    """Return the stable assistant intent without changing form schema field names."""
    detected = detect_field(message, current_field, previous_field)
    return NORMALIZED_FIELD_INTENTS.get(detected, detected or "unknown")


def field_for_normalized_intent(intent: str) -> str | None:
    return INTENT_FIELDS.get(intent, intent if intent in VALID_FIELDS else None)
