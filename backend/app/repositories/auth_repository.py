from __future__ import annotations

from sqlalchemy import select

from app.database import SessionLocal, init_db
from app.models.auth_models import RefreshTokenRecord, UserRecord


class AuthRepository:
    def __init__(self) -> None:
        init_db()

    def get_user_by_email(self, email: str) -> UserRecord | None:
        with SessionLocal() as session:
            return session.scalar(select(UserRecord).where(UserRecord.email == email.casefold()))

    def get_user(self, user_id: str) -> UserRecord | None:
        with SessionLocal() as session:
            return session.get(UserRecord, user_id)

    def list_users(self) -> list[UserRecord]:
        with SessionLocal() as session:
            return list(session.scalars(select(UserRecord).order_by(UserRecord.email)).all())

    def upsert_user(self, user: UserRecord) -> UserRecord:
        with SessionLocal() as session:
            session.merge(user)
            session.commit()
        return user

    def create_refresh_token(self, token: RefreshTokenRecord) -> RefreshTokenRecord:
        with SessionLocal() as session:
            session.add(token)
            session.commit()
        return token

    def get_refresh_token(self, token_hash: str) -> RefreshTokenRecord | None:
        with SessionLocal() as session:
            return session.scalar(
                select(RefreshTokenRecord).where(RefreshTokenRecord.token_hash == token_hash)
            )

    def revoke_refresh_token(self, token_hash: str, revoked_at: str) -> bool:
        with SessionLocal() as session:
            record = session.scalar(
                select(RefreshTokenRecord).where(RefreshTokenRecord.token_hash == token_hash)
            )
            if record is None:
                return False
            record.revoked_at = revoked_at
            session.commit()
            return True


auth_repository = AuthRepository()
