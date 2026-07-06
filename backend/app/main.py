from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import APP_NAME, APP_VERSION, PYTHON_REQUIREMENT
from app.routes.assistant_routes import router as assistant_router
from app.routes.form_routes import router as form_router
from app.routes.location_routes import router as location_router
from app.routes.session_routes import router as session_router
from app.routes.tts_routes import router as tts_router

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=(
        "Text-first guidance API for the Income Certificate form. "
        "It never fills or submits an application."
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
app.include_router(location_router)


@app.get("/", tags=["health"])
def health_check() -> dict[str, str]:
    return {
        "message": "NiyamGuard Call Assistant Backend is running",
        "version": APP_VERSION,
        "python": PYTHON_REQUIREMENT,
    }
