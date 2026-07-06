import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from app.config import SESSION_STORAGE_PATH
from app.models.session_models import ConversationEntry, Language, Session


class SessionNotFoundError(KeyError):
    pass


class SessionService:
    def __init__(self, storage_path: Path = SESSION_STORAGE_PATH) -> None:
        self.storage_path = storage_path
        self._lock = threading.RLock()
        self._ensure_storage()

    def _ensure_storage(self) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists():
            self.storage_path.write_text("{}\n", encoding="utf-8")

    def _read(self) -> dict[str, dict]:
        self._ensure_storage()
        try:
            content = self.storage_path.read_text(encoding="utf-8").strip()
            data = json.loads(content or "{}")
        except (json.JSONDecodeError, OSError) as exc:
            raise RuntimeError("Session storage is unreadable.") from exc
        if not isinstance(data, dict):
            raise RuntimeError("Session storage must contain a JSON object.")
        return data

    def _write(self, sessions: dict[str, dict]) -> None:
        temporary_path = self.storage_path.with_suffix(".tmp")
        temporary_path.write_text(
            json.dumps(sessions, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        os.replace(temporary_path, self.storage_path)

    def create(self, form_id: str, language: Language) -> Session:
        session = Session(
            session_id=uuid4().hex,
            form_id=form_id,
            language=language,
            created_at=datetime.now(timezone.utc),
        )
        with self._lock:
            sessions = self._read()
            sessions[session.session_id] = session.model_dump(mode="json")
            self._write(sessions)
        return session

    def get(self, session_id: str) -> Session:
        with self._lock:
            raw_session = self._read().get(session_id)
        if raw_session is None:
            raise SessionNotFoundError(session_id)
        return Session.model_validate(raw_session)

    def add_conversation_pair(self, session_id: str, user_message: str, reply: str) -> Session:
        now = datetime.now(timezone.utc)
        with self._lock:
            sessions = self._read()
            raw_session = sessions.get(session_id)
            if raw_session is None:
                raise SessionNotFoundError(session_id)
            session = Session.model_validate(raw_session)
            session.conversation.extend(
                [
                    ConversationEntry(role="user", message=user_message, timestamp=now),
                    ConversationEntry(role="assistant", message=reply, timestamp=now),
                ]
            )
            sessions[session_id] = session.model_dump(mode="json")
            self._write(sessions)
        return session


session_service = SessionService()
