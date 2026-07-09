import logging

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.config import APP_NAME, APP_VERSION, PYTHON_REQUIREMENT, settings
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
from app.routes.assistant_routes import router as assistant_router
from app.routes.admin_routes import router as admin_router
from app.routes.ai_routes import router as ai_router
from app.routes.audit_routes import router as audit_router
from app.routes.auth_routes import router as auth_router
from app.routes.cascade_routes import router as cascade_router
from app.routes.chat_routes import router as chat_router
from app.routes.compliance_routes import router as compliance_router
from app.routes.conflict_routes import router as conflict_router
from app.routes.connected_system_routes import router as connected_system_router
from app.routes.dashboard_routes import router as dashboard_router
from app.routes.dataset_routes import router as dataset_router
from app.routes.demo_routes import router as demo_router
from app.routes.form_routes import router as form_router
from app.routes.health_routes import router as health_router
from app.routes.knowledge_routes import router as knowledge_router
from app.routes.location_routes import router as location_router
from app.routes.public_routes import router as public_router
from app.routes.report_routes import router as report_router
from app.routes.session_routes import router as session_router
from app.routes.stt_routes import router as stt_router
from app.routes.tts_routes import router as tts_router
from app.services.auth_service import seed_default_users
from app.services.platform_store import ensure_demo_store_seeded

logging.basicConfig(level=getattr(logging, settings.log_level, logging.INFO))

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
app.include_router(connected_system_router)
app.include_router(compliance_router)
app.include_router(cascade_router)
app.include_router(dashboard_router)
app.include_router(dataset_router)
app.include_router(conflict_router)
app.include_router(admin_router)
app.include_router(report_router)
app.include_router(public_router)
app.include_router(audit_router)
app.include_router(demo_router)


@app.get("/", tags=["health"])
def health_check() -> dict[str, str]:
    return {
        "message": "NiyamGuard Call Assistant Backend is running",
        "version": APP_VERSION,
        "python": PYTHON_REQUIREMENT,
    }
