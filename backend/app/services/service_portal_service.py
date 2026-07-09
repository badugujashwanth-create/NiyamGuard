from __future__ import annotations

import calendar
import hashlib
import mimetypes
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import UploadFile, status

from app.models.platform_store_models import PolicyDataStore
from app.models.service_portal_models import (
    Application,
    ApplicationAssignment,
    ApplicationComment,
    ApplicationDocument,
    ApplicationFieldValue,
    ApplicationStatus,
    ApplicationStatusHistory,
    Certificate,
    CertificateVerificationLog,
    CitizenDocument,
    CitizenProfile,
    Notification,
    OfficerReview,
    PaymentRecord,
    ServiceDefinition,
    ServiceFormDefinition,
)
from app.security.rbac import CurrentUser
from app.services.platform_store import add_audit_event, read_store, write_store
from app.services.time import now_iso


BASE_DIR = Path(__file__).resolve().parents[1]
STORAGE_DIR = BASE_DIR / "storage"
DOCUMENT_STORAGE_DIR = STORAGE_DIR / "documents"
CERTIFICATE_STORAGE_DIR = STORAGE_DIR / "certificates"
MAX_UPLOAD_BYTES = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}
ALLOWED_MIME_TYPES = {"application/pdf", "image/jpeg", "image/png"}


class ServicePortalError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


def _now_dt() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def _date_string(days_from_now: int = 0) -> str:
    return (_now_dt().date() + timedelta(days=days_from_now)).isoformat()


def _actor_can_review(actor: CurrentUser) -> bool:
    return actor.role in {"admin", "reviewer"}


def _service(store: PolicyDataStore, service_id: str) -> ServiceDefinition:
    service = next((item for item in store.service_definitions if item.service_id == service_id and item.enabled), None)
    if service is None:
        raise ServicePortalError(status.HTTP_404_NOT_FOUND, "Service not found.")
    return service


def _form(store: PolicyDataStore, service_id: str) -> ServiceFormDefinition:
    form = next(
        (
            item
            for item in store.service_form_definitions
            if item.service_id == service_id and item.is_current
        ),
        None,
    )
    if form is None:
        raise ServicePortalError(status.HTTP_404_NOT_FOUND, "Service form not found.")
    return form


def _application(store: PolicyDataStore, application_id: str) -> Application:
    application = next((item for item in store.applications if item.id == application_id), None)
    if application is None:
        raise ServicePortalError(status.HTTP_404_NOT_FOUND, "Application not found.")
    return application


def _payment(store: PolicyDataStore, payment_id: str) -> PaymentRecord:
    payment = next((item for item in store.payment_records if item.id == payment_id), None)
    if payment is None:
        raise ServicePortalError(status.HTTP_404_NOT_FOUND, "Payment not found.")
    return payment


def _certificate(store: PolicyDataStore, certificate_id: str) -> Certificate:
    certificate = next((item for item in store.certificates if item.id == certificate_id), None)
    if certificate is None:
        raise ServicePortalError(status.HTTP_404_NOT_FOUND, "Certificate not found.")
    return certificate


def _assert_application_access(actor: CurrentUser, application: Application) -> None:
    if _actor_can_review(actor) or application.citizen_user_id == actor.id:
        return
    raise ServicePortalError(status.HTTP_403_FORBIDDEN, "You do not have access to this application.")


def _assert_review_access(actor: CurrentUser) -> None:
    if not _actor_can_review(actor):
        raise ServicePortalError(status.HTTP_403_FORBIDDEN, "Officer access required.")


def _next_number(store: PolicyDataStore, service: ServiceDefinition, collection: str, prefix: str) -> str:
    code = service.rule_bindings_json.get("application_code") or service.service_id[:3].upper()
    year = str(_now_dt().year)
    stem = f"{prefix}-{year}-{code}-"
    existing = getattr(store, collection)
    used: list[int] = []
    for item in existing:
        number = getattr(item, "application_number", None) or getattr(item, "certificate_number", None)
        if isinstance(number, str) and number.startswith(stem):
            try:
                used.append(int(number.rsplit("-", 1)[-1]))
            except ValueError:
                continue
    return f"{stem}{(max(used) + 1 if used else 1):06d}"


