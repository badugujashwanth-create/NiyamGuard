from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field

from app.config import settings
from app.security.rate_limit import rate_limit
from app.tts.tts_service import (
    TtsProviderError,
    synthesize_speech,
)

router = APIRouter(prefix="/api/tts", tags=["tts"])


class TtsRequest(BaseModel):
    text: str = Field(default="", max_length=10_000)
    language_code: str | None = None
    detected_language: str | None = None
    provider: str = "auto"


@router.get("/health")
def tts_health() -> dict:
    return {
        "success": True,
        "available_providers": ["browser", "edge_tts"],
        "default_provider": "edge_tts",
        "supported_languages": {
            "telugu": "te-IN",
            "hindi": "hi-IN",
            "english": "en-IN",
        },
    }


@router.post("/speak", response_model=None, dependencies=[Depends(rate_limit)])
def speak(request: TtsRequest) -> Response | JSONResponse:
    if not request.text.strip():
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": "TTS text must not be empty.",
            },
        )
    if len(request.text) > settings.tts_max_characters:
        return JSONResponse(
            status_code=413,
            content={"success": False, "message": "TTS text exceeds the configured character limit."},
        )
    try:
        result = synthesize_speech(
            request.text,
            request.language_code or "",
            request.provider,
            detected_language=request.detected_language,
        )
    except ValueError as exc:
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": str(exc)},
        )
    except TtsProviderError as exc:
        return JSONResponse(
            status_code=503,
            content={"success": False, "message": str(exc)},
        )

    return Response(
        content=result.audio,
        media_type="audio/mpeg",
        headers={
            "X-TTS-Language-Code": result.language_code,
            "X-TTS-Provider": result.provider,
            "X-TTS-Cache": result.cache_status,
        },
    )
