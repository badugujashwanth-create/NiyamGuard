import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from app.models.platform_store_models import PolicyDataStore
from app.repositories.audit_repository import audit_repository
from app.repositories.policy_store_repository import PolicyStoreRepository
from app.services.time import now_iso


BASE_DIR = Path(__file__).resolve().parents[1]
STORAGE_DIR = BASE_DIR / "storage"
DATA_PATH = STORAGE_DIR / "platform_demo.json"
_repository = PolicyStoreRepository()


def _empty_store() -> dict[str, list[Any]]:
    return PolicyDataStore().model_dump()


def read_store() -> PolicyDataStore:
    db_store = _repository.load()
    if db_store is not None:
        db_store.audit_events = audit_repository.list(limit=500) or db_store.audit_events
        return db_store
    if not DATA_PATH.exists():
        return PolicyDataStore(**deepcopy(DEMO_DATA))
    with DATA_PATH.open("r", encoding="utf-8") as handle:
        store = PolicyDataStore(**json.load(handle))
        store.audit_events = audit_repository.list(limit=500) or store.audit_events
        return store


def write_store(store: PolicyDataStore) -> PolicyDataStore:
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    _repository.replace(store)
    with DATA_PATH.open("w", encoding="utf-8") as handle:
        json.dump(store.model_dump(), handle, indent=2, ensure_ascii=False)
    return store


def reset_demo_store(persist: bool = True) -> PolicyDataStore:
    store = PolicyDataStore(**deepcopy(DEMO_DATA))
    if persist:
        audit_repository.replace_from_legacy(store.audit_events)
        write_store(store)
    return store


def ensure_demo_store_seeded() -> PolicyDataStore:
    if _repository.has_records():
        store = read_store()
        demo_store = PolicyDataStore(**deepcopy(DEMO_DATA))
        changed = False
        for collection in (
            "official_circular_sources",
            "mock_connected_systems",
            "verified_policy_rule_versions",
            "service_definitions",
            "service_form_definitions",
            "service_slas",
        ):
            if not getattr(store, collection):
                setattr(store, collection, getattr(demo_store, collection))
                changed = True
        for collection in ("circulars", "verified_rules"):
            existing_ids = {item.id for item in getattr(store, collection)}
            for demo_item in getattr(demo_store, collection):
                if demo_item.id not in existing_ids:
                    getattr(store, collection).append(demo_item)
                    existing_ids.add(demo_item.id)
                    changed = True
        demo_services = {item.service_id: item for item in demo_store.service_definitions}
        enriched_service_ids = {"income_certificate", "post_matric_scholarship", "old_age_pension"}
        for service in store.service_definitions:
            if not service.department and service.service_id in demo_services:
                service.department = demo_services[service.service_id].department
                changed = True
            if service.service_id in enriched_service_ids and service.service_id in demo_services:
                demo_service = demo_services[service.service_id]
                if service.rule_bindings_json != demo_service.rule_bindings_json:
                    service.rule_bindings_json = demo_service.rule_bindings_json
                    changed = True
                if service.eligibility_json != demo_service.eligibility_json:
                    service.eligibility_json = demo_service.eligibility_json
                    changed = True
                if service.required_documents_json != demo_service.required_documents_json:
                    service.required_documents_json = demo_service.required_documents_json
                    changed = True
                if service.processing_days != demo_service.processing_days:
                    service.processing_days = demo_service.processing_days
                    changed = True
        demo_forms = {item.service_id: item for item in demo_store.service_form_definitions}
        for form in store.service_form_definitions:
            if form.service_id in enriched_service_ids and form.service_id in demo_forms:
                demo_form = demo_forms[form.service_id]
                if form.validation_rules_json != demo_form.validation_rules_json:
                    form.validation_rules_json = demo_form.validation_rules_json
                    changed = True
        demo_slas = {item.service_id: item for item in demo_store.service_slas}
        for sla in store.service_slas:
            if sla.service_id in enriched_service_ids and sla.service_id in demo_slas and sla.processing_days != demo_slas[sla.service_id].processing_days:
                sla.processing_days = demo_slas[sla.service_id].processing_days
                changed = True
        if changed:
            write_store(store)
        return store
    return reset_demo_store(persist=True)


def add_audit_event(store: PolicyDataStore, action: str, payload: dict[str, Any]) -> None:
    event = audit_repository.create(
        action=action,
        details=payload,
        actor_user_id=(
            payload.get("actor_user_id")
            or payload.get("reviewer_user_id")
            or payload.get("published_by")
            or payload.get("approved_by")
            or payload.get("parsed_by")
            or payload.get("created_by")
            or payload.get("triggered_by")
        ),
        actor_email=payload.get("actor_email"),
        actor_role=payload.get("actor_role"),
        entity_type=payload.get("entity_type"),
        entity_id=payload.get("entity_id"),
    )
    store.audit_events.append(event)


SERVICE_PORTAL_TIMESTAMP = "2026-07-01T00:00:00+00:00"


def _doc(key: str, name: str, mandatory: bool = True, copies: int = 1, notes: str | None = None) -> dict[str, Any]:
    return {
        "key": key,
        "name": name,
        "mandatory": mandatory,
        "copies_required": copies,
        "notes": notes,
    }


