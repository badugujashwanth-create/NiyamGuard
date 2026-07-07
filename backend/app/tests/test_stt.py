import pytest

from app.services import stt_service


def test_stt_endpoint_accepts_browser_fallback_transcript(client) -> None:
    response = client.post(
        "/api/stt/transcribe",
        data={
            "language_hint": "auto",
            "form_id": "income_certificate",
            "session_id": "session-123",
            "fallback_transcript": "purpose lo scholarship ani rayacha",
        },
        files={"audio": ("voice.webm", b"fallback-only", "audio/webm")},
    )
    body = response.json()
    assert response.status_code == 200
    assert body["success"] is True
    assert body["transcript"] == "purpose lo scholarship ani rayacha"
    assert body["detected_language"] == "telugu"
    assert body["language_code"] == "te-IN"
    assert body["provider"] == "browser-fallback"


def test_stt_endpoint_reports_optional_local_provider_unavailable(
    client,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def unavailable():
        raise stt_service.SttUnavailableError(
            "Local Whisper STT is not installed. Browser speech recognition fallback is available."
        )

    monkeypatch.setattr(stt_service, "_load_whisper_model", unavailable)
    response = client.post(
        "/api/stt/transcribe",
        data={"language_hint": "auto"},
        files={"audio": ("voice.webm", b"fake-audio", "audio/webm")},
    )
    body = response.json()
    assert response.status_code == 503
    assert body["success"] is False
    assert body["provider"] == "unavailable"
    assert body["fallback"] == "browser-speech-recognition"
