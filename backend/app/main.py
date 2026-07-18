import logging
import os
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.config import APP_NAME, APP_VERSION, PYTHON_REQUIREMENT, settings, validate_runtime_settings
from app.dependencies import require_demo_mode
from app.database import init_db
from app.middleware.error_handler import (
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.middleware.logging_middleware import LoggingMiddleware
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.middleware.version_alias import ApiVersionAliasMiddleware
from app.api.assistant_routes import router as assistant_router
from app.api.admin_routes import router as admin_router
from app.api.ai_routes import router as ai_router
from app.api.audit_routes import router as audit_router
from app.api.auth_routes import router as auth_router
from app.api.cascade_routes import router as cascade_router
from app.api.chat_routes import router as chat_router
from app.api.circular_routes import router as circular_router
from app.api.compliance_update_routes import router as compliance_update_router
from app.api.compliance_routes import router as compliance_router
from app.api.conflict_routes import router as conflict_router
from app.api.connected_system_routes import router as connected_system_router
from app.api.dashboard_routes import router as dashboard_router
from app.api.dataset_routes import router as dataset_router
from app.api.demo_routes import router as demo_router
from app.api.demo_self_update_routes import router as demo_self_update_router
from app.api.form_routes import router as form_router
from app.api.health_routes import router as health_router
from app.api.hybrid_intelligence_routes import router as hybrid_intelligence_router
from app.api.knowledge_update_routes import router as knowledge_update_router
from app.api.knowledge_routes import router as knowledge_router
from app.api.location_routes import router as location_router
from app.api.mock_system_routes import router as mock_system_router
from app.api.policy_update_routes import router as policy_update_router
from app.api.public_routes import router as public_router
from app.api.propagation_routes import router as propagation_router
from app.api.readiness_routes import router as readiness_router
from app.api.report_routes import router as report_router
from app.api.rule_candidate_routes import router as rule_candidate_router
from app.api.scheduler_routes import router as scheduler_router
from app.api.scheme_finder_routes import router as scheme_finder_router
from app.api.service_portal_routes import router as service_portal_router
from app.api.session_routes import router as session_router
from app.api.source_routes import router as source_router
from app.api.stt_routes import router as stt_router
from app.api.tts_routes import router as tts_router
from app.api.virtual_government_routes import router as virtual_government_router
from app.api.sandbox_routes import router as sandbox_router
from app.api.government_routes import router as government_router
from app.api.chatbot_routes import router as chatbot_router
from app.services.auth_service import seed_default_users
from app.knowledge_base.platform_store import ensure_demo_store_seeded

logging.basicConfig(level=getattr(logging, settings.log_level, logging.INFO))
validate_runtime_settings()

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=(
        "Voice and form guidance API for simplified government service forms. "
        "It guides citizens but never fills, uploads, or submits an application."
    ),
)

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

app.add_middleware(ApiVersionAliasMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.trusted_hosts)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=[
        "X-Request-ID",
        "X-TTS-Language-Code",
        "X-TTS-Provider",
        "X-TTS-Cache",
    ],
)

init_db()
ensure_demo_store_seeded()
seed_default_users()

app.include_router(health_router)
app.include_router(hybrid_intelligence_router)
app.include_router(auth_router)
app.include_router(form_router)
app.include_router(session_router)
app.include_router(assistant_router)
app.include_router(ai_router)
app.include_router(chat_router)
app.include_router(tts_router)
app.include_router(stt_router)
app.include_router(location_router)
app.include_router(knowledge_router)
app.include_router(knowledge_update_router)
app.include_router(connected_system_router)
app.include_router(compliance_router)
app.include_router(compliance_update_router)
app.include_router(cascade_router)
app.include_router(dashboard_router)
app.include_router(dataset_router)
app.include_router(conflict_router)
app.include_router(source_router)
app.include_router(circular_router)
app.include_router(rule_candidate_router)
app.include_router(policy_update_router)
app.include_router(propagation_router)
app.include_router(readiness_router)
app.include_router(scheduler_router)
app.include_router(mock_system_router, dependencies=[Depends(require_demo_mode)])
app.include_router(scheme_finder_router)
app.include_router(service_portal_router)
app.include_router(admin_router)
app.include_router(report_router)
app.include_router(public_router)
app.include_router(audit_router)
app.include_router(demo_router, dependencies=[Depends(require_demo_mode)])
app.include_router(demo_self_update_router, dependencies=[Depends(require_demo_mode)])
app.include_router(virtual_government_router, dependencies=[Depends(require_demo_mode)])
app.include_router(sandbox_router, dependencies=[Depends(require_demo_mode)])
app.include_router(government_router)
app.include_router(chatbot_router)


_frontend_dist_dir = Path(
    os.getenv("FRONTEND_DIST_DIR", Path(__file__).resolve().parents[1] / "static")
).resolve()
_frontend_index = _frontend_dist_dir / "index.html"


@app.get("/", tags=["health"], response_model=None)
def health_check() -> dict[str, str] | FileResponse:
    if _frontend_index.is_file():
        return FileResponse(_frontend_index)
    return {
        "message": "NiyamGuard API is running",
        "version": APP_VERSION,
        "python": PYTHON_REQUIREMENT,
    }


if _frontend_index.is_file():
    @app.get("/{requested_path:path}", include_in_schema=False, response_model=None)
    def serve_frontend(requested_path: str) -> FileResponse:
        if requested_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API route not found")
        requested_file = (_frontend_dist_dir / requested_path).resolve()
        if requested_file.is_relative_to(_frontend_dist_dir) and requested_file.is_file():
            return FileResponse(requested_file)
        return FileResponse(_frontend_index)
