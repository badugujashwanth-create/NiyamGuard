import json
from functools import lru_cache
from pathlib import Path

from app.config import FORM_SCHEMA_PATH, FORMS_DIR
from app.models.form_models import FormCatalogItem, FormField, FormSchema


CATALOG_ONLY_SERVICES: tuple[dict[str, object], ...] = (
    {
        "form_id": "ration_card_food_security_card",
        "service_name": "Ration Card / Food Security Card",
        "department": "Civil Supplies",
        "category": "Food Security",
        "description": "Guidance for food security card or ration card application requirements.",
        "common_use_cases": ["Food security", "Ration benefits", "Family card"],
    },
    {
        "form_id": "ration_card_corrections",
        "service_name": "Ration Card Corrections",
        "department": "Civil Supplies",
        "category": "Food Security",
        "description": "Guidance for correcting names, address, or family members on ration card records.",
        "common_use_cases": ["Name correction", "Address correction", "Member update"],
    },
    {
        "form_id": "employment_exchange_registration",
        "service_name": "Employment Exchange Registration",
        "department": "Employment",
        "category": "Employment",
        "description": "Guidance for employment exchange registration details and documents.",
        "common_use_cases": ["Job registration", "Employment card", "Government job eligibility"],
    },
    {
        "form_id": "employment_exchange_renewal",
        "service_name": "Employment Exchange Renewal",
        "department": "Employment",
        "category": "Employment",
        "description": "Guidance for renewing an existing employment exchange registration.",
        "common_use_cases": ["Registration renewal", "Employment card renewal"],
    },
    {
        "form_id": "loan_eligibility_card",
        "service_name": "Loan Eligibility Card",
        "department": "Agriculture / Revenue",
        "category": "Agriculture",
        "description": "General guidance for loan eligibility card requirements. Detailed guided form is coming soon.",
        "common_use_cases": ["Agriculture loan", "Bank support", "Farmer benefit"],
    },
    {
        "form_id": "agricultural_income_certificate",
        "service_name": "Agricultural Income Certificate",
        "department": "Revenue",
        "category": "Agriculture",
        "description": "Guidance for proving agricultural income for schemes and records.",
        "common_use_cases": ["Agriculture income", "Farmer schemes", "Loan support"],
    },
    {
        "form_id": "small_marginal_farmer_certificate",
        "service_name": "Small and Marginal Farmer Certificate",
        "department": "Agriculture / Revenue",
        "category": "Agriculture",
        "description": "Guidance for small or marginal farmer certificate requirements.",
        "common_use_cases": ["Farmer benefits", "Subsidy", "Agriculture loan"],
    },
    {
        "form_id": "integrated_certificate",
        "service_name": "Integrated Certificate",
        "department": "Revenue",
        "category": "Certificates",
        "description": "Guidance for integrated certificate combining community, nativity, or date details where applicable.",
        "common_use_cases": ["Education", "Scholarship", "Recruitment"],
    },
    {
        "form_id": "nativity_certificate",
        "service_name": "Nativity Certificate",
        "department": "Revenue",
        "category": "Certificates",
        "description": "Guidance for nativity certificate requirements.",
        "common_use_cases": ["Local status", "Education", "Recruitment"],
    },
    {
        "form_id": "solvency_certificate",
        "service_name": "Solvency Certificate",
        "department": "Revenue",
        "category": "Certificates",
        "description": "Guidance for solvency certificate details and supporting documents.",
        "common_use_cases": ["Tender", "Financial proof", "Official requirement"],
    },
    {
        "form_id": "encumbrance_certificate_assistance",
        "service_name": "Encumbrance Certificate Assistance",
        "department": "Registration",
        "category": "Property",
        "description": "Guidance for collecting details needed before applying for an encumbrance certificate.",
        "common_use_cases": ["Property purchase", "Loan", "Legal check"],
    },
    {
        "form_id": "mutation_application_assistance",
        "service_name": "Mutation Application Assistance",
        "department": "Revenue",
        "category": "Property",
        "description": "Guidance for property mutation application preparation.",
        "common_use_cases": ["Ownership change", "Inheritance", "Sale deed update"],
    },
    {
        "form_id": "electricity_new_connection_assistance",
        "service_name": "Electricity New Connection Assistance",
        "department": "Energy",
        "category": "Utilities",
        "description": "Guidance for new electricity connection application requirements.",
        "common_use_cases": ["New house", "Shop connection", "Meter application"],
    },
    {
        "form_id": "birth_correction",
        "service_name": "Birth Correction",
        "department": "Municipal / Panchayat",
        "category": "Corrections",
        "description": "Guidance for correcting name, date, or parent details in birth records.",
        "common_use_cases": ["Name correction", "DOB correction", "Parent name correction"],
    },
    {
        "form_id": "death_correction",
        "service_name": "Death Correction",
        "department": "Municipal / Panchayat",
        "category": "Corrections",
        "description": "Guidance for correcting death certificate record details.",
        "common_use_cases": ["Name correction", "Date correction", "Address correction"],
    },
    {
        "form_id": "widow_pension_assistance",
        "service_name": "Widow Pension Assistance",
        "department": "Social Welfare",
        "category": "Benefits",
        "description": "Guidance for preparing widow pension application details and documents.",
        "common_use_cases": ["Pension", "Welfare benefit", "Income support"],
    },
    {
        "form_id": "disability_certificate_assistance",
        "service_name": "Disability Certificate Assistance",
        "department": "Health",
        "category": "Certificates",
        "description": "Guidance for disability certificate process preparation.",
        "common_use_cases": ["Disability benefits", "Pension", "Concession"],
    },
)

