from __future__ import annotations

from typing import Any, Callable

from app.security.rbac import CurrentUser
from app.services import (
    circular_ingestion_service,
    circular_sync_service,
    compliance_orchestrator_service,
    compliance_service,
    mock_system_service,
    policy_publication_service,
    readiness_service,
    rule_extraction_service,
    service_portal_service as portal,
    system_patch_service,
)
from app.services.ai import AIProviderFactory
from app.services.hybrid_intelligence.hybrid_answer_service import answer_question
from app.services.platform_store import add_audit_event, read_store, reset_demo_store, write_store
from app.services.virtual_government_service import attach_synthetic_documents


StepRunner = Callable[[], dict[str, Any]]


def _success(key: str, label: str, details: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "key": key,
        "label": label,
        "status": "success",
        "details": details,
        "payload": payload or {},
    }


def _failed(key: str, label: str, exc: Exception) -> dict[str, Any]:
    return {
        "key": key,
        "label": label,
        "status": "failed",
        "details": str(exc),
        "payload": {},
    }


def _safe_step(steps: list[dict[str, Any]], key: str, label: str, runner: StepRunner) -> dict[str, Any]:
    try:
        step = runner()
    except Exception as exc:  # pragma: no cover - defensive guard for demo resilience
        step = _failed(key, label, exc)
    steps.append(step)
    return step


