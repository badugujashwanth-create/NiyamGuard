from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import Request

from app.config import settings
from app.models.auth_models import RefreshTokenRecord, UserRecord
from app.repositories.auth_repository import auth_repository
from app.schemas.auth_schemas import CreateUserRequest, UpdateUserRequest
from app.security.jwt import create_access_token
from app.security.password import hash_password, verify_password
from app.security.rbac import CurrentUser
from app.services import audit_service
from app.services.time import now_iso


DEFAULT_USERS = [
    ("user_admin", "admin@niyamguard.local", "Admin@12345", "admin"),
    ("user_reviewer", "reviewer@niyamguard.local", "Reviewer@12345", "reviewer"),
    ("user_viewer", "viewer@niyamguard.local", "Viewer@12345", "viewer"),
    ("user_officer", "officer@niyamguard.local", "Officer@12345", "officer"),
    ("user_citizen", "citizen@niyamguard.local", "Citizen@12345", "citizen"),
    ("user_sandbox_admin", "sandbox@niyamguard.local", "Sandbox@12345", "sandbox_admin"),
]


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _expires_iso(days: int) -> str:
    return (datetime.now(timezone.utc) + timedelta(days=days)).replace(microsecond=0).isoformat()


def _user_response(user: UserRecord) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
    }


def seed_default_users() -> None:
    for user_id, email, password, role in DEFAULT_USERS:
        existing = auth_repository.get_user_by_email(email)
        if existing:
            if existing.role != role or not existing.is_active:
                existing.role = role
                existing.is_active = True
                existing.updated_at = now_iso()
                auth_repository.upsert_user(existing)
            continue
        timestamp = now_iso()
        auth_repository.upsert_user(
            UserRecord(
                id=user_id,
                email=email.casefold(),
                password_hash=hash_password(password),
                role=role,
                is_active=True,
                created_at=timestamp,
                updated_at=timestamp,
            )
        )


def login(email: str, password: str, request: Request | None = None) -> dict | None:
    user = auth_repository.get_user_by_email(email)
    if user is None or not user.is_active or not verify_password(password, user.password_hash):
        audit_service.record_event(
            action="login_failure",
            details={"email": email.casefold()},
            request=request,
        )
        return None
    access_token = create_access_token({"sub": user.id, "email": user.email, "role": user.role})
    refresh_token = secrets.token_urlsafe(48)
    auth_repository.create_refresh_token(
        RefreshTokenRecord(
            id=f"refresh_{uuid4().hex}",
            user_id=user.id,
            token_hash=_token_hash(refresh_token),
            expires_at=_expires_iso(settings.refresh_token_expire_days),
            revoked_at=None,
            created_at=now_iso(),
        )
    )
    audit_service.record_event(
        action="login_success",
        actor=CurrentUser(id=user.id, email=user.email, role=user.role),
        request=request,
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": _user_response(user),
    }


def refresh(refresh_token: str) -> dict | None:
    record = auth_repository.get_refresh_token(_token_hash(refresh_token))
    if record is None or record.revoked_at:
        return None
    if datetime.fromisoformat(record.expires_at) < datetime.now(timezone.utc):
        return None
    user = auth_repository.get_user(record.user_id)
    if user is None or not user.is_active:
        return None
    return {
        "access_token": create_access_token({"sub": user.id, "email": user.email, "role": user.role}),
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": _user_response(user),
    }


def logout(refresh_token: str | None, actor: CurrentUser, request: Request | None = None) -> None:
    if refresh_token:
        auth_repository.revoke_refresh_token(_token_hash(refresh_token), now_iso())
    audit_service.record_event(action="logout", actor=actor, request=request)


def list_users() -> list[dict]:
    return [_user_response(user) for user in auth_repository.list_users()]


def create_user(payload: CreateUserRequest, actor: CurrentUser, request: Request | None = None) -> dict:
    timestamp = now_iso()
    user = UserRecord(
        id=f"user_{uuid4().hex}",
        email=payload.email.casefold(),
        password_hash=hash_password(payload.password),
        role=payload.role,
        is_active=payload.is_active,
        created_at=timestamp,
        updated_at=timestamp,
    )
    auth_repository.upsert_user(user)
    audit_service.record_event(
        action="user_created",
        actor=actor,
        request=request,
        entity_type="user",
        entity_id=user.id,
        details={"email": user.email, "role": user.role},
    )
    return _user_response(user)


def update_user(user_id: str, payload: UpdateUserRequest, actor: CurrentUser, request: Request | None = None) -> dict | None:
    user = auth_repository.get_user(user_id)
    if user is None:
        return None
    if payload.role is not None:
        user.role = payload.role
    if payload.is_active is not None:
        user.is_active = payload.is_active
    if payload.password is not None:
        user.password_hash = hash_password(payload.password)
    user.updated_at = now_iso()
    auth_repository.upsert_user(user)
    audit_service.record_event(
        action="user_updated",
        actor=actor,
        request=request,
        entity_type="user",
        entity_id=user.id,
        details={"email": user.email, "role": user.role, "is_active": user.is_active},
    )
    return _user_response(user)
