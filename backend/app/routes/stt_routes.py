from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import JSONResponse

from app.services.stt_service import (
    SttTranscriptionError,
    SttUnavailableError,
    transcribe_audio,
)

router = APIRouter(prefix="/api/stt", tags=["speech-to-text"])


@router.post("/transcribe")
async def transcribe(
    audio: UploadFile = File(...),
    language_hint: str | None = Form(default="auto"),
    form_id: str | None = Form(default=None),
    session_id: str | None = Form(default=None),
    fallback_transcript: str | None = Form(default=None),
) -> JSONResponse:
    try:
        audio_bytes = await audio.read()
        result = transcribe_audio(
            audio_bytes,
            filename=audio.filename or "audio.webm",
            content_type=audio.content_type,
            language_hint=language_hint,
            fallback_transcript=fallback_transcript,
        )
    except SttUnavailableError as exc:
        return JSONResponse(
            status_code=503,
            content={
                "success": False,
                "message": str(exc),
                "provider": "unavailable",
                "fallback": "browser-speech-recognition",
            },
        )
    except SttTranscriptionError as exc:
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "message": str(exc),
                "provider": "local-whisper",
            },
        )

    return JSONResponse(
        content={
            "success": True,
            "transcript": result.transcript,
            "detected_language": result.detected_language,
            "language_code": result.language_code,
            "confidence": result.confidence,
            "provider": result.provider,
        }
    )
