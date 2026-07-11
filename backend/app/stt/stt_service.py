import importlib.util
import logging
import os
import tempfile
import threading
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.citizen_assistant.language_helper import detect_language


logger = logging.getLogger("niyamguard.stt")

STT_ENGINE = "faster-whisper"
STT_RESULT_PROVIDER = "local-whisper"
SUPPORTED_LANGUAGES = {
    "english": {"whisper_code": "en", "language_code": "en-IN"},
    "telugu": {"whisper_code": "te", "language_code": "te-IN"},
    # Hindi remains supported by the existing assistant even though Phase 1
    # explicitly requires English and Telugu.
    "hindi": {"whisper_code": "hi", "language_code": "hi-IN"},
}
_LANGUAGE_HINTS = {
    "english": "en",
    "en": "en",
    "en-in": "en",
    "en-us": "en",
    "telugu": "te",
    "te": "te",
    "te-in": "te",
    "hindi": "hi",
    "hi": "hi",
    "hi-in": "hi",
}
_LANGUAGE_NAMES_BY_CODE = {
    value["whisper_code"]: (name, value["language_code"])
    for name, value in SUPPORTED_LANGUAGES.items()
}


class SttUnavailableError(RuntimeError):
    pass


class SttTranscriptionError(RuntimeError):
    pass


@dataclass(frozen=True)
class SttConfig:
    enabled: bool
    provider: str
    model: str
    device: str
    compute_type: str
    cpu_threads: int
    num_workers: int
    download_root: str | None
    local_files_only: bool
    warmup_on_startup: bool
    beam_size: int
    vad_filter: bool

    @property
    def model_signature(self) -> tuple[Any, ...]:
        return (
            self.provider,
            self.model,
            self.device,
            self.compute_type,
            self.cpu_threads,
            self.num_workers,
            self.download_root,
            self.local_files_only,
        )

    def public_dict(self) -> dict[str, Any]:
        return {
            "enabled": self.enabled,
            "provider": self.provider,
            "model": self.model,
            "device": self.device,
            "compute_type": self.compute_type,
            "cpu_threads": self.cpu_threads,
            "num_workers": self.num_workers,
            "local_files_only": self.local_files_only,
            "warmup_on_startup": self.warmup_on_startup,
            "beam_size": self.beam_size,
            "vad_filter": self.vad_filter,
        }


@dataclass(frozen=True)
class SttResult:
    transcript: str
    detected_language: str
    language_code: str
    confidence: float
    provider: str
    engine: str
    model: str | None
    processing_time_ms: float
    model_load_time_ms: float
    transcription_time_ms: float
    audio_duration_ms: float | None = None