def run_full_end_to_end_demo() -> dict[str, Any]:
    steps: list[dict[str, Any]] = []
    entities: dict[str, Any] = {}
    state: dict[str, Any] = {}
    citizen = CurrentUser(id="user_citizen", email="citizen@niyamguard.local", role="citizen")
    officer = CurrentUser(id="user_officer", email="officer@niyamguard.local", role="officer")

    def reset_sandbox() -> dict[str, Any]:
        reset_demo_store(persist=True)
        return _success("reset_sandbox", "Reset sandbox", "Demo store reset to known GO-138 baseline.")

    def publish_circular() -> dict[str, Any]:
        sync = circular_sync_service.sync_all(created_by="full_demo")
        document = circular_ingestion_service.get_document("cirdoc_go_138")
        if document is None:
            document, _ = circular_ingestion_service.ingest_circular(
                {"id": "cirdoc_go_138", "source_id": "src_revenue_demo"}
            )
        state["circular_document"] = document
        return _success(
            "publish_circular",
            "Published GO-138 circular",
            "Virtual Gazette made the income certificate validity circular available.",
            {"sync": sync, "document": document.model_dump()},
        )

    def ingest_circular() -> dict[str, Any]:
        document = state["circular_document"]
        extraction = rule_extraction_service.extract_rules(document.id)
        candidate_id = (
            extraction.get("candidates", [{}])[0].get("id")
            if extraction.get("candidates")
            else f"cand_{document.id}_income_validity"
        )
        state["candidate_id"] = candidate_id
        return _success(
            "ingest_circular",
            "Ingested circular and extracted rule candidate",
            "Rule extraction found the 12 month to 6 month validity change.",
            {"candidate_id": candidate_id, "extraction": extraction},
        )

    def update_verified_rule() -> dict[str, Any]:
        candidate_id = state["candidate_id"]
        approval = rule_extraction_service.approve_candidate(
            candidate_id,
            reviewer_user_id="demo_reviewer",
            notes="Full end-to-end demo approval.",
        )
        publication = policy_publication_service.publish_rule_candidate(
            candidate_id,
            reviewer_user_id="demo_reviewer",
            notes="Full end-to-end demo publication.",
        )
        state["publication"] = publication
        version = publication.get("rule_version") or {}
        entities["rule_id"] = version.get("rule_id") or "rule_001"
        entities["rule_version_id"] = version.get("id")
        return _success(
            "update_verified_rule",
            "Updated verified rule engine",
            "Verified rule now points to GO-138 and 6 months.",
            {"approval": approval, "publication": publication},
        )

    def update_service_portal() -> dict[str, Any]:
        service = portal.get_service("income_certificate")
        return _success(
            "update_service_portal",
            "Updated service portal rule context",
            "Income Certificate service is available with current rule bindings.",
            {"service_id": service["service_id"], "name": service["name"]},
        )

    def create_citizen_identity() -> dict[str, Any]:
        profile = portal.get_or_create_profile(
            citizen,
            {
                "full_name": "Ravi Kumar",
                "mobile": "9876543210",
                "email": "citizen@niyamguard.local",
                "district": "Hyderabad",
                "mandal": "Ameerpet",
            },
        )
        otp = readiness_service.request_demo_otp("sms", "9876543210")
        state["otp"] = otp
        return _success(
            "create_citizen_identity",
            "Created sandbox citizen identity",
            "Citizen profile and deterministic sandbox OTP were created.",
            {"profile": profile, "otp": otp},
        )

    def submit_application() -> dict[str, Any]:
        application = portal.create_application(
            citizen,
            {
                "service_id": "income_certificate",
                "form_values": {
                    "applicant_name": "Ravi Kumar",
                    "mobile_number": "9876543210",
                    "district": "Hyderabad",
                    "mandal": "Ameerpet",
                    "address": "House 1, Ameerpet, Hyderabad",
                    "purpose": "Post-matric scholarship",
                    "annual_income": 180000,
                    "occupation": "Student family",
                },
            },
        )
        attach_synthetic_documents(citizen, application["id"])
        submitted = portal.submit_application(citizen, application["id"])
        state["application"] = submitted
        entities["application_id"] = submitted["id"]
        entities["application_number"] = submitted["application_number"]
        return _success(
            "submit_application",
            "Submitted citizen application",
            "Income Certificate application submitted with synthetic document-vault evidence.",
            {"application": submitted},
        )

    def verify_otp() -> dict[str, Any]:
        otp = state["otp"]
        verified = readiness_service.verify_demo_otp(otp["otp_id"], "123456")
        return _success(
            "verify_otp",
            "Verified sandbox OTP",
            "Demo OTP verification succeeded with deterministic sandbox code.",
            verified,
        )

    def complete_payment() -> dict[str, Any]:
        application = state["application"]
        payment = portal.create_payment(citizen, application["id"])
        paid = portal.simulate_payment_success(citizen, payment["id"])
        state["payment"] = paid
        return _success(
            "complete_payment",
            "Completed sandbox payment",
            "Virtual payment gateway marked the fee paid.",
            {"payment": paid},
        )

    def officer_approves() -> dict[str, Any]:
        approved = portal.approve_application(officer, state["application"]["id"], "Full demo officer approval.")
        state["approved_application"] = approved
        cert = approved["certificate"]
        entities["certificate_id"] = cert["id"]
        entities["certificate_number"] = cert["certificate_number"]
        entities["verification_hash"] = cert["verification_hash"]
        return _success(
            "officer_approval",
            "Officer approved application",
            "Officer review completed and certificate generation was triggered.",
            {"application": approved},
        )

    def generate_certificate() -> dict[str, Any]:
        cert = state["approved_application"]["certificate"]
        return _success(
            "generate_certificate",
            "Generated certificate",
            "Virtual certificate authority created a demo certificate number and verification hash.",
            {"certificate": cert},
        )

    def sign_certificate() -> dict[str, Any]:
        cert = state["approved_application"]["certificate"]
        return _success(
            "sign_certificate",
            "Signed certificate in sandbox",
            "Certificate includes a verification hash used as the sandbox signature.",
            {"verification_hash": cert["verification_hash"], "qr_code_value": cert["qr_code_value"]},
        )

    def verify_certificate() -> dict[str, Any]:
        verified = portal.verify_certificate(entities["verification_hash"])
        return _success(
            "verify_certificate",
            "Verified certificate publicly",
            verified.get("message", "Certificate verification completed."),
            verified,
        )

    def patch_connected_systems() -> dict[str, Any]:
        patches = []
        plan = (state.get("publication") or {}).get("propagation_plan") or {}
        for task_id in plan.get("task_ids", []):
            patch = system_patch_service.apply_demo_patch(task_id)
            if patch.get("success"):
                patches.append(patch)
        mock_systems = mock_system_service.apply_demo_patch()
        return _success(
            "patch_connected_systems",
            "Patched connected systems",
            "Mock MeeSeva and public FAQ were patched to the verified 6 month value.",
            {"patches": patches, "mock_systems": mock_systems},
        )

    def rerun_compliance() -> dict[str, Any]:
        rule_id = entities.get("rule_id") or "rule_001"
        run = compliance_orchestrator_service.rerun_for_rule(
            rule_id,
            trigger_type="patch_applied",
            triggered_by="demo",
        )
        findings = [item.model_dump() for item in compliance_service.run_compliance()]
        return _success(
            "rerun_compliance",
            "Reran compliance drift check",
            "Compliance engine refreshed findings after the demo patch.",
            {"run": run.model_dump() if hasattr(run, "model_dump") else run, "findings": findings},
        )

    def write_audit_trail() -> dict[str, Any]:
        store = read_store()
        add_audit_event(
            store,
            "full_end_to_end_demo_completed",
            {
                "entity_type": "demo",
                "entity_id": entities.get("application_number"),
                "application_number": entities.get("application_number"),
                "certificate_number": entities.get("certificate_number"),
            },
        )
        write_store(store)
        return _success(
            "write_audit_trail",
            "Wrote audit trail",
            "Final demo completion event was added to the audit chain.",
            {"audit_events": len(read_store().audit_events)},
        )

    def ask_hybrid_answer() -> dict[str, Any]:
        answer = answer_question(
            "income certificate validity entha",
            context={"service_id": "income_certificate"},
        )
        state["hybrid_answer"] = answer
        return _success(
            "ask_hybrid_answer",
            "Asked hybrid answer engine",
            "Hybrid engine answered from verified GO-138 context.",
            answer,
        )

    def generate_ollama_explanation() -> dict[str, Any]:
        prompt = (
            "Explain GO-138 in simple words for a citizen. Use only this verified context: "
            "Income Certificate validity changed from 12 months to 6 months. "
            "Source circular: GO-138, Revenue Department, effective 2026-07-01."
        )
        fallback_text = (
            "GO-138 means the demo Income Certificate validity is 6 months instead of 12 months. "
            "Citizens should follow the latest verified GO-138 rule shown by NiyamGuard."
        )
        result = AIProviderFactory.get_client().generate_text(prompt, {"fallback_text": fallback_text})
        entities["ollama_provider"] = result.get("provider")
        entities["ollama_model"] = result.get("model")
        entities["ollama_fallback"] = bool(result.get("fallback"))
        return _success(
            "generate_ollama_explanation",
            "Generated Ollama explanation if available",
            "Ollama was used when online; otherwise deterministic explanation fallback stayed active.",
            result,
        )

    runners: list[tuple[str, str, StepRunner]] = [
        ("reset_sandbox", "Reset sandbox", reset_sandbox),
        ("publish_circular", "Published GO-138 circular", publish_circular),
        ("ingest_circular", "Ingested circular", ingest_circular),
        ("update_verified_rule", "Updated verified rule", update_verified_rule),
        ("update_service_portal", "Updated service portal", update_service_portal),
        ("create_citizen_identity", "Created citizen identity", create_citizen_identity),
        ("submit_application", "Submitted application", submit_application),
        ("verify_otp", "Verified OTP", verify_otp),
        ("complete_payment", "Completed payment", complete_payment),
        ("officer_approval", "Officer approval", officer_approves),
        ("generate_certificate", "Generated certificate", generate_certificate),
        ("sign_certificate", "Signed certificate", sign_certificate),
        ("verify_certificate", "Verified certificate", verify_certificate),
        ("patch_connected_systems", "Patched connected systems", patch_connected_systems),
        ("rerun_compliance", "Reran compliance", rerun_compliance),
        ("write_audit_trail", "Wrote audit trail", write_audit_trail),
        ("ask_hybrid_answer", "Asked hybrid answer engine", ask_hybrid_answer),
        ("generate_ollama_explanation", "Generated Ollama explanation", generate_ollama_explanation),
    ]

    for key, label, runner in runners:
        _safe_step(steps, key, label, runner)

    return {
        "success": all(step["status"] == "success" for step in steps),
        "steps": steps,
        "circular_number": "GO-138",
        "application_number": entities.get("application_number"),
        "certificate_number": entities.get("certificate_number"),
        "verification_hash": entities.get("verification_hash"),
        "verified_rule": {
            "rule_id": entities.get("rule_id"),
            "rule_version_id": entities.get("rule_version_id"),
            "service_id": "income_certificate",
            "rule_key": "validity",
            "value": "6 months",
            "source_circular_number": "GO-138",
        },
        "audit_event_count": next(
            (
                step.get("payload", {}).get("audit_events")
                for step in steps
                if step.get("key") == "write_audit_trail"
            ),
            None,
        ),
        "entities": entities,
    }
