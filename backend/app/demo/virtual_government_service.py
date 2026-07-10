from __future__ import annotations

from uuid import uuid4

from app.models.service_portal_models import ApplicationDocument, CitizenDocument
from app.models.virtual_gov_models import VirtualScenarioResult, VirtualScenarioStep
from app.security.rbac import CurrentUser
from app.services import dataset_service
from app.services.hybrid_intelligence.hybrid_answer_service import answer_question
from app.knowledge_base.platform_store import add_audit_event, read_store, reset_demo_store, write_store
from app.services import service_portal_service as portal
from app.services.time import now_iso


SCENARIOS = [
    {
        "scenario_id": "income_certificate_full_flow",
        "title": "Income certificate regulation-to-certificate sandbox",
        "description": "Asks a regulation question, creates a citizen application, completes payment, approves it, issues a certificate, and verifies audit evidence.",
        "service_id": "income_certificate",
    }
]


def catalog() -> dict:
    return {"success": True, "scenarios": SCENARIOS}


def status() -> dict:
    store = read_store()
    return {
        "success": True,
        "sandbox": "virtual_government",
        "applications": len(store.applications),
        "certificates": len(store.certificates),
        "payments": len(store.payment_records),
        "audit_events": len(store.audit_events),
        "scenarios": len(SCENARIOS),
    }


def run_scenario(scenario_id: str = "income_certificate_full_flow", *, reset_before_run: bool = True) -> dict:
    if scenario_id != "income_certificate_full_flow":
        return {"success": False, "error": "Scenario not found in available dataset."}
    if reset_before_run:
        reset_demo_store(persist=True)

    citizen = CurrentUser(id="user_citizen", email="citizen@niyamguard.local", role="citizen")
    officer = CurrentUser(id="user_officer", email="officer@niyamguard.local", role="reviewer")
    steps: list[VirtualScenarioStep] = []

    regulation_answer = answer_question(
        "income certificate validity entha",
        context={"service_id": "income_certificate"},
    )
    steps.append(
        VirtualScenarioStep(
            step_id="regulation_question",
            title="User asks about a regulation",
            payload=regulation_answer,
        )
    )

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
    steps.append(
        VirtualScenarioStep(
            step_id="application_created",
            title="Citizen application is created",
            payload={"application_id": application["id"], "application_number": application["application_number"]},
        )
    )

    attach_synthetic_documents(citizen, application["id"])
    submitted = portal.submit_application(citizen, application["id"])
    steps.append(
        VirtualScenarioStep(
            step_id="application_submitted",
            title="Evidence attached and application submitted",
            payload={"status": submitted["status"], "missing_items": []},
        )
    )

    payment = portal.create_payment(citizen, application["id"])
    paid = portal.simulate_payment_success(citizen, payment["id"])
    steps.append(
        VirtualScenarioStep(
            step_id="payment_completed",
            title="Sandbox payment completed",
            payload={"payment_reference": paid["payment_reference"], "payment_status": paid["payment_status"]},
        )
    )

    approved = portal.approve_application(officer, application["id"], "Virtual sandbox review approved.")
    certificate = approved["certificate"]
    verified = portal.verify_certificate(certificate["verification_hash"])
    steps.append(
        VirtualScenarioStep(
            step_id="certificate_issued",
            title="Officer approves and certificate is issued",
            payload={
                "application_status": approved["status"],
                "certificate_number": certificate["certificate_number"],
                "certificate_valid": verified["valid"],
            },
        )
    )

    demo_flow = dataset_service.demo_flow()
    steps.append(
        VirtualScenarioStep(
            step_id="compliance_demo_flow",
            title="Dataset gap, drift, risk, evidence, and audit context retrieved",
            payload=demo_flow,
        )
    )

    tracked = portal.track_application(approved["application_number"])
    result = VirtualScenarioResult(
        success=True,
        scenario_id=scenario_id,
        title="Income certificate regulation-to-certificate sandbox",
        steps=steps,
        artifacts={
            "application_number": approved["application_number"],
            "certificate_number": certificate["certificate_number"],
            "verification_hash": certificate["verification_hash"],
            "tracking": tracked,
            "source_rule": regulation_answer.get("sources", [{}])[0],
        },
    )
    return result.model_dump()


def attach_synthetic_documents(actor: CurrentUser, application_id: str) -> None:
    store = read_store()
    application = next(item for item in store.applications if item.id == application_id)
    timestamp = now_iso()
    for document_type in ("aadhaar", "income_proof", "address_proof"):
        doc = ApplicationDocument(
            id=f"appdoc_{uuid4().hex}",
            application_id=application_id,
            document_type=document_type,
            file_name=f"{document_type}.pdf",
            storage_path=f"storage/documents/virtual/{application_id}/{document_type}.pdf",
            mime_type="application/pdf",
            file_size=128,
            verification_status="accepted",
            uploaded_at=timestamp,
        )
        store.application_documents.append(doc)
        store.citizen_documents.append(
            CitizenDocument(
                id=f"citdoc_{uuid4().hex}",
                citizen_user_id=application.citizen_user_id,
                document_type=document_type,
                file_name=doc.file_name,
                storage_path=doc.storage_path,
                mime_type=doc.mime_type,
                file_size=doc.file_size,
                created_at=timestamp,
            )
        )
    add_audit_event(
        store,
        "virtual_government_documents_attached",
        {
            "entity_type": "application",
            "entity_id": application_id,
            "actor_user_id": actor.id,
            "document_types": ["aadhaar", "income_proof", "address_proof"],
        },
    )
    write_store(store)
