from __future__ import annotations

from app.config import settings
from app.services import circular_sync_service


def status() -> dict:
    return {
        "enabled": settings.auto_sync_enabled,
        "interval_minutes": settings.auto_sync_interval_minutes,
        "source_mode": settings.circular_source_mode,
        "running": False,
        "message": "Scheduler is disabled unless AUTO_SYNC_ENABLED=true.",
    }


def run_now() -> dict:
    return circular_sync_service.sync_all(created_by="scheduler_run_now")
