import time

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool

from app.stt.stt_service import (
    SttTranscriptionError,
    SttUnavailableError,
    get_stt_readiness,
    schedule_stt_warmup,
    transcribe_audio,
)

router = APIRouter(prefix="/api/stt", tags=["speech-to-text"])
schedule_stt_warmup()


def _request_time_ms(started_at: float) -> float:
    return round((time.perf_counter() - started_at) * 1000, 2)


@router.get("/health")
def stt_health() -> dict:
    """Report provider readiness without loading or downloading the model."""
    started_at = time.perf_counter()
    readiness = get_stt_readiness()
    return {
        "success": True,
        **readiness,
        "timing_ms": {"health_check": _request_time_ms(started_at)},
    }


@router.post("/transcribe")
async def transcribe(
    audio: UploadFile = File(...),
    language_hint: str | None = Form(default="auto"),
    form_id: str | None = Form(default=None),
    session_id: str | None = Form(default=None),
    fallback_transcript: str | None = Form(default=None),
) -> JSONResponse:
    started_at = time.perf_counter()
    try:
        audio_bytes = await audio.read()
        # Faster-Whisper model loading and CPU inference are blocking work.
        # Keep them off the async server loop so health, auth, and form APIs
        # remain responsive while a voice request is being transcribed.
        result = await run_in_threadpool(
            transcribe_audio,
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
                "engine": "faster-whisper",
                "fallback": "browser-speech-recognition",
                "readiness": get_stt_readiness(),
                "timing_ms": {"request_total": _request_time_ms(started_at)},
            },
        )
    except SttTranscriptionError as exc:
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "message": str(exc),
                "provider": "local-whisper",
                "engine": "faster-whisper",
                "fallback": "browser-speech-recognition",
                "timing_ms": {"request_total": _request_time_ms(started_at)},
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
            "engine": result.engine,
            "model": result.model,
            "timing_ms": {
                "request_total": _request_time_ms(started_at),
                "processing": result.processing_time_ms,
                "model_load": result.model_load_time_ms,
                "transcription": result.transcription_time_ms,
                "audio_duration": result.audio_duration_ms,
            },
        }
    )
