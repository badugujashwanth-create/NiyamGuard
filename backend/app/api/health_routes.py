from fastapi import APIRouter

from app.config import APP_NAME, settings
from app.database import REQUIRED_RUNTIME_TABLES, database_ready, engine
from sqlalchemy import inspect
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
    try:
        available_tables = set(inspect(engine).get_table_names())
    except Exception:
        available_tables = set()
    missing_tables = sorted(REQUIRED_RUNTIME_TABLES - available_tables)
    return {
        "status": "ok" if db_ok and demo_ok else "degraded",
        "database": {"reachable": db_ok},
        "core_tables": {"available": db_ok, "missing": missing_tables},
        "demo_data": {"available": demo_ok, "verified_rules": len(store.verified_rules)},
    }
