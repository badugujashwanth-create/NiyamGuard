from types import SimpleNamespace

import pytest

from app.config import settings, validate_runtime_settings
from app.database import normalize_database_url


@pytest.mark.parametrize(
    ("secret", "debug", "demo_mode"),
    [
        ("change-this-secret-key", False, False),
        ("short", False, False),
        ("a-secure-production-secret-with-32-plus-chars", True, False),
        ("a-secure-production-secret-with-32-plus-chars", False, True),
    ],
)
def test_production_rejects_development_controls(secret: str, debug: bool, demo_mode: bool) -> None:
    candidate = SimpleNamespace(
        app_env="production",
        secret_key=secret,
        debug=debug,
        demo_mode=demo_mode,
    )
    with pytest.raises(RuntimeError):
        validate_runtime_settings(candidate)


def test_production_accepts_hardened_runtime_settings() -> None:
    validate_runtime_settings(
        SimpleNamespace(
            app_env="production",
            secret_key="a-secure-production-secret-with-32-plus-chars",
            debug=False,
            demo_mode=False,
        )
    )


@pytest.mark.parametrize(
    ("input_url", "expected_url"),
    [
        ("postgres://user:pass@db:5432/app", "postgresql+psycopg://user:pass@db:5432/app"),
        ("postgresql://user:pass@db:5432/app", "postgresql+psycopg://user:pass@db:5432/app"),
        ("postgresql+psycopg://user:pass@db:5432/app", "postgresql+psycopg://user:pass@db:5432/app"),
        ("sqlite:///./niyamguard.db", "sqlite:///./niyamguard.db"),
    ],
)
def test_database_url_uses_the_installed_postgres_driver(input_url: str, expected_url: str) -> None:
    assert normalize_database_url(input_url) == expected_url


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("get", "/api/mock-systems"),
        ("post", "/api/demo/run-full-end-to-end"),
        ("get", "/api/virtual-gov/scenarios"),
        ("get", "/api/sandbox/status"),
    ],
)
def test_sandbox_endpoints_disappear_when_demo_mode_is_disabled(
    client, monkeypatch: pytest.MonkeyPatch, method: str, path: str
) -> None:
    monkeypatch.setattr(settings, "demo_mode", False)
    response = getattr(client, method)(path)
    assert response.status_code == 404
    assert response.json()["error"]["message"] == "Sandbox endpoint is disabled outside demo mode."