def _income_rule_bindings() -> dict[str, Any]:
    old_documents = [
        _doc("aadhaar", "Aadhaar Card"),
        _doc("ration_card", "Ration Card"),
        _doc("income_affidavit", "Self-declaration of income affidavit"),
        _doc("income_proof", "Salary slip / income proof", False, notes="Required where available"),
    ]
    new_documents = [
        _doc("aadhaar", "Aadhaar Card"),
        _doc("ration_card", "Ration Card"),
        _doc("income_affidavit", "Self-declaration of income affidavit"),
        _doc("passport_photo", "Passport-size photograph", True, 2, "New requirement introduced by GO-138"),
        _doc("income_proof", "Salary slip / income proof", False, notes="Required where available"),
    ]
    return {
        "validity_rule": "income_certificate.validity",
        "latest_rule_id": "rule_001",
        "previous_version": {
            "id": "income_certificate_go_112",
            "circular": {
                "id": "circ_000",
                "number": "GO-112",
                "title": "Revised procedure for issuance of Income Certificates",
                "issue_date": "2025-04-10",
                "effective_date": "2025-04-15",
            },
            "comparable_fields": {"validity_period_months": 12, "processing_time_days": 7},
            "eligibility_rules": [],
            "documents": old_documents,
            "process_steps": [
                {
                    "step_number": 1,
                    "title": "Submit application",
                    "description": "Submit the application with identity, ration card, and income proof documents.",
                    "required_documents": ["aadhaar", "ration_card", "income_affidavit"],
                    "is_start": True,
                    "is_end": False,
                },
                {
                    "step_number": 2,
                    "title": "Field verification",
                    "description": "Revenue staff verify household and income details.",
                    "required_documents": [],
                    "is_start": False,
                    "is_end": False,
                },
                {
                    "step_number": 3,
                    "title": "Approval",
                    "description": "Officer approves and issues the income certificate.",
                    "required_documents": [],
                    "is_start": False,
                    "is_end": True,
                },
            ],
        },
        "current_version": {
            "id": "income_certificate_go_138",
            "circular": {
                "id": "circ_001",
                "number": "GO-138",
                "title": "Amendment to validity period of Income Certificates",
                "issue_date": "2026-06-20",
                "effective_date": "2026-07-01",
            },
            "comparable_fields": {"validity_period_months": 6, "processing_time_days": 7},
            "eligibility_rules": [],
            "documents": new_documents,
            "process_steps": [
                {
                    "step_number": 1,
                    "title": "Submit application",
                    "description": "Submit the application with identity, income proof, and the new passport-size photographs.",
                    "required_documents": ["aadhaar", "ration_card", "income_affidavit", "passport_photo"],
                    "is_start": True,
                    "is_end": False,
                },
                {
                    "step_number": 2,
                    "title": "Field verification",
                    "description": "Revenue staff verify household and income details.",
                    "required_documents": [],
                    "is_start": False,
                    "is_end": False,
                },
                {
                    "step_number": 3,
                    "title": "Approval",
                    "description": "Officer approves and issues the income certificate under GO-138.",
                    "required_documents": [],
                    "is_start": False,
                    "is_end": True,
                },
            ],
        },
    }


def _scholarship_rule_bindings() -> dict[str, Any]:
    documents = [
        _doc("income_certificate", "Income Certificate (valid, current)", True, notes="Must be within current validity period"),
        _doc("caste_certificate", "Caste Certificate", True),
        _doc("marksheet", "Previous year mark sheet", True),
        _doc("bonafide", "Bonafide certificate from institution", True),
        _doc("bank_passbook", "Bank passbook copy", False, notes="For direct benefit transfer"),
    ]
    return {
        "depends_on": ["income_certificate"],
        "previous_version": {
            "id": "post_matric_scholarship_go_058",
            "circular": {
                "id": "circ_sch_058",
                "number": "GO-58",
                "title": "Post-Matric Scholarship Scheme guidelines",
                "issue_date": "2025-04-01",
                "effective_date": "2025-04-01",
            },
            "comparable_fields": {
                "income_limit_annual": 200000,
                "age_min": 15,
                "age_max": 25,
                "benefit_amount": 12000,
                "processing_time_days": 30,
            },
            "eligibility_rules": [],
            "documents": documents,
            "process_steps": [],
        },
        "current_version": {
            "id": "post_matric_scholarship_go_091",
            "circular": {
                "id": "circ_sch_091",
                "number": "GO-91",
                "title": "Revision of income limit for Post-Matric Scholarship Scheme",
                "issue_date": "2026-05-15",
                "effective_date": "2026-06-01",
            },
            "comparable_fields": {
                "income_limit_annual": 250000,
                "age_min": 15,
                "age_max": 25,
                "benefit_amount": 15000,
                "processing_time_days": 30,
            },
            "eligibility_rules": [
                {
                    "field_name": "annual_income",
                    "operator": "<=",
                    "value": 250000,
                    "explanation": "Annual family income must be at or below Rs. 2,50,000",
                },
                {"field_name": "age", "operator": ">=", "value": 15, "explanation": "Applicant must be at least 15 years old"},
                {"field_name": "age", "operator": "<=", "value": 25, "explanation": "Applicant must be 25 years old or younger"},
                {
                    "field_name": "category",
                    "operator": "in",
                    "value": ["SC", "ST", "OBC", "Minority", "General"],
                    "explanation": "Applicant category must be accepted by the scholarship scheme",
                },
                {
                    "field_name": "currently_enrolled",
                    "operator": "==",
                    "value": True,
                    "explanation": "Applicant must be currently enrolled in a post-matric course",
                },
            ],
            "documents": documents,
            "process_steps": [
                {
                    "step_number": 1,
                    "title": "Register on scholarship portal",
                    "description": "Create or update the student profile on the scholarship portal.",
                    "required_documents": [],
                    "is_start": True,
                    "is_end": False,
                },
                {
                    "step_number": 2,
                    "title": "Fill application and upload documents",
                    "description": "Enter student, institution, income, and bank details, then upload required evidence.",
                    "required_documents": ["income_certificate", "caste_certificate", "marksheet", "bonafide"],
                    "is_start": False,
                    "is_end": False,
                },
                {
                    "step_number": 3,
                    "title": "Institution verification",
                    "description": "Educational institution verifies enrollment and academic details.",
                    "required_documents": ["bonafide", "marksheet"],
                    "is_start": False,
                    "is_end": False,
                },
                {
                    "step_number": 4,
                    "title": "Department approval and disbursal",
                    "description": "Department approves the claim and releases benefit to the bank account.",
                    "required_documents": ["bank_passbook"],
                    "is_start": False,
                    "is_end": True,
                },
            ],
        },
    }


