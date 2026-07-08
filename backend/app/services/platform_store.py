import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.models.platform_store_models import PolicyDataStore


BASE_DIR = Path(__file__).resolve().parents[1]
STORAGE_DIR = BASE_DIR / "storage"
DATA_PATH = STORAGE_DIR / "platform_demo.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _empty_store() -> dict[str, list[Any]]:
    return PolicyDataStore().model_dump()


def read_store() -> PolicyDataStore:
    if not DATA_PATH.exists():
        return PolicyDataStore(**deepcopy(DEMO_DATA))
    with DATA_PATH.open("r", encoding="utf-8") as handle:
        return PolicyDataStore(**json.load(handle))


def write_store(store: PolicyDataStore) -> PolicyDataStore:
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    with DATA_PATH.open("w", encoding="utf-8") as handle:
        json.dump(store.model_dump(), handle, indent=2, ensure_ascii=False)
    return store


def reset_demo_store(persist: bool = True) -> PolicyDataStore:
    store = PolicyDataStore(**deepcopy(DEMO_DATA))
    if persist:
        write_store(store)
    return store


def add_audit_event(store: PolicyDataStore, action: str, payload: dict[str, Any]) -> None:
    store.audit_events.append(
        {
            "id": f"audit_{len(store.audit_events) + 1:03d}",
            "action": action,
            "payload": payload,
            "timestamp": now_iso(),
        }
    )


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
                "and fee reimbursement applications."
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
            "document_changes": [],
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
}
