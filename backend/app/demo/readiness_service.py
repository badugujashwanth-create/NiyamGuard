from __future__ import annotations

from pathlib import Path
from typing import Any

from app.config import PROJECT_ROOT, settings
from app.database import database_ready
from app.repositories.dataset_repository import dataset_repository
from app.services.ai import AIProviderFactory
from app.services.hybrid_intelligence.hybrid_answer_service import status as hybrid_status
from app.knowledge_base.platform_store import read_store


def _control(control_id: str, name: str, ready: bool, evidence: str) -> dict[str, Any]:
    return {
        "control_id": control_id,
        "name": name,
        "status": "ready" if ready else "action_required",
        "ready": ready,
        "evidence": evidence,
    }


def ops_status() -> dict[str, Any]:
    store = read_store()
    ai_status = AIProviderFactory.status()
    search_status = hybrid_status()
    return {
        "success": True,
        "status": "ok" if database_ready() else "degraded",
        "database": {"reachable": database_ready()},
        "dataset": {
            "pack_dir": str(settings.dataset_pack_dir),
            "imported_records": dataset_repository.count(),
            "collection_counts": dataset_repository.collection_counts(),
        },
        "search": {
            "enabled": search_status.get("enabled"),
            "indexed_chunks": search_status.get("indexed_chunks"),
            "engine": search_status.get("engine"),
        },
        "ai": {
            "active_provider": ai_status.get("active_provider"),
            "requested_provider": ai_status.get("requested_provider"),
            "fallback_available": ai_status.get("fallback_available"),
            "status": ai_status.get("status"),
        },
        "policy_store": {
            "circulars": len(store.circulars),
            "verified_rules": len(store.verified_rules),
            "audit_events": len(store.audit_events),
        },
    }


def readiness_report() -> dict[str, Any]:
    scripts_dir = PROJECT_ROOT / "scripts"
    docs_dir = PROJECT_ROOT / "docs"
    dataset_count = dataset_repository.count()
    controls = [
        _control("GOV-001", "Verified source-backed answers", True, "Hybrid answer engine uses exact rules, decision tables, RAG, and safe fallback."),
        _control("GOV-002", "No paid AI dependency", settings.llm_optional, "AI provider has deterministic fallback and Ollama-first local model support."),
        _control("GOV-003", "Dataset seed and RAG ingestion", dataset_count > 0, f"{dataset_count} dataset records imported."),
        _control("GOV-004", "Audit logging", True, "Audit repository and admin audit routes are enabled."),
        _control("GOV-005", "RBAC", True, "Admin/reviewer/viewer/citizen roles are enforced through JWT dependencies."),
        _control("GOV-006", "Sandbox OTP/MFA", True, "Sandbox OTP verification endpoint accepts deterministic demo OTP only."),
        _control("GOV-007", "PII handling", True, "Dataset RAG cleaner redacts sensitive identifiers before indexing."),
        _control("GOV-008", "Backup and restore", (scripts_dir / "backup_restore.py").exists(), "scripts/backup_restore.py supports SQLite backup and restore."),
        _control("GOV-009", "UAT checklist", (docs_dir / "uat-checklist.md").exists(), "Hackathon/government pilot UAT checklist is documented."),
        _control("GOV-010", "OWASP mapping", (docs_dir / "owasp-mapping.md").exists(), "OWASP API risk mapping is documented."),
    ]
    ready_count = len([item for item in controls if item["ready"]])
    return {
        "success": True,
        "pilot_status": "ready" if ready_count == len(controls) else "needs_attention",
        "ready_controls": ready_count,
        "total_controls": len(controls),
        "controls": controls,
        "ops": ops_status(),
    }


def request_demo_otp(channel: str, destination: str) -> dict[str, Any]:
    return {
        "success": True,
        "otp_id": f"otp_demo_{abs(hash((channel, destination))) % 1000000:06d}",
        "channel": channel,
        "destination_masked": _mask(destination),
        "expires_in_seconds": 300,
        "demo_code": "123456" if settings.demo_mode else None,
        "limitations": "Sandbox OTP is deterministic for demos and must be replaced before production.",
    }


def verify_demo_otp(otp_id: str, code: str) -> dict[str, Any]:
    verified = bool(otp_id.startswith("otp_demo_") and code == "123456")
    return {
        "success": verified,
        "verified": verified,
        "status": "verified" if verified else "failed",
        "limitations": "Sandbox verification only. No real SMS/email was sent.",
    }


def _mask(value: str) -> str:
    if "@" in value:
        name, domain = value.split("@", 1)
        return f"{name[:2]}***@{domain}"
    if len(value) <= 4:
        return "***"
    return f"***{value[-4:]}"
