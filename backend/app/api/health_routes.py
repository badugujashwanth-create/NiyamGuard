from fastapi import APIRouter

from app.config import APP_NAME, settings
from app.database import database_ready
from app.knowledge_base.platform_store import read_store

router = APIRouter(tags=["Health"])


@router.get("/api/health")
def health() -> dict:
    return {
        "status": "ok",
        "app": APP_NAME,
        "environment": settings.app_env,
    }


@router.get("/api/ready")
def ready() -> dict:
    db_ok = database_ready()
    store = read_store()
    demo_ok = bool(store.verified_rules) if settings.demo_mode else True
    return {
        "status": "ok" if db_ok and demo_ok else "degraded",
        "database": {"reachable": db_ok},
        "core_tables": {"available": db_ok},
        "demo_data": {"available": demo_ok, "verified_rules": len(store.verified_rules)},
    }
