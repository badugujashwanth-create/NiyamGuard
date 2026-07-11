from __future__ import annotations

from fastapi import Request

from app.repositories.audit_repository import audit_repository
from app.security.rbac import CurrentUser


def record_event(
    *,
    action: str,
    details: dict | None = None,
    actor: CurrentUser | None = None,
    request: Request | None = None,
    entity_type: str | None = None,
    entity_id: str | None = None,
) -> dict:
    return audit_repository.create(
        action=action,
        details=details,
        actor_user_id=actor.id if actor else None,
        actor_email=actor.email if actor else None,
        actor_role=actor.role if actor else None,
        entity_type=entity_type,
        entity_id=entity_id,
        ip_address=request.client.host if request and request.client else None,
        user_agent=request.headers.get("user-agent") if request else None,
        request_id=getattr(request.state, "request_id", None) if request else None,
    )


def list_events(
    limit: int = 100,
    action: str | None = None,
    actor_user_id: str | None = None,
) -> list[dict]:
    return audit_repository.list(limit=limit, action=action, actor_user_id=actor_user_id)


def get_event(event_id: str) -> dict | None:
    return audit_repository.get(event_id)


def verify_events() -> dict:
    return audit_repository.verify_chain()