def _bool_env(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().casefold() in {"1", "true", "yes", "on"}


def _int_env(name: str, default: int, *, minimum: int = 0) -> int:
    try:
        return max(minimum, int(os.getenv(name, str(default))))
    except ValueError:
        return default


def get_stt_config() -> SttConfig:
    """Read STT settings at use time so tests and deployments remain reproducible."""
    provider = os.getenv("STT_PROVIDER", STT_ENGINE).strip().casefold() or STT_ENGINE
    if provider in {"auto", "local-whisper"}:
        provider = STT_ENGINE
    download_root = os.getenv("STT_DOWNLOAD_ROOT", "").strip() or None
    return SttConfig(
        enabled=_bool_env("STT_ENABLED", True),
        provider=provider,
        model=os.getenv("STT_MODEL", "base").strip() or "base",
        device=os.getenv("STT_DEVICE", "cpu").strip() or "cpu",
        compute_type=os.getenv("STT_COMPUTE_TYPE", "int8").strip() or "int8",
        cpu_threads=_int_env("STT_CPU_THREADS", 0),
        num_workers=_int_env("STT_NUM_WORKERS", 1, minimum=1),
        download_root=download_root,
        local_files_only=_bool_env("STT_LOCAL_FILES_ONLY", False),
        warmup_on_startup=_bool_env("STT_WARMUP_ON_STARTUP", False),
        beam_size=_int_env("STT_BEAM_SIZE", 1, minimum=1),
        vad_filter=_bool_env("STT_VAD_FILTER", True),
    )


_model_load_lock = threading.RLock()
_runtime_lock = threading.RLock()
_model_instance: Any | None = None
_model_signature: tuple[Any, ...] | None = None
_warmup_thread: threading.Thread | None = None
_runtime: dict[str, Any] = {
    "status": "not_loaded",
    "last_error": None,
    "model_load_time_ms": None,
    "loaded_at": None,
    "last_transcription_time_ms": None,
    "last_audio_duration_ms": None,
}


def _elapsed_ms(started_at: float) -> float:
    return round((time.perf_counter() - started_at) * 1000, 2)


def _set_runtime(**updates: Any) -> None:
    with _runtime_lock:
        _runtime.update(updates)


def _faster_whisper_installed() -> bool:
    try:
        return importlib.util.find_spec("faster_whisper") is not None
    except (ImportError, ValueError):
        return False


def _import_whisper_model_class():
    try:
        from faster_whisper import WhisperModel  # type: ignore
    except ImportError as exc:
        raise SttUnavailableError(
            "Local Faster-Whisper STT is not installed. Browser speech recognition fallback is available."
        ) from exc
    return WhisperModel


def _load_whisper_model():
    """Lazily load one configured model per process without blocking app startup."""
    global _model_instance, _model_signature

    config = get_stt_config()
    if not config.enabled:
        raise SttUnavailableError(
            "Local Faster-Whisper STT is disabled. Browser speech recognition fallback is available."
        )
    if config.provider != STT_ENGINE:
        raise SttUnavailableError(
            f"Unsupported STT provider '{config.provider}'. Configure STT_PROVIDER={STT_ENGINE}."
        )

    with _model_load_lock:
        if _model_instance is not None and _model_signature == config.model_signature:
            return _model_instance

        _set_runtime(status="loading", last_error=None)
        started_at = time.perf_counter()
        try:
            whisper_model = _import_whisper_model_class()
            model_options: dict[str, Any] = {
                "device": config.device,
                "compute_type": config.compute_type,
                "cpu_threads": config.cpu_threads,
                "num_workers": config.num_workers,
                "local_files_only": config.local_files_only,
            }
            if config.download_root:
                model_options["download_root"] = config.download_root
            model = whisper_model(config.model, **model_options)
        except SttUnavailableError:
            _set_runtime(
                status="unavailable",
                last_error="Faster-Whisper package is not installed.",
                model_load_time_ms=_elapsed_ms(started_at),
            )
            raise
        except Exception as exc:
            logger.exception(
                "stt_model_load_failed engine=%s model=%s device=%s compute_type=%s",
                STT_ENGINE,
                config.model,
                config.device,
                config.compute_type,
            )
            _set_runtime(
                status="error",
                last_error=(
                    f"{type(exc).__name__}: model initialization failed; "
                    "check server logs."
                ),
                model_load_time_ms=_elapsed_ms(started_at),
            )
            raise SttUnavailableError(
                "Local Faster-Whisper model could not be loaded. Browser speech recognition fallback is available."
            ) from exc

        _model_instance = model
        _model_signature = config.model_signature
        load_time_ms = _elapsed_ms(started_at)
        _set_runtime(
            status="ready",
            last_error=None,
            model_load_time_ms=load_time_ms,
            loaded_at=datetime.now(UTC).isoformat(),
        )
        logger.info(
            "stt_model_ready engine=%s model=%s device=%s compute_type=%s load_ms=%.2f",
            STT_ENGINE,
            config.model,
            config.device,
            config.compute_type,
            load_time_ms,
        )
        return model


def get_stt_readiness() -> dict[str, Any]:
    """Return provider availability without loading or downloading a model."""
    config = get_stt_config()
    package_installed = _faster_whisper_installed()
    with _runtime_lock:
        runtime = dict(_runtime)
    with _model_load_lock:
        model_loaded = (
            _model_instance is not None
            and _model_signature == config.model_signature
        )

    if not config.enabled:
        status = "disabled"
    elif config.provider != STT_ENGINE:
        status = "misconfigured"
    elif model_loaded:
        status = "ready"
    elif runtime["status"] in {"loading", "error", "unavailable"}:
        status = runtime["status"]
    elif not package_installed:
        status = "unavailable"
    else:
        status = "available"

    return {
        "provider": STT_ENGINE,
        "available": bool(
            config.enabled
            and config.provider == STT_ENGINE
            and package_installed
        ),
        "ready": model_loaded,
        "status": status,
        "package_installed": package_installed,
        "supported_languages": {
            name: details["language_code"]
            for name, details in SUPPORTED_LANGUAGES.items()
        },
        "config": config.public_dict(),
        "runtime": {
            **runtime,
            "model_loaded": model_loaded,
        },
        "fallback": "browser-speech-recognition",
    }


def warmup_stt_model() -> dict[str, Any]:
    """Load the configured model; callers decide whether this may download it."""
    started_at = time.perf_counter()
    _load_whisper_model()
    readiness = get_stt_readiness()
    readiness["warmup_time_ms"] = _elapsed_ms(started_at)
    return readiness


def _background_warmup() -> None:
    try:
        warmup_stt_model()
    except SttUnavailableError as exc:
        # Startup warmup is opt-in and must never make the API process crash.
        logger.warning("stt_warmup_unavailable error=%s", exc)
    except Exception:
        logger.exception("stt_warmup_failed")


def schedule_stt_warmup() -> bool:
    """Start one daemon warmup thread when explicitly enabled by configuration."""
    global _warmup_thread
    config = get_stt_config()
    if not config.enabled or not config.warmup_on_startup:
        return False
    with _runtime_lock:
        if _warmup_thread is not None and _warmup_thread.is_alive():
            return False
        _warmup_thread = threading.Thread(
            target=_background_warmup,
            name="niyamguard-stt-warmup",
            daemon=True,
        )
        _warmup_thread.start()
    return True


def _whisper_language_hint(language_hint: str | None) -> str | None:
    normalized = (language_hint or "").strip().casefold()
    if normalized in {"", "auto", "mixed"}:
        return None
    return _LANGUAGE_HINTS.get(normalized, normalized)


def _detected_language(
    transcript: str,
    language_hint: str | None,
    model_language: str | None,
) -> tuple[str, str, float]:
    language_info = detect_language(transcript, language_hint)
    normalized_model_language = (model_language or "").strip().casefold()
    model_match = _LANGUAGE_NAMES_BY_CODE.get(normalized_model_language)
    if model_match:
        name, language_code = model_match
        return name, language_code, float(language_info["confidence"])
    return (
        str(language_info["detected_language"]),
        str(language_info["language_code"]),
        float(language_info["confidence"]),
    )


def _validate_requested_script(
    transcript: str,
    language_hint: str | None,
    model_language: str | None,
) -> None:
    """Reject confident-looking cross-script output so the browser fallback can retry."""
    requested = _whisper_language_hint(language_hint) or (model_language or "").casefold()
    if requested != "te":
        return
    telugu_characters = sum("\u0c00" <= character <= "\u0c7f" for character in transcript)
    if telugu_characters == 0:
        raise SttTranscriptionError(
            "Telugu speech was not transcribed reliably in Telugu script. Please retry with browser speech recognition."
        )


def transcribe_audio(
    audio_bytes: bytes,
    *,
    filename: str = "audio.webm",
    content_type: str | None = None,
    language_hint: str | None = None,
    fallback_transcript: str | None = None,
) -> SttResult:
    total_started_at = time.perf_counter()
    config = get_stt_config()
    cleaned_fallback = (fallback_transcript or "").strip()
    if cleaned_fallback:
        language_info = detect_language(cleaned_fallback, language_hint)
        return SttResult(
            transcript=cleaned_fallback,
            detected_language=str(language_info["detected_language"]),
            language_code=str(language_info["language_code"]),
            confidence=float(language_info["confidence"]),
            provider="browser-fallback",
            engine="browser-speech-recognition",
            model=None,
            processing_time_ms=_elapsed_ms(total_started_at),
            model_load_time_ms=0.0,
            transcription_time_ms=0.0,
        )

    if not audio_bytes:
        raise SttTranscriptionError("Audio file is empty.")

    model_load_started_at = time.perf_counter()
    model = _load_whisper_model()
    model_load_time_ms = _elapsed_ms(model_load_started_at)
    audio_path: Path | None = None
    transcription_started_at = time.perf_counter()
    try:
        suffix = Path(filename or "audio.webm").suffix or ".webm"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as audio_file:
            audio_file.write(audio_bytes)
            audio_path = Path(audio_file.name)
        segments, info = model.transcribe(
            str(audio_path),
            language=_whisper_language_hint(language_hint),
            vad_filter=config.vad_filter,
            beam_size=config.beam_size,
            condition_on_previous_text=False,
        )
        transcript = " ".join(segment.text.strip() for segment in segments).strip()
    except Exception as exc:
        raise SttTranscriptionError("Could not transcribe audio clearly.") from exc
    finally:
        if audio_path is not None:
            try:
                audio_path.unlink(missing_ok=True)
            except OSError:
                logger.warning("stt_temp_file_cleanup_failed path=%s", audio_path)

    transcription_time_ms = _elapsed_ms(transcription_started_at)
    if not transcript:
        raise SttTranscriptionError("Could not hear clearly. Please repeat.")

    _validate_requested_script(
        transcript,
        language_hint,
        getattr(info, "language", None),
    )

    detected_language, language_code, detector_confidence = _detected_language(
        transcript,
        language_hint,
        getattr(info, "language", None),
    )
    confidence = float(
        getattr(info, "language_probability", 0.0) or detector_confidence
    )
    raw_audio_duration = getattr(info, "duration", None)
    audio_duration_ms = (
        round(float(raw_audio_duration) * 1000, 2)
        if raw_audio_duration is not None
        else None
    )
    processing_time_ms = _elapsed_ms(total_started_at)
    _set_runtime(
        status="ready",
        last_error=None,
        last_transcription_time_ms=transcription_time_ms,
        last_audio_duration_ms=audio_duration_ms,
    )
    return SttResult(
        transcript=transcript,
        detected_language=detected_language,
        language_code=language_code,
        confidence=min(1.0, max(0.0, confidence)),
        provider=STT_RESULT_PROVIDER,
        engine=STT_ENGINE,
        model=config.model,
        processing_time_ms=processing_time_ms,
        model_load_time_ms=model_load_time_ms,
        transcription_time_ms=transcription_time_ms,
        audio_duration_ms=audio_duration_ms,
    )