def _pension_rule_bindings() -> dict[str, Any]:
    return {
        "current_version": {
            "id": "old_age_pension_go_076",
            "circular": {
                "id": "circ_oap_076",
                "number": "GO-76",
                "title": "Old-Age Pension Scheme guidelines",
                "issue_date": "2026-01-10",
                "effective_date": "2026-02-01",
            },
            "comparable_fields": {
                "income_limit_annual": 150000,
                "age_min": 60,
                "age_max": None,
                "benefit_amount": 3000,
                "processing_time_days": 20,
            },
            "eligibility_rules": [
                {"field_name": "age", "operator": ">=", "value": 60, "explanation": "Applicant must be at least 60 years old"},
                {
                    "field_name": "annual_income",
                    "operator": "<=",
                    "value": 150000,
                    "explanation": "Annual family income must be at or below Rs. 1,50,000",
                },
            ],
            "documents": [
                _doc("aadhaar", "Aadhaar Card"),
                _doc("age_proof", "Age proof"),
                _doc("income_certificate", "Income Certificate (valid, current)"),
                _doc("bank_passbook", "Bank passbook copy"),
            ],
            "process_steps": [
                {
                    "step_number": 1,
                    "title": "Submit application at Panchayat or Ward office",
                    "description": "Submit identity, age, income, and bank details to the local office.",
                    "required_documents": ["aadhaar", "age_proof", "income_certificate", "bank_passbook"],
                    "is_start": True,
                    "is_end": False,
                },
                {
                    "step_number": 2,
                    "title": "Verification",
                    "description": "Officer verifies age, income, and residence details.",
                    "required_documents": [],
                    "is_start": False,
                    "is_end": False,
                },
                {
                    "step_number": 3,
                    "title": "Sanction and monthly disbursal",
                    "description": "Sanctioned pension is paid through the recorded bank account.",
                    "required_documents": ["bank_passbook"],
                    "is_start": False,
                    "is_end": True,
                },
            ],
        }
    }

