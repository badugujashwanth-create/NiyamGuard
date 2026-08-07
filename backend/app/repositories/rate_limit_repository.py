from __future__ import annotations

import hashlib
from threading import RLock
from time import time

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.database import SessionLocal
from app.models.rate_limit_models import RateLimitBucket
from app.services.time import now_iso


class RateLimitRepository:
    _lock = RLock()

    def consume(self, key: str, limit: int, *, now: float | None = None) -> bool:
        """Atomically consume one fixed-window request across workers."""
        timestamp = time() if now is None else now
        window_start = int(timestamp // 60) * 60
        bucket_id = hashlib.sha256(key.encode("utf-8")).hexdigest()
        for attempt in range(2):
            try:
                with self._lock, SessionLocal() as session:
                    statement = select(RateLimitBucket).where(RateLimitBucket.id == bucket_id)
                    if session.bind and session.bind.dialect.name != "sqlite":
                        statement = statement.with_for_update()
                    bucket = session.scalar(statement)
                    if bucket is None:
                        session.add(
                            RateLimitBucket(
                                id=bucket_id,
                                window_start=window_start,
                                count=1,
                                updated_at=now_iso(),
                            )
                        )
                        session.commit()
                        return True
                    if bucket.window_start != window_start:
                        bucket.window_start = window_start
                        bucket.count = 1
                        bucket.updated_at = now_iso()
                        session.commit()
                        return True
                    if bucket.count >= limit:
                        return False
                    bucket.count += 1
                    bucket.updated_at = now_iso()
                    session.commit()
                    return True
            except IntegrityError:
                if attempt == 1:
                    raise
        return False


rate_limit_repository = RateLimitRepository()
