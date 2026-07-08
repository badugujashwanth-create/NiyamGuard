from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import APP_NAME, APP_VERSION, PYTHON_REQUIREMENT
from app.routes.assistant_routes import router as assistant_router
from app.routes.admin_routes import router as admin_router
from app.routes.cascade_routes import router as cascade_router
from app.routes.compliance_routes import router as compliance_router
from app.routes.conflict_routes import router as conflict_router
from app.routes.connected_system_routes import router as connected_system_router
from app.routes.dashboard_routes import router as dashboard_router
from app.routes.form_routes import router as form_router
from app.routes.knowledge_routes import router as knowledge_router
from app.routes.location_routes import router as location_router
from app.routes.public_routes import router as public_router
from app.routes.report_routes import router as report_router
from app.routes.session_routes import router as session_router
from app.routes.stt_routes import router as stt_router
from app.routes.tts_routes import router as tts_router

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=(
        "Voice and form guidance API for simplified government service forms. "
        "It guides citizens but never fills, uploads, or submits an application."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=[
        "X-TTS-Language-Code",
        "X-TTS-Provider",
        "X-TTS-Cache",
    ],
)

app.include_router(form_router)
app.include_router(session_router)
app.include_router(assistant_router)
app.include_router(tts_router)
app.include_router(stt_router)
app.include_router(location_router)
app.include_router(knowledge_router)
app.include_router(connected_system_router)
app.include_router(compliance_router)
app.include_router(cascade_router)
app.include_router(dashboard_router)
app.include_router(conflict_router)
app.include_router(admin_router)
app.include_router(report_router)
app.include_router(public_router)


@app.get("/", tags=["health"])
def health_check() -> dict[str, str]:
    return {
        "message": "NiyamGuard Call Assistant Backend is running",
        "version": APP_VERSION,
        "python": PYTHON_REQUIREMENT,
    }
