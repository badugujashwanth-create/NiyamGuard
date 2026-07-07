import hashlib
import os
import threading
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from gtts import gTTS

from app.config import ENABLE_BHASHINI, ENABLE_GTTS, TTS_CACHE_DIR, TTS_PROVIDER

SUPPORTED_LANGUAGE_CODES = {"te-IN", "hi-IN", "en-IN", "en-US"}
DETECTED_LANGUAGE_CODES = {
    "telugu": "te-IN",
    "hindi": "hi-IN",
    "english": "en-IN",
}
GTTS_LANGUAGE_CODES = {
    "te-IN": "te",
    "hi-IN": "hi",
    "en-IN": "en",
    "en-US": "en",
}
TTS_FAILURE_MESSAGE = (
    "TTS provider failed. Text response is available, but voice audio "
    "could not be generated."
)

_cache_lock = threading.RLock()


class TtsProviderError(RuntimeError):
    pass


@dataclass(frozen=True)
class TtsResult:
    audio: bytes
    language_code: str
    provider: str
    cache_status: str


def normalize_language_code(
    language_code: str | None, detected_language: str | None = None
) -> str:
    normalized = (language_code or "").strip()
    canonical = next(
        (
            supported
            for supported in SUPPORTED_LANGUAGE_CODES
            if supported.casefold() == normalized.casefold()
        ),
        None,
    )
    if canonical:
        return canonical

    detected_code = DETECTED_LANGUAGE_CODES.get(
        (detected_language or "").strip().casefold()
    )
    if detected_code:
        return detected_code
    if not normalized:
        return "en-IN"
    raise ValueError(f"Unsupported TTS language code: {language_code}.")


def language_code_to_gtts_lang(language_code: str) -> str:
    canonical = normalize_language_code(language_code)
    try:
        return GTTS_LANGUAGE_CODES[canonical]
    except KeyError as exc:
        raise ValueError(
            f"Unsupported TTS language code: {language_code}."
        ) from exc


def _resolve_provider(provider: str) -> str:
    normalized = (provider or "auto").strip().casefold()
    if normalized == "auto":
        normalized = TTS_PROVIDER if TTS_PROVIDER != "auto" else "gtts"
    if normalized == "gtts":
        if not ENABLE_GTTS:
            raise TtsProviderError("gTTS is disabled by server configuration.")
        return "gtts"
    if normalized == "bhashini":
        if not ENABLE_BHASHINI:
            raise TtsProviderError(
                "Bhashini TTS is not configured. Use provider 'auto' or 'gtts'."
            )
        raise TtsProviderError("Bhashini TTS is not implemented in this MVP.")
    raise ValueError(f"Unknown TTS provider: {provider}.")


def _cache_path(
    text: str,
    language_code: str,
    provider: str,
    cache_dir: Path,
) -> Path:
    digest = hashlib.sha256(
        f"{provider}\0{language_code}\0{text}".encode("utf-8")
    ).hexdigest()
    return cache_dir / f"{digest}.mp3"


def synthesize_speech(
    text: str,
    language_code: str,
    provider: str = "auto",
    *,
    detected_language: str | None = None,
    cache_dir: Path | None = None,
) -> TtsResult:
    cleaned_text = text.strip()
    if not cleaned_text:
        raise ValueError("TTS text must not be empty.")

    canonical_language = normalize_language_code(
        language_code,
        detected_language,
    )
    resolved_provider = _resolve_provider(provider)
    target_cache_dir = cache_dir or TTS_CACHE_DIR
    target_cache_dir.mkdir(parents=True, exist_ok=True)
    cached_path = _cache_path(
        cleaned_text,
        canonical_language,
        resolved_provider,
        target_cache_dir,
    )

    with _cache_lock:
        if cached_path.exists():
            try:
                cached_audio = cached_path.read_bytes()
            except OSError as exc:
                raise TtsProviderError(TTS_FAILURE_MESSAGE) from exc
            if cached_audio:
                return TtsResult(
                    audio=cached_audio,
                    language_code=canonical_language,
                    provider=resolved_provider,
                    cache_status="HIT",
                )

        if resolved_provider != "gtts":
            raise TtsProviderError(TTS_FAILURE_MESSAGE)

        buffer = BytesIO()
        try:
            gTTS(
                text=cleaned_text,
                lang=language_code_to_gtts_lang(canonical_language),
            ).write_to_fp(buffer)
            audio = buffer.getvalue()
            if not audio:
                raise RuntimeError("TTS provider returned empty audio.")
            temporary_path = cached_path.with_suffix(".tmp")
            temporary_path.write_bytes(audio)
            os.replace(temporary_path, cached_path)
        except Exception as exc:
            raise TtsProviderError(TTS_FAILURE_MESSAGE) from exc

    return TtsResult(
        audio=audio,
        language_code=canonical_language,
        provider=resolved_provider,
        cache_status="MISS",
    )


def synthesize_speech_mp3(
    text: str,
    language_code: str,
    provider: str = "auto",
) -> bytes:
    return synthesize_speech(text, language_code, provider).audio
