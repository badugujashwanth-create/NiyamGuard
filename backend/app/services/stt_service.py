from dataclasses import dataclass
from functools import lru_cache

from app.services.language_helper import detect_language


class SttUnavailableError(RuntimeError):
    pass


class SttTranscriptionError(RuntimeError):
    pass


@dataclass(frozen=True)
class SttResult:
    transcript: str
    detected_language: str
    language_code: str
    confidence: float
    provider: str


@lru_cache(maxsize=1)
def _load_whisper_model():
    try:
        from faster_whisper import WhisperModel  # type: ignore
    except ImportError as exc:
        raise SttUnavailableError(
            "Local Whisper STT is not installed. Browser speech recognition fallback is available."
        ) from exc
    return WhisperModel("base", device="cpu", compute_type="int8")


def transcribe_audio(
    audio_bytes: bytes,
    *,
    filename: str = "audio.webm",
    content_type: str | None = None,
    language_hint: str | None = None,
    fallback_transcript: str | None = None,
) -> SttResult:
    cleaned_fallback = (fallback_transcript or "").strip()
    if cleaned_fallback:
        language_info = detect_language(cleaned_fallback, language_hint)
        return SttResult(
            transcript=cleaned_fallback,
            detected_language=str(language_info["detected_language"]),
            language_code=str(language_info["language_code"]),
            confidence=float(language_info["confidence"]),
            provider="browser-fallback",
        )

    if not audio_bytes:
        raise SttTranscriptionError("Audio file is empty.")

    # The local provider is intentionally optional for the MVP. If faster-whisper
    # is present, use it; otherwise the route returns a clear 503 and the
    # frontend falls back to browser SpeechRecognition.
    model = _load_whisper_model()
    try:
        import tempfile
        from pathlib import Path

        suffix = Path(filename or "audio.webm").suffix or ".webm"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as audio_file:
            audio_file.write(audio_bytes)
            audio_path = audio_file.name
        segments, info = model.transcribe(
            audio_path,
            language=None if language_hint in {None, "", "auto"} else language_hint,
            vad_filter=True,
        )
        transcript = " ".join(segment.text.strip() for segment in segments).strip()
    except Exception as exc:
        raise SttTranscriptionError("Could not transcribe audio clearly.") from exc

    if not transcript:
        raise SttTranscriptionError("Could not hear clearly. Please repeat.")

    language_info = detect_language(transcript, language_hint)
    confidence = float(getattr(info, "language_probability", 0.0) or language_info["confidence"])
    return SttResult(
        transcript=transcript,
        detected_language=str(language_info["detected_language"]),
        language_code=str(language_info["language_code"]),
        confidence=min(1.0, max(0.0, confidence)),
        provider="local-whisper",
    )
