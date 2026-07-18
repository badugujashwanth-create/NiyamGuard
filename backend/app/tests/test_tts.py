from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.services import tts_service


class FakeCommunicate:
    calls: list[tuple[str, str]] = []

    def __init__(self, text: str, voice: str) -> None:
        self.text = text
        self.voice = voice
        self.calls.append((text, voice))

    def save_sync(self, target: str) -> None:
        Path(target).write_bytes(b"ID3-niyamguard-test-audio")


@pytest.fixture(autouse=True)
def isolated_tts(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    FakeCommunicate.calls = []
    monkeypatch.setattr(tts_service.edge_tts, "Communicate", FakeCommunicate)
    monkeypatch.setattr(tts_service, "TTS_CACHE_DIR", tmp_path / "tts-cache")


def test_tts_health(client: TestClient) -> None:
    response = client.get("/api/tts/health")
    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "available_providers": ["browser", "edge_tts"],
        "default_provider": "edge_tts",
        "supported_languages": {
            "telugu": "te-IN",
            "hindi": "hi-IN",
            "english": "en-IN",
        },
    }


def test_cors_exposes_tts_metadata_headers(client: TestClient) -> None:
    response = client.post(
        "/api/tts/speak",
        json={"text": "Hello", "language_code": "en-IN"},
        headers={
            "Origin": "http://127.0.0.1:5173",
        },
    )
    assert response.status_code == 200
    exposed = response.headers["access-control-expose-headers"]
    assert "X-TTS-Language-Code" in exposed
    assert "X-TTS-Provider" in exposed
    assert "X-TTS-Cache" in exposed


@pytest.mark.parametrize(
    ("text", "language_code", "edge_voice"),
    [
        ("నమస్తే", "te-IN", "te-IN-ShrutiNeural"),
        ("नमस्ते", "hi-IN", "hi-IN-SwaraNeural"),
        ("Hello", "en-IN", "en-IN-NeerjaNeural"),
    ],
)
def test_tts_speak_returns_mp3(
    client: TestClient,
    text: str,
    language_code: str,
    edge_voice: str,
) -> None:
    response = client.post(
        "/api/tts/speak",
        json={
            "text": text,
            "language_code": language_code,
            "provider": "auto",
        },
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("audio/mpeg")
    assert response.headers["x-tts-language-code"] == language_code
    assert response.headers["x-tts-provider"] == "edge_tts"
    assert response.headers["x-tts-cache"] == "MISS"
    assert response.content.startswith(b"ID3")
    assert FakeCommunicate.calls[-1] == (text, edge_voice)


def test_tts_cache_uses_hashed_filename(client: TestClient) -> None:
    payload = {
        "text": "private spoken reply",
        "language_code": "en-IN",
        "provider": "edge_tts",
    }
    first = client.post("/api/tts/speak", json=payload)
    second = client.post("/api/tts/speak", json=payload)

    assert first.headers["x-tts-cache"] == "MISS"
    assert second.headers["x-tts-cache"] == "HIT"
    assert len(FakeCommunicate.calls) == 1
    cached_files = list(tts_service.TTS_CACHE_DIR.glob("*.mp3"))
    assert len(cached_files) == 1
    assert "private" not in cached_files[0].name
    assert len(cached_files[0].stem) == 64


def test_empty_tts_text_returns_400(client: TestClient) -> None:
    response = client.post(
        "/api/tts/speak",
        json={"text": "  ", "language_code": "te-IN"},
    )
    assert response.status_code == 400
    assert response.json()["success"] is False


def test_unsupported_tts_language_returns_400(client: TestClient) -> None:
    response = client.post(
        "/api/tts/speak",
        json={"text": "Bonjour", "language_code": "fr-FR"},
    )
    assert response.status_code == 400
    assert "Unsupported TTS language" in response.json()["message"]


def test_unknown_tts_provider_returns_400(client: TestClient) -> None:
    response = client.post(
        "/api/tts/speak",
        json={
            "text": "Hello",
            "language_code": "en-IN",
            "provider": "unknown",
        },
    )
    assert response.status_code == 400
    assert "Unknown TTS provider" in response.json()["message"]


def test_tts_provider_failure_returns_503(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    class BrokenCommunicate(FakeCommunicate):
        def save_sync(self, target: str) -> None:
            raise OSError("network unavailable")

    monkeypatch.setattr(tts_service.edge_tts, "Communicate", BrokenCommunicate)
    response = client.post(
        "/api/tts/speak",
        json={"text": "నమస్తే", "language_code": "te-IN"},
    )
    assert response.status_code == 503
    assert response.json() == {
        "success": False,
        "message": (
            "TTS provider failed. Text response is available, but voice "
            "audio could not be generated."
        ),
    }
