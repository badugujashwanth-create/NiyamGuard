from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile
from pydantic import BaseModel, Field

from app.security.rbac import CurrentUser, get_current_user, require_roles
from app.services import service_portal_service as portal


router = APIRouter(tags=["Service Portal"])


class ApplicationRequest(BaseModel):
    service_id: str
    form_values: dict[str, Any] = Field(default_factory=dict)
    district: str | None = None
    mandal: str | None = None


class ApplicationUpdateRequest(BaseModel):
    form_values: dict[str, Any] = Field(default_factory=dict)
    district: str | None = None
    mandal: str | None = None


class ProfileRequest(BaseModel):
    full_name: str | None = None
    date_of_birth: str | None = None
    gender: str | None = None
    mobile: str | None = None
    email: str | None = None
    address_line1: str | None = None
    address_line2: str | None = None
    district: str | None = None
    mandal: str | None = None
    village: str | None = None
    pincode: str | None = None


class AssignRequest(BaseModel):
    officer_user_id: str | None = None


class RequestDocumentsRequest(BaseModel):
    notes: str = "Additional documents are required."
    requested_documents: list[str] = Field(default_factory=list)


class ApprovalRequest(BaseModel):
    notes: str | None = None


class RejectionRequest(BaseModel):
    reason: str = Field(min_length=1)


class CommentRequest(BaseModel):
    comment: str = Field(min_length=1)


class RevokeCertificateRequest(BaseModel):
    reason: str = Field(min_length=1)


def _handle_error(exc: portal.ServicePortalError) -> None:
    raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc


@router.get("/api/portal/services")
def list_portal_services() -> dict:
    return {"success": True, "services": portal.list_services()}


@router.get("/api/portal/services/{service_id}")
@router.get("/api/services/{service_id}")
def get_portal_service(service_id: str) -> dict:
    try:
        return {"success": True, "service": portal.get_service(service_id)}
    except portal.ServicePortalError as exc:
        _handle_error(exc)


@router.get("/api/portal/services/{service_id}/form")
def get_portal_service_form(service_id: str) -> dict:
    try:
        return {"success": True, "form": portal.get_service_form(service_id)}
    except portal.ServicePortalError as exc:
        _handle_error(exc)


@router.get("/api/citizen/profile")
def get_profile(actor: CurrentUser = Depends(get_current_user)) -> dict:
    try:
        return {"success": True, "profile": portal.get_or_create_profile(actor)}
    except portal.ServicePortalError as exc:
        _handle_error(exc)


@router.patch("/api/citizen/profile")
def update_profile(payload: ProfileRequest, actor: CurrentUser = Depends(get_current_user)) -> dict:
    try:
        return {"success": True, "profile": portal.get_or_create_profile(actor, payload.model_dump(exclude_none=True))}
    except portal.ServicePortalError as exc:
        _handle_error(exc)


@router.get("/api/citizen/documents")
def list_citizen_documents(actor: CurrentUser = Depends(get_current_user)) -> dict:
    return {"success": True, "documents": portal.list_citizen_documents(actor)}


@router.post("/api/applications", status_code=201)
def create_application(payload: ApplicationRequest, actor: CurrentUser = Depends(get_current_user)) -> dict:
    try:
        return {"success": True, "application": portal.create_application(actor, payload.model_dump())}
    except portal.ServicePortalError as exc:
        _handle_error(exc)


@router.get("/api/applications")
def list_applications(status: str | None = None, actor: CurrentUser = Depends(get_current_user)) -> dict:
    try:
        return {"success": True, "applications": portal.list_applications(actor, status_filter=status)}
    except portal.ServicePortalError as exc:
        _handle_error(exc)


@router.get("/api/applications/{application_id}")
def get_application(application_id: str, actor: CurrentUser = Depends(get_current_user)) -> dict:
    try:
        return {"success": True, "application": portal.get_application(actor, application_id)}
    except portal.ServicePortalError as exc:
        _handle_error(exc)


@router.patch("/api/applications/{application_id}")
def update_application(
    application_id: str,
    payload: ApplicationUpdateRequest,
    actor: CurrentUser = Depends(get_current_user),
) -> dict:
    try:
        return {"success": True, "application": portal.update_application(actor, application_id, payload.model_dump())}
    except portal.ServicePortalError as exc:
        _handle_error(exc)


@router.post("/api/applications/{application_id}/submit")
def submit_application(application_id: str, actor: CurrentUser = Depends(get_current_user)) -> dict:
    try:
        return {"success": True, "application": portal.submit_application(actor, application_id)}
    except portal.ServicePortalError as exc:
        _handle_error(exc)