SERVICE_PORTAL_SEED = [
    {
        "service_id": "income_certificate",
        "code": "INC",
        "name": "Income Certificate",
        "department": "Revenue Department",
        "category": "Revenue Certificates",
        "description": "Certificate confirming declared family income for scholarships, fee reimbursement, and public benefit checks.",
        "eligibility": ["Resident applicant", "Income details and supporting proof available"],
        "documents": [
            ("aadhaar", "Aadhaar Card", True),
            ("ration_card", "Ration Card", True),
            ("income_affidavit", "Self-declaration of income affidavit", True),
            ("passport_photo", "Passport-size photograph", True, 2, "New requirement introduced by GO-138"),
            ("income_proof", "Salary slip / income proof", False, 1, "Required where available"),
        ],
        "fee": 35,
        "days": 7,
        "rule_bindings": _income_rule_bindings(),
    },
    {
        "service_id": "residence_certificate",
        "code": "RES",
        "name": "Residence Certificate",
        "department": "Revenue Department",
        "category": "Revenue Certificates",
        "description": "Certificate confirming local residence for education, employment, and public service applications.",
        "eligibility": ["Resident applicant", "Address proof available"],
        "documents": [("aadhaar", "Aadhaar Card", True), ("address_proof", "Address Proof", True)],
        "fee": 25,
        "days": 7,
        "rule_bindings": {},
    },
    {
        "service_id": "caste_certificate",
        "code": "CAS",
        "name": "Caste Certificate",
        "department": "Social Welfare Department",
        "category": "Social Welfare Certificates",
        "description": "Certificate used for applicable reservation, welfare, and education benefits.",
        "eligibility": ["Applicant claims eligible caste/community status", "Parent or community proof available"],
        "documents": [
            ("aadhaar", "Aadhaar Card", True),
            ("community_proof", "Community Proof", True),
            ("address_proof", "Address Proof", True),
        ],
        "fee": 45,
        "days": 14,
        "rule_bindings": {},
    },
    {
        "service_id": "ews_certificate",
        "code": "EWS",
        "name": "EWS Certificate",
        "department": "Social Welfare Department",
        "category": "Social Welfare Certificates",
        "description": "Certificate for Economically Weaker Section eligibility checks.",
        "eligibility": ["Applicant meets declared income threshold", "Asset and income proof available"],
        "documents": [
            ("aadhaar", "Aadhaar Card", True),
            ("income_proof", "Income Proof", True),
            ("asset_declaration", "Asset Declaration", True),
        ],
        "fee": 45,
        "days": 14,
        "rule_bindings": {},
    },
    {
        "service_id": "birth_certificate",
        "code": "BIR",
        "name": "Birth Certificate",
        "department": "Civil Registration Department",
        "category": "Civil Registration",
        "description": "Certificate of birth registration for school admission, identity, and public records.",
        "eligibility": ["Birth event details available", "Hospital or local registration proof available"],
        "documents": [("hospital_record", "Hospital Record", True), ("parent_id", "Parent Identity Proof", True)],
        "fee": 20,
        "days": 5,
        "rule_bindings": {},
    },
    {
        "service_id": "death_certificate",
        "code": "DEA",
        "name": "Death Certificate",
        "department": "Civil Registration Department",
        "category": "Civil Registration",
        "description": "Certificate of death registration for legal, pension, and family member services.",
        "eligibility": ["Death event details available", "Medical or local authority record available"],
        "documents": [("medical_record", "Medical Record", True), ("informant_id", "Informant Identity Proof", True)],
        "fee": 20,
        "days": 5,
        "rule_bindings": {},
    },
    {
        "service_id": "family_member_certificate",
        "code": "FAM",
        "name": "Family Member Certificate",
        "department": "Revenue Department",
        "category": "Revenue Certificates",
        "description": "Family member certificate for inheritance, pension, and public record use cases.",
        "eligibility": ["Applicant can declare family relationship", "Supporting family record available"],
        "documents": [
            ("aadhaar", "Aadhaar Card", True),
            ("relationship_proof", "Relationship Proof", True),
            ("death_certificate", "Death Certificate if applicable", False),
        ],
        "fee": 35,
        "days": 10,
        "rule_bindings": {},
    },
    {
        "service_id": "ration_card",
        "code": "RAT",
        "name": "Ration Card",
        "department": "Civil Supplies Department",
        "category": "Food Security",
        "description": "Household ration card application for food security benefits.",
        "eligibility": ["Household details available", "Income and residence proof available"],
        "documents": [
            ("aadhaar", "Aadhaar Card", True),
            ("income_proof", "Income Proof", True),
            ("family_photo", "Family Photo", False),
        ],
        "fee": 0,
        "days": 21,
        "rule_bindings": {},
    },
    {
        "service_id": "old_age_pension",
        "code": "OAP",
        "name": "Old-Age Pension",
        "department": "Social Welfare Department",
        "category": "Welfare",
        "description": "Pension service for eligible senior citizens.",
        "eligibility": ["Applicant is at least 60 years old", "Annual family income is at or below Rs. 1,50,000"],
        "documents": [
            ("aadhaar", "Aadhaar Card", True),
            ("age_proof", "Age Proof", True),
            ("income_certificate", "Income Certificate (valid, current)", True),
            ("bank_passbook", "Bank Passbook", True),
        ],
        "fee": 0,
        "days": 20,
        "rule_bindings": _pension_rule_bindings(),
    },
    {
        "service_id": "post_matric_scholarship",
        "code": "SCH",
        "name": "Post-Matric Scholarship",
        "department": "Education Department",
        "category": "Education Welfare",
        "description": "Scholarship support workflow for post-matric students.",
        "eligibility": [
            "Annual family income is at or below Rs. 2,50,000",
            "Applicant age is between 15 and 25 years",
            "Applicant is currently enrolled in a post-matric course",
        ],
        "documents": [
            ("income_certificate", "Income Certificate (valid, current)", True, 1, "Must be within current validity period"),
            ("caste_certificate", "Caste Certificate", True),
            ("marksheet", "Previous Year Mark Sheet", True),
            ("bonafide", "Bonafide Certificate", True),
            ("bank_passbook", "Bank Passbook", False, 1, "For direct benefit transfer"),
        ],
        "fee": 0,
        "days": 30,
        "rule_bindings": _scholarship_rule_bindings(),
    },
]


def _portal_doc(
    key: str,
    label: str,
    required: bool,
    copies_required: int = 1,
    notes: str | None = None,
) -> dict[str, Any]:
    return {
        "key": key,
        "label": label,
        "required": required,
        "copies_required": copies_required,
        "notes": notes,
        "accepted_file_types": ["pdf", "jpg", "jpeg", "png"],
        "max_size_mb": 5,
    }


