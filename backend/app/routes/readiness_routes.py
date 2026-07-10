from __future__ import annotations

from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends

from app.security.rbac import require_roles
from app.services import readiness_service

router = APIRouter(tags=["Government Pilot Readiness"])


class OtpRequest(BaseModel):
    channel: str = Field(default="sms", pattern="^(sms|email)$")
    destination: str = Field(min_length=3)


class OtpVerifyRequest(BaseModel):
    otp_id: str = Field(min_length=1)
    code: str = Field(min_length=4, max_length=8)


@router.get("/api/ops/status")
def ops_status() -> dict:
    return readiness_service.ops_status()


@router.get("/api/admin/readiness", dependencies=[Depends(require_roles("admin", "reviewer", "viewer"))])
def admin_readiness() -> dict:
    return readiness_service.readiness_report()


@router.post("/api/security/otp/request")
def request_otp(payload: OtpRequest) -> dict:
    return readiness_service.request_demo_otp(payload.channel, payload.destination)


@router.post("/api/security/otp/verify")
def verify_otp(payload: OtpVerifyRequest) -> dict:
    return readiness_service.verify_demo_otp(payload.otp_id, payload.code)
