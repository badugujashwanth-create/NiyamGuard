from fastapi import APIRouter
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from app.services.tts_service import (
    TtsProviderError,
    synthesize_speech,
)

router = APIRouter(prefix="/api/tts", tags=["tts"])


class TtsRequest(BaseModel):
    text: str = ""
    language_code: str | None = None
    detected_language: str | None = None
    provider: str = "auto"


@router.get("/health")
def tts_health() -> dict:
    return {
        "success": True,
        "available_providers": ["browser", "gtts"],
        "default_provider": "gtts",
        "supported_languages": {
            "telugu": "te-IN",
            "hindi": "hi-IN",
            "english": "en-IN",
        },
    }


@router.post("/speak", response_model=None)
def speak(request: TtsRequest) -> Response | JSONResponse:
    if not request.text.strip():
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": "TTS text must not be empty.",
            },
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
