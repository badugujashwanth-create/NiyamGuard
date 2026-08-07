from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import JSONResponse

from app.config import settings
from app.security.rate_limit import rate_limit
from app.stt.stt_service import (
    SttTranscriptionError,
    SttUnavailableError,
    transcribe_audio,
)

router = APIRouter(prefix="/api/stt", tags=["speech-to-text"])


@router.post("/transcribe", dependencies=[Depends(rate_limit)])
async def transcribe(
    audio: UploadFile = File(...),
    language_hint: str | None = Form(default="auto"),
    form_id: str | None = Form(default=None),
    session_id: str | None = Form(default=None),
    fallback_transcript: str | None = Form(default=None),
) -> JSONResponse:
    try:
        audio_bytes = await audio.read(settings.stt_max_upload_bytes + 1)
        if len(audio_bytes) > settings.stt_max_upload_bytes:
            return JSONResponse(
                status_code=413,
                content={"success": False, "message": "Audio upload exceeds the configured size limit."},
            )
        suffix = Path(audio.filename or "audio.webm").suffix.casefold()
        if suffix not in {".webm", ".wav", ".mp3", ".m4a", ".ogg"}:
            return JSONResponse(
                status_code=415,
                content={"success": False, "message": "Unsupported audio format."},
            )
        content_type = (audio.content_type or "").casefold().split(";", 1)[0]
        if content_type and content_type not in {
            "audio/webm",
            "audio/wav",
            "audio/x-wav",
            "audio/mpeg",
            "audio/mp4",
            "audio/ogg",
            "application/octet-stream",
        }:
            return JSONResponse(
                status_code=415,
                content={"success": False, "message": "Unsupported audio MIME type."},
            )
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
