from fastapi import APIRouter

from app.config import APP_NAME, runtime_config_health, settings
from app.database import REQUIRED_RUNTIME_TABLES, database_ready, engine
from app.documents.processing import ocr_health
from app.security.malware_scan import malware_scan_health
from app.storage.object_storage import ObjectStorageError, ObjectStorageUnavailable, get_object_storage
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
    try:
        storage_status = get_object_storage().health()
    except (ObjectStorageError, ObjectStorageUnavailable) as exc:
        storage_status = {
            "backend": getattr(settings, "object_storage_backend", "local"),
            "ready": False,
            "required": settings.app_env.strip().lower() in {"production", "prod", "staging"},
            "error": str(exc),
        }
    scanner_status = malware_scan_health()
    ocr_status = ocr_health()
    config_status = runtime_config_health()
    dependencies_ok = all(
        bool(status.get("ready"))
        for status in (storage_status, scanner_status, ocr_status, config_status)
        if status.get("required")
    )
    overall_ok = db_ok and demo_ok and dependencies_ok
    return {
        "status": "ok" if overall_ok else "degraded",
        "database": {"reachable": db_ok},
        "core_tables": {"available": db_ok, "missing": missing_tables},
        "demo_data": {"available": demo_ok, "verified_rules": len(store.verified_rules)},
        "object_storage": storage_status,
        "malware_scanner": scanner_status,
        "ocr": ocr_status,
        "configuration": config_status,
    }
