from __future__ import annotations

import hashlib
import json
from uuid import uuid4

from sqlalchemy import delete, select

from app.database import SessionLocal, init_db
from app.models.audit_models import AuditEventRecord
from app.services.time import now_iso

GENESIS_HASH = "0" * 64


def _legacy_payload(record: AuditEventRecord) -> dict:
    return {
        "id": record.id,
        "action": record.action,
        "payload": record.details_json or {},
        "timestamp": record.created_at,
        "actor_user_id": record.actor_user_id,
        "actor_email": record.actor_email,
        "actor_role": record.actor_role,
        "entity_type": record.entity_type,
        "entity_id": record.entity_id,
        "ip_address": record.ip_address,
        "user_agent": record.user_agent,
        "request_id": record.request_id,
        "previous_hash": record.previous_hash,
        "current_hash": record.current_hash,
        "created_at": record.created_at,
    }


def _hash_event(record: AuditEventRecord, previous_hash: str) -> str:
    payload = json.dumps(record.details_json or {}, sort_keys=True, separators=(",", ":"))
    raw = "|".join(
        [
            record.id,
            record.action,
            record.actor_email or "",
            record.actor_role or "",
            record.entity_type or "",
            record.entity_id or "",
            payload,
            record.created_at,
            previous_hash,
        ]
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class AuditRepository:
    def __init__(self) -> None:
        init_db()

    def create(
        self,
        *,
        action: str,
        details: dict | None = None,
        actor_user_id: str | None = None,
        actor_email: str | None = None,
        actor_role: str | None = None,
        entity_type: str | None = None,
        entity_id: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        request_id: str | None = None,
        event_id: str | None = None,
        created_at: str | None = None,
    ) -> dict:
        created = created_at or now_iso()
        with SessionLocal() as session:
            previous_hash = (
                session.scalars(
                    select(AuditEventRecord.current_hash)
                    .where(AuditEventRecord.current_hash.is_not(None))
                    .order_by(AuditEventRecord.created_at.desc())
                    .limit(1)
                ).first()
                or GENESIS_HASH
            )
        record = AuditEventRecord(
            id=event_id or f"audit_{uuid4().hex}",
            actor_user_id=actor_user_id,
            actor_email=actor_email,
            actor_role=actor_role,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details_json=details or {},
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
            previous_hash=previous_hash,
            current_hash=None,
            created_at=created,
        )
        record.current_hash = _hash_event(record, previous_hash)
        with SessionLocal() as session:
            session.merge(record)
            session.commit()
        return _legacy_payload(record)

    def list(self, limit: int = 100, action: str | None = None) -> list[dict]:
        statement = select(AuditEventRecord)
        if action:
            statement = statement.where(AuditEventRecord.action == action)
        statement = statement.order_by(AuditEventRecord.created_at.desc()).limit(limit)
        with SessionLocal() as session:
            return [_legacy_payload(record) for record in session.scalars(statement).all()]

    def get(self, event_id: str) -> dict | None:
        with SessionLocal() as session:
            record = session.get(AuditEventRecord, event_id)
            return _legacy_payload(record) if record else None

    def replace_from_legacy(self, events: list[dict]) -> None:
        with SessionLocal() as session:
            session.execute(delete(AuditEventRecord))
            previous_hash = GENESIS_HASH
            for event in events:
                record = AuditEventRecord(
                    id=event.get("id") or f"audit_{uuid4().hex}",
                    actor_user_id=event.get("actor_user_id"),
                    actor_email=event.get("actor_email"),
                    actor_role=event.get("actor_role"),
                    action=event.get("action", "unknown"),
                    entity_type=event.get("entity_type"),
                    entity_id=event.get("entity_id"),
                    details_json=event.get("payload") or event.get("details_json") or {},
                    ip_address=event.get("ip_address"),
                    user_agent=event.get("user_agent"),
                    request_id=event.get("request_id"),
                    previous_hash=previous_hash,
                    current_hash=None,
                    created_at=event.get("created_at") or event.get("timestamp") or now_iso(),
                )
                record.current_hash = _hash_event(record, previous_hash)
                previous_hash = record.current_hash
                session.add(record)
            session.commit()

    def verify_chain(self) -> dict:
        with SessionLocal() as session:
            records = session.scalars(select(AuditEventRecord).order_by(AuditEventRecord.created_at.asc())).all()
        expected_previous = GENESIS_HASH
        for record in records:
            if record.previous_hash != expected_previous:
                return {
                    "success": True,
                    "chain_intact": False,
                    "message": f"Audit chain broken at {record.id}: previous hash mismatch.",
                    "checked_events": len(records),
                }
            if _hash_event(record, record.previous_hash or GENESIS_HASH) != record.current_hash:
                return {
                    "success": True,
                    "chain_intact": False,
                    "message": f"Audit chain broken at {record.id}: current hash mismatch.",
                    "checked_events": len(records),
                }
            expected_previous = record.current_hash or GENESIS_HASH
        return {
            "success": True,
            "chain_intact": True,
            "message": f"{len(records)} audit events verified.",
            "checked_events": len(records),
        }


audit_repository = AuditRepository()