def _upsert_field_values(store: PolicyDataStore, application: Application, values: dict[str, Any]) -> None:
    timestamp = now_iso()
    for key, value in values.items():
        existing = next(
            (
                item
                for item in store.application_field_values
                if item.application_id == application.id and item.field_key == key
            ),
            None,
        )
        if existing:
            existing.value_json = value
            existing.updated_at = timestamp
            continue
        store.application_field_values.append(
            ApplicationFieldValue(
                id=f"field_{uuid4().hex}",
                application_id=application.id,
                field_key=key,
                value_json=value,
                created_at=timestamp,
                updated_at=timestamp,
            )
        )


def _history(
    store: PolicyDataStore,
    application: Application,
    status_value: ApplicationStatus,
    actor: CurrentUser | None,
    note: str | None = None,
) -> None:
    store.application_status_history.append(
        ApplicationStatusHistory(
            id=f"hist_{uuid4().hex}",
            application_id=application.id,
            status=status_value,
            note=note,
            actor_user_id=actor.id if actor else None,
            created_at=now_iso(),
        )
    )


def _notify(
    store: PolicyDataStore,
    user_id: str | None,
    notification_type: str,
    title: str,
    message: str,
    *,
    entity_type: str | None = None,
    entity_id: str | None = None,
) -> None:
    if not user_id:
        return
    store.notifications.append(
        Notification(
            id=f"not_{uuid4().hex}",
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            read=False,
            entity_type=entity_type,
            entity_id=entity_id,
            created_at=now_iso(),
        )
    )


def _audit(store: PolicyDataStore, action: str, actor: CurrentUser | None, payload: dict[str, Any]) -> None:
    add_audit_event(
        store,
        action,
        {
            **payload,
            "actor_user_id": actor.id if actor else None,
            "actor_email": actor.email if actor else None,
            "actor_role": actor.role if actor else None,
        },
    )


def _required_field_keys(form: ServiceFormDefinition) -> set[str]:
    return {field["key"] for field in form.fields_json if field.get("required")}


def _required_document_keys(service: ServiceDefinition) -> set[str]:
    return {doc["key"] for doc in service.required_documents_json if doc.get("required")}


def _missing_submission_items(
    store: PolicyDataStore,
    application: Application,
    service: ServiceDefinition,
    form: ServiceFormDefinition,
) -> dict[str, list[str]]:
    values = application.form_values_json
    missing_fields = [
        key
        for key in sorted(_required_field_keys(form))
        if values.get(key) in (None, "", [])
    ]
    uploaded = {
        doc.document_type
        for doc in store.application_documents
        if doc.application_id == application.id
    }
    missing_documents = sorted(_required_document_keys(service) - uploaded)
    return {"missing_fields": missing_fields, "missing_documents": missing_documents}


def _latest_rule_version(store: PolicyDataStore, service_id: str, rule_key: str):
    versions = [
        item
        for item in store.verified_policy_rule_versions
        if item.service_id == service_id and item.rule_key == rule_key and item.is_current
    ]
    if versions:
        return sorted(versions, key=lambda item: item.published_at or item.effective_date)[-1]
    return None


def _add_months(value: datetime, months: int) -> datetime:
    month = value.month - 1 + months
    year = value.year + month // 12
    month = month % 12 + 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return value.replace(year=year, month=month, day=day)


def _certificate_expiry(store: PolicyDataStore, service: ServiceDefinition, issued_at: datetime) -> tuple[str | None, str | None]:
    if service.service_id != "income_certificate":
        return None, None
    rule_version = _latest_rule_version(store, service.service_id, "validity")
    if rule_version is None:
        return None, None
    try:
        months = int(str(rule_version.value))
    except ValueError:
        return None, rule_version.id
    return _add_months(issued_at, months).date().isoformat(), rule_version.id


def _status_stage(status_value: str) -> str:
    return {
        "draft": "Draft",
        "payment_pending": "Payment pending",
        "under_review": "Officer review",
        "documents_required": "Documents requested",
        "approved": "Approved",
        "rejected": "Rejected",
        "certificate_issued": "Certificate issued",
        "closed": "Closed",
    }.get(status_value, "Submitted")