DEFAULT_USE_CASES: dict[str, list[str]] = {
    "income_certificate": ["Scholarship", "Fee reimbursement", "Jobs", "Benefits"],
    "residence_certificate": ["Address proof", "Local residence", "School admission"],
    "caste_community_certificate": ["Scholarship", "Admission", "Reservation benefits"],
    "birth_certificate": ["School admission", "Passport", "Identity proof"],
    "death_certificate": ["Legal record", "Pension", "Inheritance"],
    "name_change_request": ["Spelling correction", "Marriage", "Record mismatch"],
    "family_member_certificate": ["Family proof", "Pension", "Legal purpose"],
    "no_earning_member_certificate": ["Pension", "Scheme benefit", "Family support"],
    "no_property_certificate": ["Housing scheme", "Benefits", "Legal proof"],
    "ews_certificate": ["Scholarship", "Education reservation", "Recruitment"],
}

DETAILED_FORM_IDS: set[str] = {
    "income_certificate",
    "residence_certificate",
    "caste_community_certificate",
    "birth_certificate",
    "death_certificate",
    "name_change_request",
    "family_member_certificate",
    "no_earning_member_certificate",
    "no_property_certificate",
    "ews_certificate",
}


def normalize_form_id(form_id: str) -> str:
    return form_id.strip().replace("-", "_")


@lru_cache(maxsize=1)
def load_income_certificate_form(path: Path = FORM_SCHEMA_PATH) -> FormSchema:
    return load_form_schema("income_certificate", path=path)


@lru_cache(maxsize=64)
def load_form_schema(form_id: str, path: Path | None = None) -> FormSchema:
    normalized = normalize_form_id(form_id)
    form_path = path or FORMS_DIR / f"{normalized}.json"
    if not form_path.exists():
        raise FileNotFoundError(f"Unknown form: {form_id}")
    with form_path.open("r", encoding="utf-8") as form_file:
        payload = json.load(form_file)
    schema = FormSchema.model_validate(payload)
    if not schema.form_name:
        schema.form_name = f"{schema.service_name} Application"
    return schema