def _portal_fields(service_id: str) -> list[dict[str, Any]]:
    common = [
        {"key": "applicant_name", "label": "Applicant Full Name", "type": "text", "required": True},
        {"key": "mobile_number", "label": "Mobile Number", "type": "phone", "required": True},
        {"key": "district", "label": "District", "type": "text", "required": True},
        {"key": "mandal", "label": "Mandal", "type": "text", "required": True},
        {"key": "address", "label": "Address", "type": "textarea", "required": True},
        {"key": "purpose", "label": "Purpose", "type": "textarea", "required": True},
    ]
    service_specific = {
        "income_certificate": [
            {"key": "annual_income", "label": "Annual Income", "type": "number", "required": True},
            {"key": "occupation", "label": "Occupation", "type": "text", "required": True},
        ],
        "residence_certificate": [
            {"key": "years_at_address", "label": "Years at Address", "type": "number", "required": True},
        ],
        "caste_certificate": [
            {"key": "community_name", "label": "Community Name", "type": "text", "required": True},
        ],
        "ews_certificate": [
            {"key": "annual_income", "label": "Annual Income", "type": "number", "required": True},
            {"key": "asset_declaration", "label": "Asset Declaration Summary", "type": "textarea", "required": True},
        ],
        "birth_certificate": [
            {"key": "child_name", "label": "Child Name", "type": "text", "required": True},
            {"key": "date_of_birth", "label": "Date of Birth", "type": "date", "required": True},
        ],
        "death_certificate": [
            {"key": "deceased_name", "label": "Deceased Person Name", "type": "text", "required": True},
            {"key": "date_of_death", "label": "Date of Death", "type": "date", "required": True},
        ],
        "family_member_certificate": [
            {"key": "relationship_summary", "label": "Family Relationship Summary", "type": "textarea", "required": True},
        ],
        "ration_card": [
            {"key": "family_size", "label": "Family Size", "type": "number", "required": True},
            {"key": "annual_income", "label": "Annual Income", "type": "number", "required": True},
        ],
        "old_age_pension": [
            {"key": "age", "label": "Age", "type": "number", "required": True},
            {"key": "bank_account_last4", "label": "Bank Account Last 4 Digits", "type": "text", "required": True},
        ],
        "post_matric_scholarship": [
            {"key": "course_name", "label": "Course Name", "type": "text", "required": True},
            {"key": "institution_name", "label": "Institution Name", "type": "text", "required": True},
            {"key": "annual_income", "label": "Family Annual Income", "type": "number", "required": True},
        ],
    }
    return common + service_specific.get(service_id, [])


def _service_definitions() -> list[dict[str, Any]]:
    return [
        {
            "id": f"svc_{item['service_id']}",
            "service_id": item["service_id"],
            "name": item["name"],
            "department": item["department"],
            "category": item["category"],
            "description": item["description"],
            "eligibility_json": item["eligibility"],
            "required_documents_json": [_portal_doc(*doc) for doc in item["documents"]],
            "fee_amount": item["fee"],
            "processing_days": item["days"],
            "enabled": True,
            "rule_bindings_json": {**item["rule_bindings"], "application_code": item["code"]},
            "created_at": SERVICE_PORTAL_TIMESTAMP,
            "updated_at": SERVICE_PORTAL_TIMESTAMP,
        }
        for item in SERVICE_PORTAL_SEED
    ]


def _service_form_definitions() -> list[dict[str, Any]]:
    return [
        {
            "id": f"form_{item['service_id']}_v1",
            "service_id": item["service_id"],
            "version": 1,
            "fields_json": _portal_fields(item["service_id"]),
            "validation_rules_json": {"required_documents": [doc[0] for doc in item["documents"] if doc[2]]},
            "is_current": True,
            "created_at": SERVICE_PORTAL_TIMESTAMP,
            "updated_at": SERVICE_PORTAL_TIMESTAMP,
        }
        for item in SERVICE_PORTAL_SEED
    ]


def _service_slas() -> list[dict[str, Any]]:
    return [
        {
            "id": f"sla_{item['service_id']}",
            "service_id": item["service_id"],
            "processing_days": item["days"],
            "escalation_days": max(item["days"] - 1, 1),
            "created_at": SERVICE_PORTAL_TIMESTAMP,
        }
        for item in SERVICE_PORTAL_SEED
    ]


