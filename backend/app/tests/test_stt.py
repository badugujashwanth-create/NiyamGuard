from pathlib import Path
from types import SimpleNamespace

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
    assert body["engine"] == "browser-speech-recognition"
    assert body["timing_ms"]["processing"] >= 0
    assert body["timing_ms"]["model_load"] == 0
    assert body["timing_ms"]["transcription"] == 0


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
    assert body["engine"] == "faster-whisper"
    assert body["fallback"] == "browser-speech-recognition"
    assert body["timing_ms"]["request_total"] >= 0


def test_stt_health_reports_available_without_loading_or_downloading(
    client,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(stt_service, "_faster_whisper_installed", lambda: True)
    monkeypatch.setattr(stt_service, "_model_instance", None)
    monkeypatch.setattr(stt_service, "_model_signature", None)
    monkeypatch.setitem(stt_service._runtime, "status", "not_loaded")
    monkeypatch.setattr(
        stt_service,
        "_load_whisper_model",
        lambda: pytest.fail("health must not load or download a model"),
    )

    response = client.get("/api/stt/health")
    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert body["provider"] == "faster-whisper"
    assert body["available"] is True
    assert body["ready"] is False
    assert body["status"] == "available"
    assert body["supported_languages"]["english"] == "en-IN"
    assert body["supported_languages"]["telugu"] == "te-IN"
    assert body["config"]["model"] == "base"
    assert body["timing_ms"]["health_check"] >= 0


def test_stt_health_reports_missing_provider_without_trying_model_load(
    client,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(stt_service, "_faster_whisper_installed", lambda: False)
    monkeypatch.setattr(stt_service, "_model_instance", None)
    monkeypatch.setattr(stt_service, "_model_signature", None)

    response = client.get("/api/stt/health")
    body = response.json()

    assert response.status_code == 200
    assert body["available"] is False
    assert body["ready"] is False
    assert body["status"] == "unavailable"
    assert body["fallback"] == "browser-speech-recognition"


def test_stt_model_loader_uses_reproducible_environment_config(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    created: list[tuple[str, dict]] = []

    class FakeWhisperModel:
        def __init__(self, model: str, **options) -> None:
            created.append((model, options))

    monkeypatch.setenv("STT_MODEL", "small")
    monkeypatch.setenv("STT_DEVICE", "cuda")
    monkeypatch.setenv("STT_COMPUTE_TYPE", "float16")
    monkeypatch.setenv("STT_CPU_THREADS", "3")
    monkeypatch.setenv("STT_NUM_WORKERS", "2")
    monkeypatch.setenv("STT_DOWNLOAD_ROOT", str(tmp_path / "models"))
    monkeypatch.setenv("STT_LOCAL_FILES_ONLY", "true")
    monkeypatch.setattr(stt_service, "_import_whisper_model_class", lambda: FakeWhisperModel)
    monkeypatch.setattr(stt_service, "_faster_whisper_installed", lambda: True)
    monkeypatch.setattr(stt_service, "_model_instance", None)
    monkeypatch.setattr(stt_service, "_model_signature", None)

    readiness = stt_service.warmup_stt_model()

    assert created == [
        (
            "small",
            {
                "device": "cuda",
                "compute_type": "float16",
                "cpu_threads": 3,
                "num_workers": 2,
                "local_files_only": True,
                "download_root": str(tmp_path / "models"),
            },
        )
    ]
    assert readiness["ready"] is True
    assert readiness["status"] == "ready"
    assert readiness["config"]["model"] == "small"
    assert readiness["warmup_time_ms"] >= 0


@pytest.mark.parametrize(
    ("language_hint", "transcript", "model_language", "expected_name", "expected_code"),
    [
        ("en-IN", "What documents are required?", "en", "english", "en-IN"),
        ("te-IN", "మండలం అంటే ఏమిటి?", "te", "telugu", "te-IN"),
        ("auto", "నెలవారీ ఆదాయం ఎంత?", "te", "telugu", "te-IN"),
    ],
)
def test_faster_whisper_transcribes_english_and_telugu_without_downloading(
    monkeypatch: pytest.MonkeyPatch,
    language_hint: str,
    transcript: str,
    model_language: str,
    expected_name: str,
    expected_code: str,
) -> None:
    calls: list[dict] = []

    class FakeModel:
        def transcribe(self, audio_path: str, **options):
            assert Path(audio_path).read_bytes() == b"synthetic-webm-audio"
            calls.append({"audio_path": audio_path, **options})
            return (
                [SimpleNamespace(text=transcript)],
                SimpleNamespace(
                    language=model_language,
                    language_probability=0.97,
                    duration=1.25,
                ),
            )

    monkeypatch.setenv("STT_BEAM_SIZE", "1")
    monkeypatch.setenv("STT_VAD_FILTER", "true")
    monkeypatch.setattr(stt_service, "_load_whisper_model", lambda: FakeModel())

    result = stt_service.transcribe_audio(
        b"synthetic-webm-audio",
        filename="voice.webm",
        content_type="audio/webm",
        language_hint=language_hint,
    )

    assert result.transcript == transcript
    assert result.detected_language == expected_name
    assert result.language_code == expected_code
    assert result.confidence == pytest.approx(0.97)
    assert result.provider == "local-whisper"
    assert result.engine == "faster-whisper"
    assert result.audio_duration_ms == 1250
    assert result.processing_time_ms >= result.transcription_time_ms >= 0
    assert calls[0]["language"] == stt_service._whisper_language_hint(language_hint)
    assert calls[0]["vad_filter"] is True
    assert calls[0]["beam_size"] == 1
    assert calls[0]["condition_on_previous_text"] is False
    assert not Path(calls[0]["audio_path"]).exists()


def test_stt_transcribe_endpoint_exposes_engine_model_and_timing(
    client,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeModel:
        def transcribe(self, _audio_path: str, **_options):
            return (
                [SimpleNamespace(text="మండలం అంటే ఏమిటి")],
                SimpleNamespace(
                    language="te",
                    language_probability=0.93,
                    duration=0.8,
                ),
            )

    monkeypatch.setattr(stt_service, "_load_whisper_model", lambda: FakeModel())
    response = client.post(
        "/api/stt/transcribe",
        data={"language_hint": "auto"},
        files={"audio": ("voice.webm", b"synthetic-webm-audio", "audio/webm")},
    )
    body = response.json()

    assert response.status_code == 200
    assert body["transcript"] == "మండలం అంటే ఏమిటి"
    assert body["detected_language"] == "telugu"
    assert body["language_code"] == "te-IN"
    assert body["engine"] == "faster-whisper"
    assert body["model"] == "base"
    assert body["timing_ms"]["audio_duration"] == 800
    assert body["timing_ms"]["request_total"] >= 0


def test_telugu_hint_rejects_cross_script_output_for_browser_retry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeModel:
        def transcribe(self, _audio_path: str, **_options):
            return (
                [SimpleNamespace(text="phonetic output in the wrong script")],
                SimpleNamespace(language="te", language_probability=0.99, duration=1.0),
            )

    monkeypatch.setattr(stt_service, "_load_whisper_model", lambda: FakeModel())
    with pytest.raises(stt_service.SttTranscriptionError, match="Telugu script"):
        stt_service.transcribe_audio(
            b"synthetic-webm-audio",
            filename="voice.webm",
            content_type="audio/webm",
            language_hint="te-IN",
        )


def test_startup_warmup_is_opt_in_and_non_blocking(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    events: list[str] = []

    class FakeThread:
        def __init__(self, *, target, name: str, daemon: bool) -> None:
            events.extend([name, str(daemon)])
            self.target = target

        def is_alive(self) -> bool:
            return False

        def start(self) -> None:
            events.append("started")

    monkeypatch.setattr(stt_service.threading, "Thread", FakeThread)
    monkeypatch.setattr(stt_service, "_warmup_thread", None)

    monkeypatch.setenv("STT_WARMUP_ON_STARTUP", "false")
    assert stt_service.schedule_stt_warmup() is False
    assert events == []

    monkeypatch.setenv("STT_WARMUP_ON_STARTUP", "true")
    assert stt_service.schedule_stt_warmup() is True
    assert events == ["niyamguard-stt-warmup", "True", "started"]