def _application_payload(store: PolicyDataStore, application: Application) -> dict[str, Any]:
    service = _service(store, application.service_id)
    documents = [
        item.model_dump()
        for item in store.application_documents
        if item.application_id == application.id
    ]
    payments = [
        item.model_dump()
        for item in store.payment_records
        if item.application_id == application.id
    ]
    certificate = (
        next((item.model_dump() for item in store.certificates if item.id == application.certificate_id), None)
        if application.certificate_id
        else None
    )
    sla = get_application_sla(application.id, store=store)
    return {
        **application.model_dump(),
        "service": service.model_dump(),
        "documents": documents,
        "payments": payments,
        "certificate": certificate,
        "sla": sla,
    }


def _certificate_text(certificate: Certificate, application: Application, service: ServiceDefinition) -> str:
    applicant = application.form_values_json.get("applicant_name", "Applicant")
    expires = certificate.expires_at or "Not time limited in this demo dataset"
    return (
        "NiyamGuard Service Portal Demo Certificate\n"
        f"Certificate Number: {certificate.certificate_number}\n"
        f"Service: {service.name}\n"
        f"Applicant: {applicant}\n"
        f"Application Number: {application.application_number}\n"
        f"Issued At: {certificate.issued_at}\n"
        f"Expires At: {expires}\n"
        f"Verification Hash: {certificate.verification_hash}\n"
        "This is a synthetic demo certificate generated by NiyamGuard Service Portal.\n"
    )


def list_services() -> list[dict[str, Any]]:
    store = read_store()
    return [item.model_dump() for item in store.service_definitions if item.enabled]


def get_service(service_id: str) -> dict[str, Any]:
    store = read_store()
    service = _service(store, service_id)
    form = _form(store, service_id)
    return {**service.model_dump(), "form": form.model_dump()}


def get_service_form(service_id: str) -> dict[str, Any]:
    store = read_store()
    return _form(store, service_id).model_dump()