DEMO_DATA = {
    **_empty_store(),
    "circulars": [
        {
            "id": "circ_001",
            "title": "Income Certificate Validity Amendment",
            "circular_number": "GO-138",
            "department": "Revenue",
            "issue_date": "2026-06-20",
            "effective_date": "2026-07-01",
            "source_file_path": "demo/go-138-income-certificate.txt",
            "source_text": (
                "Income certificate must be issued within 6 months for scholarship "
                "and fee reimbursement applications. Applicant must attach two recent "
                "passport-size photographs with the application."
            ),
            "status": "approved",
            "created_at": "2026-07-01T00:00:00+00:00",
            "updated_at": "2026-07-01T00:00:00+00:00",
        },
        {
            "id": "circ_000",
            "title": "Income Certificate Earlier Validity",
            "circular_number": "GO-112",
            "department": "Revenue",
            "issue_date": "2025-04-10",
            "effective_date": "2025-04-15",
            "source_file_path": "demo/go-112-income-certificate.txt",
            "source_text": "Income certificate validity is 12 months from date of issue.",
            "status": "approved",
            "created_at": "2025-04-15T00:00:00+00:00",
            "updated_at": "2025-04-15T00:00:00+00:00",
        },
        {
            "id": "circ_sch_058",
            "title": "Post-Matric Scholarship Scheme Guidelines",
            "circular_number": "GO-58",
            "department": "Education Department",
            "issue_date": "2025-04-01",
            "effective_date": "2025-04-01",
            "source_file_path": "demo/go-58-post-matric-scholarship.txt",
            "source_text": "Annual family income limit for eligibility under the Post-Matric Scholarship Scheme is Rs. 2,00,000.",
            "status": "approved",
            "created_at": "2025-04-01T00:00:00+00:00",
            "updated_at": "2025-04-01T00:00:00+00:00",
        },
        {
            "id": "circ_sch_091",
            "title": "Revision of Income Limit for Post-Matric Scholarship Scheme",
            "circular_number": "GO-91",
            "department": "Education Department",
            "issue_date": "2026-05-15",
            "effective_date": "2026-06-01",
            "source_file_path": "demo/go-91-post-matric-scholarship.txt",
            "source_text": (
                "In partial modification of GO-58, the annual family income limit for Post-Matric Scholarship "
                "is revised to Rs. 2,50,000 and the annual benefit amount is revised to Rs. 15,000."
            ),
            "status": "approved",
            "created_at": "2026-06-01T00:00:00+00:00",
            "updated_at": "2026-06-01T00:00:00+00:00",
        },
        {
            "id": "circ_oap_076",
            "title": "Old-Age Pension Scheme Guidelines",
            "circular_number": "GO-76",
            "department": "Social Welfare Department",
            "issue_date": "2026-01-10",
            "effective_date": "2026-02-01",
            "source_file_path": "demo/go-76-old-age-pension.txt",
            "source_text": (
                "Old-Age Pension eligibility requires applicant age of at least 60 years, annual family income "
                "not exceeding Rs. 1,50,000, and monthly benefit amount of Rs. 3,000."
            ),
            "status": "approved",
            "created_at": "2026-02-01T00:00:00+00:00",
            "updated_at": "2026-02-01T00:00:00+00:00",
        },
    ],
    "extracted_rules": [
        {
            "id": "ext_001",
            "circular_id": "circ_001",
            "service_id": "income_certificate",
            "rule_key": "validity",
            "rule_name": "Income Certificate Validity",
            "old_value": "12",
            "new_value": "6",
            "unit": "months",
            "effective_date": "2026-07-01",
            "affected_departments": ["Revenue", "Social Welfare"],
            "affected_forms": ["income_certificate"],
            "affected_documents": ["Income Certificate"],
            "affected_faqs": ["income_certificate_validity"],
            "eligibility_changes": [],
            "document_changes": ["Passport-size photograph added as a mandatory document"],
            "deadline_changes": ["Certificate must be renewed sooner"],
            "extraction_confidence": 0.91,
            "confidence_reason": "Circular explicitly states 6 months and references earlier 12-month validity.",
            "status": "approved",
            "source_clause": "Income certificate must be issued within 6 months.",
            "created_at": "2026-07-01T00:00:00+00:00",
            "updated_at": "2026-07-01T00:00:00+00:00",
        }
    ],
    "verified_rules": [
        {
            "id": "rule_001",
            "source_extraction_id": "ext_001",
            "circular_id": "circ_001",
            "service_id": "income_certificate",
            "rule_key": "validity",
            "rule_name": "Income Certificate Validity",
            "current_value": "6",
            "previous_value": "12",
            "unit": "months",
            "effective_date": "2026-07-01",
            "supersedes_rule_id": "rule_000",
            "status": "active",
            "approved_by": "demo_reviewer",
            "approved_at": "2026-07-01T00:00:00+00:00",
            "source_clause": "Income certificate must be issued within 6 months.",
            "confidence": 0.91,
            "created_at": "2026-07-01T00:00:00+00:00",
            "updated_at": "2026-07-01T00:00:00+00:00",
        },
        {
            "id": "rule_conflict_001",
            "source_extraction_id": None,
            "circular_id": "circ_000",
            "service_id": "income_certificate",
            "rule_key": "validity",
            "rule_name": "Income Certificate Validity",
            "current_value": "12",
            "previous_value": None,
            "unit": "months",
            "effective_date": "2025-04-15",
            "supersedes_rule_id": None,
            "status": "active",
            "approved_by": "demo_reviewer",
            "approved_at": "2025-04-15T00:00:00+00:00",
            "source_clause": "Income certificate validity is 12 months from date of issue.",
            "confidence": 0.88,
            "created_at": "2025-04-15T00:00:00+00:00",
            "updated_at": "2025-04-15T00:00:00+00:00",
        },
        {
            "id": "rule_sch_income_limit",
            "source_extraction_id": None,
            "circular_id": "circ_sch_091",
            "service_id": "post_matric_scholarship",
            "rule_key": "income_limit",
            "rule_name": "Post-Matric Scholarship Annual Income Limit",
            "current_value": "250000",
            "previous_value": "200000",
            "unit": "rupees",
            "effective_date": "2026-06-01",
            "supersedes_rule_id": None,
            "status": "active",
            "approved_by": "demo_reviewer",
            "approved_at": "2026-06-01T00:00:00+00:00",
            "source_clause": "The annual family income limit is revised to Rs. 2,50,000.",
            "confidence": 0.9,
            "created_at": "2026-06-01T00:00:00+00:00",
            "updated_at": "2026-06-01T00:00:00+00:00",
        },
        {
            "id": "rule_sch_benefit_amount",
            "source_extraction_id": None,
            "circular_id": "circ_sch_091",
            "service_id": "post_matric_scholarship",
            "rule_key": "benefit_amount",
            "rule_name": "Post-Matric Scholarship Benefit Amount",
            "current_value": "15000",
            "previous_value": "12000",
            "unit": "rupees",
            "effective_date": "2026-06-01",
            "supersedes_rule_id": None,
            "status": "active",
            "approved_by": "demo_reviewer",
            "approved_at": "2026-06-01T00:00:00+00:00",
            "source_clause": "The annual benefit amount is revised to Rs. 15,000.",
            "confidence": 0.88,
            "created_at": "2026-06-01T00:00:00+00:00",
            "updated_at": "2026-06-01T00:00:00+00:00",
        },
        {
            "id": "rule_oap_age_min",
            "source_extraction_id": None,
            "circular_id": "circ_oap_076",
            "service_id": "old_age_pension",
            "rule_key": "age_min",
            "rule_name": "Old-Age Pension Minimum Age",
            "current_value": "60",
            "previous_value": None,
            "unit": "years",
            "effective_date": "2026-02-01",
            "supersedes_rule_id": None,
            "status": "active",
            "approved_by": "demo_reviewer",
            "approved_at": "2026-02-01T00:00:00+00:00",
            "source_clause": "Applicant age must be at least 60 years.",
            "confidence": 0.9,
            "created_at": "2026-02-01T00:00:00+00:00",
            "updated_at": "2026-02-01T00:00:00+00:00",
        },
        {
            "id": "rule_oap_income_limit",
            "source_extraction_id": None,
            "circular_id": "circ_oap_076",
            "service_id": "old_age_pension",
            "rule_key": "income_limit",
            "rule_name": "Old-Age Pension Annual Income Limit",
            "current_value": "150000",
            "previous_value": None,
            "unit": "rupees",
            "effective_date": "2026-02-01",
            "supersedes_rule_id": None,
            "status": "active",
            "approved_by": "demo_reviewer",
            "approved_at": "2026-02-01T00:00:00+00:00",
            "source_clause": "Annual family income must not exceed Rs. 1,50,000.",
            "confidence": 0.9,
            "created_at": "2026-02-01T00:00:00+00:00",
            "updated_at": "2026-02-01T00:00:00+00:00",
        },
        {
            "id": "rule_oap_benefit_amount",
            "source_extraction_id": None,
            "circular_id": "circ_oap_076",
            "service_id": "old_age_pension",
            "rule_key": "benefit_amount",
            "rule_name": "Old-Age Pension Benefit Amount",
            "current_value": "3000",
            "previous_value": None,
            "unit": "rupees per month",
            "effective_date": "2026-02-01",
            "supersedes_rule_id": None,
            "status": "active",
            "approved_by": "demo_reviewer",
            "approved_at": "2026-02-01T00:00:00+00:00",
            "source_clause": "Monthly benefit amount is Rs. 3,000.",
            "confidence": 0.9,
            "created_at": "2026-02-01T00:00:00+00:00",
            "updated_at": "2026-02-01T00:00:00+00:00",
        },
    ],
    "connected_systems": [
        {
            "id": "sys_meeseva_portal",
            "name": "MeeSeva Income Certificate Portal",
            "system_type": "portal",
            "department": "Revenue",
            "district": "Statewide",
            "service_id": "income_certificate",
            "owner": "Portal Operations",
            "status": "active",
            "last_checked_at": None,
            "created_at": "2026-07-01T00:00:00+00:00",
            "updated_at": "2026-07-01T00:00:00+00:00",
        },
        {
            "id": "sys_officer_sop",
            "name": "Officer SOP Manual",
            "system_type": "sop",
            "department": "Revenue",
            "district": "Statewide",
            "service_id": "income_certificate",
            "owner": "Revenue Training Cell",
            "status": "active",
            "last_checked_at": None,
            "created_at": "2026-07-01T00:00:00+00:00",
            "updated_at": "2026-07-01T00:00:00+00:00",
        },
        {
            "id": "sys_public_faq",
            "name": "Public FAQ",
            "system_type": "faq",
            "department": "Revenue",
            "district": "Statewide",
            "service_id": "income_certificate",
            "owner": "Public Information Team",
            "status": "active",
            "last_checked_at": None,
            "created_at": "2026-07-01T00:00:00+00:00",
            "updated_at": "2026-07-01T00:00:00+00:00",
        },
        {
            "id": "sys_simplified_form",
            "name": "Simplified Citizen Form",
            "system_type": "form",
            "department": "Revenue",
            "district": "Statewide",
            "service_id": "income_certificate",
            "owner": "NiyamGuard Voice Assistant",
            "status": "active",
            "last_checked_at": None,
            "created_at": "2026-07-01T00:00:00+00:00",
            "updated_at": "2026-07-01T00:00:00+00:00",
        },
        {
            "id": "sys_scholarship_portal",
            "name": "Scholarship Portal Eligibility Checker",
            "system_type": "portal",
            "department": "Social Welfare",
            "district": "Statewide",
            "service_id": "post_matric_scholarship",
            "owner": "Scholarship Portal Team",
            "status": "active",
            "last_checked_at": None,
            "created_at": "2026-07-01T00:00:00+00:00",
            "updated_at": "2026-07-01T00:00:00+00:00",
        },
    ],
    "snapshots": [
        {
            "id": "snap_meeseva_validity",
            "connected_system_id": "sys_meeseva_portal",
            "service_id": "income_certificate",
            "rule_key": "validity",
            "displayed_value": "12",
            "unit": "months",
            "source_location": "Portal validation rule",
            "last_synced_at": "2026-06-15T00:00:00+00:00",
            "snapshot_source": "demo",
            "created_at": "2026-07-01T00:00:00+00:00",
            "updated_at": "2026-07-01T00:00:00+00:00",
        },
        {
            "id": "snap_sop_validity",
            "connected_system_id": "sys_officer_sop",
            "service_id": "income_certificate",
            "rule_key": "validity",
            "displayed_value": "12",
            "unit": "months",
            "source_location": "SOP section 4.2",
            "last_synced_at": "2026-06-10T00:00:00+00:00",
            "snapshot_source": "demo",
            "created_at": "2026-07-01T00:00:00+00:00",
            "updated_at": "2026-07-01T00:00:00+00:00",
        },
        {
            "id": "snap_faq_validity",
            "connected_system_id": "sys_public_faq",
            "service_id": "income_certificate",
            "rule_key": "validity",
            "displayed_value": "12",
            "unit": "months",
            "source_location": "FAQ: income certificate validity",
            "last_synced_at": "2026-06-08T00:00:00+00:00",
            "snapshot_source": "demo",
            "created_at": "2026-07-01T00:00:00+00:00",
            "updated_at": "2026-07-01T00:00:00+00:00",
        },
        {
            "id": "snap_form_validity",
            "connected_system_id": "sys_simplified_form",
            "service_id": "income_certificate",
            "rule_key": "validity",
            "displayed_value": "6",
            "unit": "months",
            "source_location": "Simplified form guidance",
            "last_synced_at": "2026-07-01T00:00:00+00:00",
            "snapshot_source": "demo",
            "created_at": "2026-07-01T00:00:00+00:00",
            "updated_at": "2026-07-01T00:00:00+00:00",
        },
        {
            "id": "snap_scholarship_income_limit",
            "connected_system_id": "sys_scholarship_portal",
            "service_id": "post_matric_scholarship",
            "rule_key": "income_limit",
            "displayed_value": "200000",
            "unit": "rupees",
            "source_location": "Scholarship eligibility checker",
            "last_synced_at": "2026-04-01T00:00:00+00:00",
            "snapshot_source": "demo",
            "created_at": "2026-07-01T00:00:00+00:00",
            "updated_at": "2026-07-01T00:00:00+00:00",
        },
    ],
    "audit_events": [
        {
            "id": "audit_001",
            "action": "demo_seed_loaded",
            "payload": {"scenario": "income_certificate_validity_12_to_6_months"},
            "timestamp": "2026-07-01T00:00:00+00:00",
        }
    ],
    "official_circular_sources": [
        {
            "id": "src_revenue_demo",
            "name": "Revenue Department Demo Circular Feed",
            "department": "Revenue",
            "source_type": "local_demo",
            "url": "demo://revenue/go-138",
            "enabled": True,
            "last_checked_at": None,
            "last_success_at": None,
            "created_at": "2026-07-01T00:00:00+00:00",
            "updated_at": "2026-07-01T00:00:00+00:00",
        }
    ],
    "verified_policy_rule_versions": [
        {
            "id": "version_rule_001_1",
            "rule_id": "rule_001",
            "version_number": 1,
            "service_id": "income_certificate",
            "rule_key": "validity",
            "value": "12",
            "unit": "months",
            "source_circular_id": "circ_000",
            "source_circular_number": "GO-112",
            "effective_date": "2025-04-15",
            "published_by": "demo_reviewer",
            "published_at": "2025-04-15T00:00:00+00:00",
            "is_current": False,
            "previous_version_id": None,
        },
        {
            "id": "version_rule_001_2",
            "rule_id": "rule_001",
            "version_number": 2,
            "service_id": "income_certificate",
            "rule_key": "validity",
            "value": "6",
            "unit": "months",
            "source_circular_id": "circ_001",
            "source_circular_number": "GO-138",
            "effective_date": "2026-07-01",
            "published_by": "demo_reviewer",
            "published_at": "2026-07-01T00:00:00+00:00",
            "is_current": True,
            "previous_version_id": "version_rule_001_1",
        },
    ],
    "mock_connected_systems": [
        {
            "id": "meeseva",
            "system_name": "Mock MeeSeva Portal",
            "service_id": "income_certificate",
            "rule_key": "validity",
            "displayed_value": "12 months",
            "expected_value": "6 months",
            "source_circular": "old_portal_config",
            "sync_status": "outdated",
            "last_updated_at": "2026-06-15T00:00:00+00:00",
        },
        {
            "id": "public_faq",
            "system_name": "Mock Public FAQ / Citizen Form",
            "service_id": "income_certificate",
            "rule_key": "validity",
            "faq_value": "12 months",
            "form_hint_value": "12 months",
            "expected_value": "6 months",
            "source_circular": "old_content",
            "sync_status": "outdated",
            "last_updated_at": "2026-06-08T00:00:00+00:00",
        },
    ],
    "service_definitions": _service_definitions(),
    "service_form_definitions": _service_form_definitions(),
    "service_slas": _service_slas(),
}