@lru_cache(maxsize=1)
def load_all_forms() -> tuple[FormSchema, ...]:
    if not FORMS_DIR.exists():
        return tuple()
    forms = [
        load_form_schema(path.stem, path=path)
        for path in sorted(FORMS_DIR.glob("*.json"))
        if path.stem in DETAILED_FORM_IDS
    ]
    return tuple(sorted(forms, key=lambda form: form.service_name.casefold()))


def catalog_item(form: FormSchema) -> FormCatalogItem:
    return FormCatalogItem(
        form_id=form.form_id,
        service_name=form.service_name,
        department=form.department,
        category=form.category,
        description=form.description,
        common_use_cases=form.common_use_cases or DEFAULT_USE_CASES.get(form.form_id, []),
        required_document_count=len(form.required_documents),
        status="ready",
        has_detailed_schema=True,
    )


def catalog_only_item(payload: dict[str, object]) -> FormCatalogItem:
    return FormCatalogItem(
        form_id=str(payload["form_id"]),
        service_name=str(payload["service_name"]),
        department=str(payload["department"]),
        category=str(payload["category"]),
        description=str(payload["description"]),
        common_use_cases=[str(item) for item in payload.get("common_use_cases", [])],
        required_document_count=0,
        status="catalog_only",
        has_detailed_schema=False,
    )


def list_form_catalog() -> list[FormCatalogItem]:
    detailed = [catalog_item(form) for form in load_all_forms()]
    detailed_ids = {item.form_id for item in detailed}
    catalog_only = [
        catalog_only_item(item)
        for item in CATALOG_ONLY_SERVICES
        if str(item["form_id"]) not in detailed_ids
    ]
    return sorted(
        [*detailed, *catalog_only],
        key=lambda item: (item.category.casefold(), item.service_name.casefold()),
    )


def search_services(query: str | None = None) -> list[FormCatalogItem]:
    normalized = " ".join((query or "").casefold().split())
    services = list_form_catalog()
    if not normalized:
        return services

    results: list[FormCatalogItem] = []
    detailed_by_id = {form.form_id: form for form in load_all_forms()}
    for service in services:
        haystack_parts = [
            service.form_id,
            service.service_name,
            service.department,
            service.category,
            service.description,
            *service.common_use_cases,
        ]
        form = detailed_by_id.get(service.form_id)
        if form is not None:
            haystack_parts.extend(
                example
                for examples in form.assistant_examples.values()
                for example in examples
            )
        haystack = " ".join(haystack_parts).casefold()
        if normalized in haystack:
            results.append(service)
    return results


def find_service_suggestion(message: str) -> FormCatalogItem | None:
    normalized = " ".join(message.casefold().split())
    services = list_form_catalog()
    scored: list[tuple[int, FormCatalogItem]] = []
    detailed_by_id = {form.form_id: form for form in load_all_forms()}
    for service in services:
        score = 0
        service_tokens = set(service.service_name.casefold().replace("/", " ").split())
        message_tokens = set(normalized.split())
        score += len(service_tokens & message_tokens) * 3
        if service.form_id.replace("_", " ") in normalized:
            score += 5
        if service.form_id == "income_certificate" and "scholarship" in normalized:
            score += 4
        if any(use_case.casefold() in normalized for use_case in service.common_use_cases):
            score += 3
        form = detailed_by_id.get(service.form_id)
        if form is not None:
            for examples in form.assistant_examples.values():
                if any(example.casefold() in normalized for example in examples):
                    score += 2
        if score:
            scored.append((score, service))
    if not scored:
        return None
    return max(scored, key=lambda item: item[0])[1]


def _walk_fields(fields: list[FormField]) -> list[FormField]:
    return fields


def field_labels(form_id: str = "income_certificate") -> dict[str, str]:
    return {field.key: field.label for field in _walk_fields(load_form_schema(form_id).fields)}


def document_labels(form_id: str = "income_certificate") -> dict[str, str]:
    return {
        document.key: document.label
        for document in load_form_schema(form_id).required_documents
    }