@router.post("/api/applications/{application_id}/documents", status_code=201)
async def upload_document(
    application_id: str,
    document_type: str = Form(...),
    file: UploadFile = File(...),
    actor: CurrentUser = Depends(get_current_user),
) -> dict:
    try:
        document = await portal.upload_application_document(actor, application_id, document_type, file)
        return {"success": True, "document": document}
    except portal.ServicePortalError as exc:
        _handle_error(exc)


@router.get("/api/applications/{application_id}/documents")
def get_application_documents(application_id: str, actor: CurrentUser = Depends(get_current_user)) -> dict:
    try:
        application = portal.get_application(actor, application_id)
        return {"success": True, "documents": application["documents"]}
    except portal.ServicePortalError as exc:
        _handle_error(exc)


@router.get("/api/applications/{application_id}/status-history")
def get_application_history(application_id: str, actor: CurrentUser = Depends(get_current_user)) -> dict:
    try:
        return {"success": True, "history": portal.get_application_history(actor, application_id)}
    except portal.ServicePortalError as exc:
        _handle_error(exc)


@router.get("/api/applications/{application_id}/sla")
def get_application_sla(application_id: str, actor: CurrentUser = Depends(get_current_user)) -> dict:
    try:
        portal.get_application(actor, application_id)
        return {"success": True, "sla": portal.get_application_sla(application_id)}
    except portal.ServicePortalError as exc:
        _handle_error(exc)


@router.get("/api/track/{application_number}")
def track_application(application_number: str) -> dict:
    try:
        return {"success": True, "tracking": portal.track_application(application_number)}
    except portal.ServicePortalError as exc:
        _handle_error(exc)


@router.post("/api/payments/{application_id}/create", status_code=201)
def create_payment(application_id: str, actor: CurrentUser = Depends(get_current_user)) -> dict:
    try:
        return {"success": True, "payment": portal.create_payment(actor, application_id)}
    except portal.ServicePortalError as exc:
        _handle_error(exc)


@router.post("/api/payments/{payment_id}/simulate-success")
def simulate_payment_success(payment_id: str, actor: CurrentUser = Depends(get_current_user)) -> dict:
    try:
        return {"success": True, "payment": portal.simulate_payment_success(actor, payment_id)}
    except portal.ServicePortalError as exc:
        _handle_error(exc)


@router.post("/api/payments/{payment_id}/simulate-failure")
def simulate_payment_failure(payment_id: str, actor: CurrentUser = Depends(get_current_user)) -> dict:
    try:
        return {"success": True, "payment": portal.simulate_payment_failure(actor, payment_id)}
    except portal.ServicePortalError as exc:
        _handle_error(exc)


@router.get("/api/payments/{application_id}")
def list_payments(application_id: str, actor: CurrentUser = Depends(get_current_user)) -> dict:
    try:
        return {"success": True, "payments": portal.list_payments(actor, application_id)}
    except portal.ServicePortalError as exc:
        _handle_error(exc)


@router.get("/api/officer/applications")
def list_officer_applications(status: str | None = None, actor: CurrentUser = Depends(get_current_user)) -> dict:
    try:
        return {"success": True, "applications": portal.officer_queue(actor, status_filter=status)}
    except portal.ServicePortalError as exc:
        _handle_error(exc)


@router.get("/api/officer/applications/{application_id}")
def get_officer_application(application_id: str, actor: CurrentUser = Depends(get_current_user)) -> dict:
    try:
        return {"success": True, "application": portal.get_application(actor, application_id)}
    except portal.ServicePortalError as exc:
        _handle_error(exc)


@router.get("/api/officer/pending")
def get_officer_pending(actor: CurrentUser = Depends(get_current_user)) -> dict:
    try:
        applications = [
            item
            for status_value in ("under_review", "documents_required", "payment_pending")
            for item in portal.officer_queue(actor, status_filter=status_value)
        ]
        return {"success": True, "applications": applications}
    except portal.ServicePortalError as exc:
        _handle_error(exc)


@router.get("/api/officer/approved")
def get_officer_approved(actor: CurrentUser = Depends(get_current_user)) -> dict:
    try:
        return {"success": True, "applications": portal.officer_queue(actor, status_filter="certificate_issued")}
    except portal.ServicePortalError as exc:
        _handle_error(exc)


@router.get("/api/officer/rejected")
def get_officer_rejected(actor: CurrentUser = Depends(get_current_user)) -> dict:
    try:
        return {"success": True, "applications": portal.officer_queue(actor, status_filter="rejected")}
    except portal.ServicePortalError as exc:
        _handle_error(exc)


@router.get("/api/officer/escalations")
def get_officer_escalations(actor: CurrentUser = Depends(get_current_user)) -> dict:
    try:
        applications = [
            item
            for item in portal.officer_queue(actor)
            if item["sla"]["status"] in {"overdue", "due_soon"}
        ]
        return {"success": True, "applications": applications}
    except portal.ServicePortalError as exc:
        _handle_error(exc)