def get_or_create_profile(actor: CurrentUser, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    store = read_store()
    existing = next((item for item in store.citizen_profiles if item.user_id == actor.id), None)
    timestamp = now_iso()
    if existing is None:
        profile = CitizenProfile(
            id=f"profile_{uuid4().hex}",
            user_id=actor.id,
            full_name=payload.get("full_name") if payload else actor.email.split("@", 1)[0].replace(".", " ").title(),
            date_of_birth=payload.get("date_of_birth") if payload else None,
            gender=payload.get("gender") if payload else None,
            mobile=payload.get("mobile") if payload else None,
            email=payload.get("email") if payload else actor.email,
            address_line1=payload.get("address_line1") if payload else None,
            address_line2=payload.get("address_line2") if payload else None,
            district=payload.get("district") if payload else None,
            mandal=payload.get("mandal") if payload else None,
            village=payload.get("village") if payload else None,
            pincode=payload.get("pincode") if payload else None,
            created_at=timestamp,
            updated_at=timestamp,
        )
        store.citizen_profiles.append(profile)
        _audit(store, "citizen_profile_created", actor, {"entity_type": "citizen_profile", "entity_id": profile.id})
        write_store(store)
        return profile.model_dump()
    if payload:
        for key, value in payload.items():
            if hasattr(existing, key):
                setattr(existing, key, value)
        existing.updated_at = timestamp
        _audit(store, "citizen_profile_updated", actor, {"entity_type": "citizen_profile", "entity_id": existing.id})
        write_store(store)
    return existing.model_dump()


def create_application(actor: CurrentUser, payload: dict[str, Any]) -> dict[str, Any]:
    store = read_store()
    service = _service(store, payload["service_id"])
    form = _form(store, service.service_id)
    timestamp = now_iso()
    application = Application(
        id=f"app_{uuid4().hex}",
        application_number=_next_number(store, service, "applications", "NGSP"),
        citizen_user_id=actor.id,
        service_id=service.service_id,
        status="draft",
        current_stage="Draft",
        submitted_at=None,
        assigned_officer_id=None,
        district=payload.get("district") or payload.get("form_values", {}).get("district"),
        mandal=payload.get("mandal") or payload.get("form_values", {}).get("mandal"),
        fee_status="pending" if service.fee_amount > 0 else "not_required",
        certificate_id=None,
        source_rule_version_id=service.rule_bindings_json.get("latest_rule_id"),
        form_values_json=payload.get("form_values", {}),
        rejection_reason=None,
        due_date=None,
        created_at=timestamp,
        updated_at=timestamp,
    )
    store.applications.append(application)
    _upsert_field_values(store, application, application.form_values_json)
    _history(store, application, "draft", actor, "Application draft created.")
    _notify(
        store,
        actor.id,
        "application_submitted",
        "Draft application created",
        f"{service.name} draft {application.application_number} was created.",
        entity_type="application",
        entity_id=application.id,
    )
    _audit(
        store,
        "service_application_created",
        actor,
        {"entity_type": "application", "entity_id": application.id, "service_id": service.service_id},
    )
    write_store(store)
    return _application_payload(store, application)


def update_application(actor: CurrentUser, application_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    store = read_store()
    application = _application(store, application_id)
    _assert_application_access(actor, application)
    if application.status not in {"draft", "documents_required", "payment_pending"} and not _actor_can_review(actor):
        raise ServicePortalError(status.HTTP_409_CONFLICT, "Submitted applications can only be changed when documents are requested.")
    values = payload.get("form_values", {})
    application.form_values_json = {**application.form_values_json, **values}
    application.district = payload.get("district") or application.form_values_json.get("district") or application.district
    application.mandal = payload.get("mandal") or application.form_values_json.get("mandal") or application.mandal
    application.updated_at = now_iso()
    _upsert_field_values(store, application, values)
    _audit(store, "service_application_updated", actor, {"entity_type": "application", "entity_id": application.id})
    write_store(store)
    return _application_payload(store, application)


async def upload_application_document(
    actor: CurrentUser,
    application_id: str,
    document_type: str,
    file: UploadFile,
) -> dict[str, Any]:
    store = read_store()
    application = _application(store, application_id)
    _assert_application_access(actor, application)
    suffix = Path(file.filename or "").suffix.lower()
    content_type = file.content_type or mimetypes.guess_type(file.filename or "")[0] or ""
    if suffix not in ALLOWED_EXTENSIONS or content_type not in ALLOWED_MIME_TYPES:
        raise ServicePortalError(status.HTTP_400_BAD_REQUEST, "Only PDF, JPG, JPEG, and PNG files are accepted.")
    content = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(content) > MAX_UPLOAD_BYTES:
        raise ServicePortalError(status.HTTP_400_BAD_REQUEST, "Uploaded document exceeds the 5 MB limit.")
    destination_dir = DOCUMENT_STORAGE_DIR / application.id
    destination_dir.mkdir(parents=True, exist_ok=True)
    safe_name = "".join(char if char.isalnum() or char in {".", "-", "_"} else "_" for char in (file.filename or "document"))
    destination = destination_dir / f"{uuid4().hex}_{safe_name}"
    destination.write_bytes(content)
    document = ApplicationDocument(
        id=f"appdoc_{uuid4().hex}",
        application_id=application.id,
        document_type=document_type,
        file_name=file.filename or "document",
        storage_path=str(destination.relative_to(BASE_DIR)),
        mime_type=content_type,
        file_size=len(content),
        verification_status="pending",
        uploaded_at=now_iso(),
    )
    store.application_documents.append(document)
    citizen_doc = CitizenDocument(
        id=f"citdoc_{uuid4().hex}",
        citizen_user_id=application.citizen_user_id,
        document_type=document_type,
        file_name=document.file_name,
        storage_path=document.storage_path,
        mime_type=document.mime_type,
        file_size=document.file_size,
        created_at=document.uploaded_at,
    )
    store.citizen_documents.append(citizen_doc)
    if application.status == "documents_required":
        application.status = "under_review"
        application.current_stage = _status_stage(application.status)
        application.updated_at = now_iso()
        _history(store, application, "under_review", actor, "Requested document uploaded.")
    _audit(
        store,
        "service_application_document_uploaded",
        actor,
        {"entity_type": "application_document", "entity_id": document.id, "application_id": application.id},
    )
    write_store(store)
    return document.model_dump()


def submit_application(actor: CurrentUser, application_id: str) -> dict[str, Any]:
    store = read_store()
    application = _application(store, application_id)
    _assert_application_access(actor, application)
    service = _service(store, application.service_id)
    form = _form(store, application.service_id)
    missing = _missing_submission_items(store, application, service, form)
    if missing["missing_fields"] or missing["missing_documents"]:
        raise ServicePortalError(status.HTTP_422_UNPROCESSABLE_ENTITY, f"Missing required items: {missing}")
    application.submitted_at = application.submitted_at or now_iso()
    application.due_date = application.due_date or _date_string(service.processing_days)
    application.status = "payment_pending" if service.fee_amount > 0 and application.fee_status != "paid" else "under_review"
    application.current_stage = _status_stage(application.status)
    application.updated_at = now_iso()
    _history(store, application, application.status, actor, "Application submitted.")
    _notify(
        store,
        actor.id,
        "application_submitted",
        "Application submitted",
        f"{application.application_number} is now {application.current_stage.lower()}.",
        entity_type="application",
        entity_id=application.id,
    )
    _audit(
        store,
        "service_application_submitted",
        actor,
        {"entity_type": "application", "entity_id": application.id, "status": application.status},
    )
    write_store(store)
    return _application_payload(store, application)


def list_applications(actor: CurrentUser, *, status_filter: str | None = None) -> list[dict[str, Any]]:
    store = read_store()
    applications = store.applications if _actor_can_review(actor) else [
        item for item in store.applications if item.citizen_user_id == actor.id
    ]
    if status_filter:
        applications = [item for item in applications if item.status == status_filter]
    return [_application_payload(store, item) for item in sorted(applications, key=lambda item: item.created_at, reverse=True)]


def get_application(actor: CurrentUser, application_id: str) -> dict[str, Any]:
    store = read_store()
    application = _application(store, application_id)
    _assert_application_access(actor, application)
    return _application_payload(store, application)


def get_application_history(actor: CurrentUser, application_id: str) -> list[dict[str, Any]]:
    store = read_store()
    application = _application(store, application_id)
    _assert_application_access(actor, application)
    return [
        item.model_dump()
        for item in store.application_status_history
        if item.application_id == application.id
    ]


def track_application(application_number: str) -> dict[str, Any]:
    store = read_store()
    application = next((item for item in store.applications if item.application_number == application_number), None)
    if application is None:
        raise ServicePortalError(status.HTTP_404_NOT_FOUND, "Application not found in available dataset.")
    service = _service(store, application.service_id)
    history = [
        item.model_dump()
        for item in store.application_status_history
        if item.application_id == application.id
    ]
    return {
        "application_number": application.application_number,
        "service_name": service.name,
        "status": application.status,
        "current_stage": application.current_stage,
        "submitted_at": application.submitted_at,
        "due_date": application.due_date,
        "sla": get_application_sla(application.id, store=store),
        "history": history,
    }


def create_payment(actor: CurrentUser, application_id: str) -> dict[str, Any]:
    store = read_store()
    application = _application(store, application_id)
    _assert_application_access(actor, application)
    service = _service(store, application.service_id)
    if service.fee_amount <= 0:
        raise ServicePortalError(status.HTTP_409_CONFLICT, "This service does not require a payment.")
    existing = next(
        (
            item
            for item in store.payment_records
            if item.application_id == application.id and item.payment_status == "created"
        ),
        None,
    )
    if existing:
        return existing.model_dump()
    payment = PaymentRecord(
        id=f"pay_{uuid4().hex}",
        application_id=application.id,
        amount=service.fee_amount,
        payment_status="created",
        payment_reference=f"NGPAY-{_now_dt().year}-{uuid4().hex[:8].upper()}",
        payment_mode="sandbox",
        paid_at=None,
        created_at=now_iso(),
    )
    store.payment_records.append(payment)
    application.fee_status = "pending"
    application.status = "payment_pending"
    application.current_stage = _status_stage(application.status)
    application.updated_at = now_iso()
    _history(store, application, "payment_pending", actor, "Sandbox payment created.")
    _audit(store, "service_payment_created", actor, {"entity_type": "payment", "entity_id": payment.id})
    write_store(store)
    return payment.model_dump()


def simulate_payment_success(actor: CurrentUser, payment_id: str) -> dict[str, Any]:
    store = read_store()
    payment = _payment(store, payment_id)
    application = _application(store, payment.application_id)
    _assert_application_access(actor, application)
    payment.payment_status = "paid"
    payment.paid_at = now_iso()
    application.fee_status = "paid"
    if application.submitted_at:
        application.status = "under_review"
        application.current_stage = _status_stage(application.status)
        _history(store, application, "under_review", actor, "Payment completed.")
    application.updated_at = now_iso()
    _notify(
        store,
        application.citizen_user_id,
        "payment_success",
        "Payment successful",
        f"Sandbox payment for {application.application_number} was marked paid.",
        entity_type="payment",
        entity_id=payment.id,
    )
    _audit(store, "service_payment_success", actor, {"entity_type": "payment", "entity_id": payment.id})
    write_store(store)
    return payment.model_dump()


def simulate_payment_failure(actor: CurrentUser, payment_id: str) -> dict[str, Any]:
    store = read_store()
    payment = _payment(store, payment_id)
    application = _application(store, payment.application_id)
    _assert_application_access(actor, application)
    payment.payment_status = "failed"
    application.fee_status = "failed"
    application.status = "payment_pending"
    application.current_stage = _status_stage(application.status)
    application.updated_at = now_iso()
    _history(store, application, "payment_pending", actor, "Sandbox payment failed.")
    _audit(store, "service_payment_failed", actor, {"entity_type": "payment", "entity_id": payment.id})
    write_store(store)
    return payment.model_dump()


def list_payments(actor: CurrentUser, application_id: str) -> list[dict[str, Any]]:
    store = read_store()
    application = _application(store, application_id)
    _assert_application_access(actor, application)
    return [item.model_dump() for item in store.payment_records if item.application_id == application.id]


def assign_application(actor: CurrentUser, application_id: str, officer_user_id: str | None = None) -> dict[str, Any]:
    _assert_review_access(actor)
    store = read_store()
    application = _application(store, application_id)
    officer_id = officer_user_id or actor.id
    application.assigned_officer_id = officer_id
    application.updated_at = now_iso()
    assignment = ApplicationAssignment(
        id=f"assign_{uuid4().hex}",
        application_id=application.id,
        officer_user_id=officer_id,
        assigned_by=actor.id,
        assigned_at=now_iso(),
    )
    store.application_assignments.append(assignment)
    _notify(
        store,
        officer_id,
        "application_assigned",
        "Application assigned",
        f"{application.application_number} is assigned for review.",
        entity_type="application",
        entity_id=application.id,
    )
    _audit(store, "service_application_assigned", actor, {"entity_type": "application", "entity_id": application.id})
    write_store(store)
    return _application_payload(store, application)


def request_documents(actor: CurrentUser, application_id: str, notes: str, requested_documents: list[str]) -> dict[str, Any]:
    _assert_review_access(actor)
    store = read_store()
    application = _application(store, application_id)
    application.status = "documents_required"
    application.current_stage = _status_stage(application.status)
    application.updated_at = now_iso()
    review = OfficerReview(
        id=f"review_{uuid4().hex}",
        application_id=application.id,
        officer_user_id=actor.id,
        decision="documents_required",
        notes=notes,
        requested_documents_json=requested_documents,
        reviewed_at=now_iso(),
    )
    store.officer_reviews.append(review)
    _history(store, application, "documents_required", actor, notes or "Additional documents requested.")
    _notify(
        store,
        application.citizen_user_id,
        "documents_requested",
        "Documents requested",
        notes or "Please upload the requested documents.",
        entity_type="application",
        entity_id=application.id,
    )
    _audit(store, "service_documents_requested", actor, {"entity_type": "application", "entity_id": application.id})
    write_store(store)
    return _application_payload(store, application)


def approve_application(actor: CurrentUser, application_id: str, notes: str | None = None) -> dict[str, Any]:
    _assert_review_access(actor)
    store = read_store()
    application = _application(store, application_id)
    service = _service(store, application.service_id)
    if application.status not in {"under_review", "approved"}:
        raise ServicePortalError(status.HTTP_409_CONFLICT, "Only applications under review can be approved.")
    issued_dt = _now_dt()
    expires_at, source_rule_version_id = _certificate_expiry(store, service, issued_dt)
    seed = f"{application.id}:{service.service_id}:{issued_dt.isoformat()}:{uuid4().hex}"
    verification_hash = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    certificate = Certificate(
        id=f"cert_{uuid4().hex}",
        certificate_number=_next_number(store, service, "certificates", "NGCERT"),
        application_id=application.id,
        service_id=service.service_id,
        citizen_user_id=application.citizen_user_id,
        issued_at=issued_dt.isoformat(),
        expires_at=expires_at,
        status="valid",
        pdf_path=None,
        qr_code_value=f"NGSP_VERIFY:{verification_hash}",
        verification_hash=verification_hash,
        source_rule_version_id=source_rule_version_id,
        created_at=now_iso(),
    )
    CERTIFICATE_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    pdf_path = CERTIFICATE_STORAGE_DIR / f"{certificate.id}.pdf"
    pdf_path.write_text(_certificate_text(certificate, application, service), encoding="utf-8")
    certificate.pdf_path = str(pdf_path.relative_to(BASE_DIR))
    store.certificates.append(certificate)
    review = OfficerReview(
        id=f"review_{uuid4().hex}",
        application_id=application.id,
        officer_user_id=actor.id,
        decision="approved",
        notes=notes,
        requested_documents_json=[],
        reviewed_at=now_iso(),
    )
    store.officer_reviews.append(review)
    application.status = "certificate_issued"
    application.current_stage = _status_stage(application.status)
    application.certificate_id = certificate.id
    application.source_rule_version_id = source_rule_version_id or application.source_rule_version_id
    application.updated_at = now_iso()
    _history(store, application, "approved", actor, notes or "Application approved.")
    _history(store, application, "certificate_issued", actor, "Certificate generated.")
    _notify(
        store,
        application.citizen_user_id,
        "application_approved",
        "Application approved",
        f"{application.application_number} was approved.",
        entity_type="application",
        entity_id=application.id,
    )
    _notify(
        store,
        application.citizen_user_id,
        "certificate_issued",
        "Certificate issued",
        f"Certificate {certificate.certificate_number} is ready.",
        entity_type="certificate",
        entity_id=certificate.id,
    )
    _audit(
        store,
        "service_application_approved",
        actor,
        {"entity_type": "application", "entity_id": application.id, "certificate_id": certificate.id},
    )
    write_store(store)
    return _application_payload(store, application)


def reject_application(actor: CurrentUser, application_id: str, reason: str) -> dict[str, Any]:
    _assert_review_access(actor)
    store = read_store()
    application = _application(store, application_id)
    application.status = "rejected"
    application.current_stage = _status_stage(application.status)
    application.rejection_reason = reason
    application.updated_at = now_iso()
    review = OfficerReview(
        id=f"review_{uuid4().hex}",
        application_id=application.id,
        officer_user_id=actor.id,
        decision="rejected",
        notes=reason,
        requested_documents_json=[],
        reviewed_at=now_iso(),
    )
    store.officer_reviews.append(review)
    _history(store, application, "rejected", actor, reason)
    _notify(
        store,
        application.citizen_user_id,
        "application_rejected",
        "Application rejected",
        reason,
        entity_type="application",
        entity_id=application.id,
    )
    _audit(store, "service_application_rejected", actor, {"entity_type": "application", "entity_id": application.id})
    write_store(store)
    return _application_payload(store, application)


def add_comment(actor: CurrentUser, application_id: str, comment: str) -> dict[str, Any]:
    store = read_store()
    application = _application(store, application_id)
    _assert_application_access(actor, application)
    item = ApplicationComment(
        id=f"comment_{uuid4().hex}",
        application_id=application.id,
        user_id=actor.id,
        comment=comment,
        created_at=now_iso(),
    )
    store.application_comments.append(item)
    _audit(store, "service_application_comment_added", actor, {"entity_type": "application_comment", "entity_id": item.id})
    write_store(store)
    return item.model_dump()


def get_certificate(actor: CurrentUser, certificate_id: str) -> dict[str, Any]:
    store = read_store()
    certificate = _certificate(store, certificate_id)
    application = _application(store, certificate.application_id)
    _assert_application_access(actor, application)
    return certificate.model_dump()


def get_certificate_bytes(actor: CurrentUser, certificate_id: str) -> tuple[str, bytes]:
    store = read_store()
    certificate = _certificate(store, certificate_id)
    application = _application(store, certificate.application_id)
    _assert_application_access(actor, application)
    if certificate.pdf_path:
        path = BASE_DIR / certificate.pdf_path
        if path.exists():
            return certificate.certificate_number, path.read_bytes()
    service = _service(store, certificate.service_id)
    return certificate.certificate_number, _certificate_text(certificate, application, service).encode("utf-8")


def verify_certificate(query: str) -> dict[str, Any]:
    store = read_store()
    certificate = next(
        (
            item
            for item in store.certificates
            if item.verification_hash == query or item.certificate_number == query
        ),
        None,
    )
    success = certificate is not None and certificate.status == "valid"
    store.certificate_verification_logs.append(
        CertificateVerificationLog(
            id=f"certlog_{uuid4().hex}",
            certificate_id=certificate.id if certificate else None,
            query=query,
            success=success,
            created_at=now_iso(),
        )
    )
    write_store(store)
    if certificate is None:
        return {"valid": False, "message": "Certificate not found in available dataset."}
    service = _service(store, certificate.service_id)
    application = _application(store, certificate.application_id)
    return {
        "valid": success,
        "message": "Certificate is valid." if success else f"Certificate is {certificate.status}.",
        "certificate": certificate.model_dump(),
        "service_name": service.name,
        "applicant_name": application.form_values_json.get("applicant_name"),
    }


def revoke_certificate(actor: CurrentUser, certificate_id: str, reason: str) -> dict[str, Any]:
    _assert_review_access(actor)
    store = read_store()
    certificate = _certificate(store, certificate_id)
    certificate.status = "revoked"
    _notify(
        store,
        certificate.citizen_user_id,
        "certificate_revoked",
        "Certificate revoked",
        reason,
        entity_type="certificate",
        entity_id=certificate.id,
    )
    _audit(store, "service_certificate_revoked", actor, {"entity_type": "certificate", "entity_id": certificate.id})
    write_store(store)
    return certificate.model_dump()


def list_notifications(actor: CurrentUser) -> list[dict[str, Any]]:
    store = read_store()
    return [
        item.model_dump()
        for item in sorted(store.notifications, key=lambda item: item.created_at, reverse=True)
        if item.user_id == actor.id
    ]


def mark_notification_read(actor: CurrentUser, notification_id: str) -> dict[str, Any]:
    store = read_store()
    notification = next((item for item in store.notifications if item.id == notification_id), None)
    if notification is None or notification.user_id != actor.id:
        raise ServicePortalError(status.HTTP_404_NOT_FOUND, "Notification not found.")
    notification.read = True
    write_store(store)
    return notification.model_dump()


def mark_all_notifications_read(actor: CurrentUser) -> list[dict[str, Any]]:
    store = read_store()
    results = []
    for notification in store.notifications:
        if notification.user_id == actor.id:
            notification.read = True
            results.append(notification.model_dump())
    write_store(store)
    return results


def list_citizen_documents(actor: CurrentUser) -> list[dict[str, Any]]:
    store = read_store()
    return [item.model_dump() for item in store.citizen_documents if item.citizen_user_id == actor.id]


def get_application_sla(application_id: str, *, store: PolicyDataStore | None = None) -> dict[str, Any]:
    local_store = store or read_store()
    application = _application(local_store, application_id)
    service = _service(local_store, application.service_id)
    if not application.due_date:
        return {
            "status": "not_started",
            "due_date": None,
            "processing_days": service.processing_days,
            "days_remaining": None,
        }
    due = date.fromisoformat(application.due_date)
    days_remaining = (due - _now_dt().date()).days
    if application.status in {"certificate_issued", "rejected", "closed"}:
        sla_status = "completed"
    elif days_remaining < 0:
        sla_status = "overdue"
    elif days_remaining <= 2:
        sla_status = "due_soon"
    else:
        sla_status = "within_sla"
    return {
        "status": sla_status,
        "due_date": application.due_date,
        "processing_days": service.processing_days,
        "days_remaining": days_remaining,
    }


def officer_queue(actor: CurrentUser, status_filter: str | None = None) -> list[dict[str, Any]]:
    _assert_review_access(actor)
    return list_applications(actor, status_filter=status_filter)