@router.post("/api/officer/applications/{application_id}/assign")
def assign_application(
    application_id: str,
    payload: AssignRequest,
    actor: CurrentUser = Depends(get_current_user),
) -> dict:
    try:
        return {"success": True, "application": portal.assign_application(actor, application_id, payload.officer_user_id)}
    except portal.ServicePortalError as exc:
        _handle_error(exc)


@router.post("/api/officer/applications/{application_id}/request-documents")
def request_documents(
    application_id: str,
    payload: RequestDocumentsRequest,
    actor: CurrentUser = Depends(get_current_user),
) -> dict:
    try:
        application = portal.request_documents(actor, application_id, payload.notes, payload.requested_documents)
        return {"success": True, "application": application}
    except portal.ServicePortalError as exc:
        _handle_error(exc)


@router.post("/api/officer/applications/{application_id}/approve")
def approve_application(
    application_id: str,
    payload: ApprovalRequest,
    actor: CurrentUser = Depends(get_current_user),
) -> dict:
    try:
        return {"success": True, "application": portal.approve_application(actor, application_id, payload.notes)}
    except portal.ServicePortalError as exc:
        _handle_error(exc)


@router.post("/api/officer/applications/{application_id}/reject")
def reject_application(
    application_id: str,
    payload: RejectionRequest,
    actor: CurrentUser = Depends(get_current_user),
) -> dict:
    try:
        return {"success": True, "application": portal.reject_application(actor, application_id, payload.reason)}
    except portal.ServicePortalError as exc:
        _handle_error(exc)


@router.post("/api/officer/applications/{application_id}/comment")
def add_comment(
    application_id: str,
    payload: CommentRequest,
    actor: CurrentUser = Depends(get_current_user),
) -> dict:
    try:
        return {"success": True, "comment": portal.add_comment(actor, application_id, payload.comment)}
    except portal.ServicePortalError as exc:
        _handle_error(exc)


@router.get("/api/certificates/{certificate_id}")
def get_certificate(certificate_id: str, actor: CurrentUser = Depends(get_current_user)) -> dict:
    try:
        return {"success": True, "certificate": portal.get_certificate(actor, certificate_id)}
    except portal.ServicePortalError as exc:
        _handle_error(exc)


@router.get("/api/certificates/{certificate_id}/download")
def download_certificate(certificate_id: str, actor: CurrentUser = Depends(get_current_user)) -> Response:
    try:
        certificate_number, content = portal.get_certificate_bytes(actor, certificate_id)
        return Response(
            content=content,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{certificate_number}.pdf"'},
        )
    except portal.ServicePortalError as exc:
        _handle_error(exc)


@router.get("/api/certificates/verify/{verification_query}")
@router.get("/api/verify-certificate/{verification_query}")
def verify_certificate(verification_query: str) -> dict:
    return {"success": True, **portal.verify_certificate(verification_query)}


@router.post("/api/certificates/{certificate_id}/revoke")
def revoke_certificate(
    certificate_id: str,
    payload: RevokeCertificateRequest,
    actor: CurrentUser = Depends(get_current_user),
) -> dict:
    try:
        return {"success": True, "certificate": portal.revoke_certificate(actor, certificate_id, payload.reason)}
    except portal.ServicePortalError as exc:
        _handle_error(exc)


@router.get("/api/notifications")
def list_notifications(actor: CurrentUser = Depends(get_current_user)) -> dict:
    return {"success": True, "notifications": portal.list_notifications(actor)}


@router.patch("/api/notifications/{notification_id}/read")
def mark_notification_read(notification_id: str, actor: CurrentUser = Depends(get_current_user)) -> dict:
    try:
        return {"success": True, "notification": portal.mark_notification_read(actor, notification_id)}
    except portal.ServicePortalError as exc:
        _handle_error(exc)


@router.patch("/api/notifications/read-all")
def mark_all_notifications_read(actor: CurrentUser = Depends(get_current_user)) -> dict:
    return {"success": True, "notifications": portal.mark_all_notifications_read(actor)}


@router.get("/api/admin/services", dependencies=[Depends(require_roles("admin", "reviewer", "viewer"))])
def admin_services() -> dict:
    return {"success": True, "services": portal.list_services()}


@router.get("/api/admin/forms", dependencies=[Depends(require_roles("admin", "reviewer", "viewer"))])
def admin_forms() -> dict:
    return {"success": True, "forms": [portal.get_service_form(item["service_id"]) for item in portal.list_services()]}


@router.get("/api/admin/certificates", dependencies=[Depends(require_roles("admin", "reviewer", "viewer"))])
def admin_certificates(actor: CurrentUser = Depends(get_current_user)) -> dict:
    certificates = []
    for application in portal.list_applications(actor):
        if application.get("certificate"):
            certificates.append(application["certificate"])
    return {"success": True, "certificates": certificates}
