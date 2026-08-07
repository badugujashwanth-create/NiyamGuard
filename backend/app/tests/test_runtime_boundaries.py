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
            cors_origins=["https://example.gov"],
            trusted_hosts=["api.example.gov"],
            malware_scan_mode="clamav",
            auth_cookie_mode=True,
            auth_cookie_secure=True,
            auth_cookie_samesite="strict",
            legacy_file_store_enabled=False,
            session_records_required=True,
            rate_limit_backend="database",
            database_url="postgresql+psycopg://user:pass@db:5432/niyamguard",
        )
    )


def test_staging_is_hardened_and_rejects_demo_mode() -> None:
    with pytest.raises(RuntimeError, match="DEMO_MODE"):
        validate_runtime_settings(
            SimpleNamespace(
                app_env="staging",
                secret_key="a-secure-production-secret-with-32-plus-chars",
                debug=False,
                demo_mode=True,
                cors_origins=["https://example.gov"],
                trusted_hosts=["api.example.gov"],
                malware_scan_mode="clamav",
                auth_cookie_mode=True,
                auth_cookie_secure=True,
                auth_cookie_samesite="strict",
                legacy_file_store_enabled=False,
                session_records_required=True,
                rate_limit_backend="database",
                database_url="postgresql+psycopg://user:pass@db:5432/niyamguard",
            )
        )


def test_hardened_environment_rejects_sqlite_database() -> None:
    with pytest.raises(RuntimeError, match="PostgreSQL"):
        validate_runtime_settings(
            SimpleNamespace(
                app_env="production",
                secret_key="a-secure-production-secret-with-32-plus-chars",
                debug=False,
                demo_mode=False,
                cors_origins=["https://example.gov"],
                trusted_hosts=["api.example.gov"],
                malware_scan_mode="clamav",
                auth_cookie_mode=True,
                auth_cookie_secure=True,
                auth_cookie_samesite="strict",
                legacy_file_store_enabled=False,
                session_records_required=True,
                rate_limit_backend="database",
                database_url="sqlite:///./niyamguard.db",
            )
        )


@pytest.mark.parametrize(
    "overrides",
    [
        {"cors_origins": ["*"]},
        {"trusted_hosts": ["*"]},
        {"trusted_hosts": []},
    ],
)
def test_production_rejects_wildcard_or_empty_network_boundaries(overrides: dict[str, list[str]]) -> None:
    values = {
        "app_env": "production",
        "secret_key": "a-secure-production-secret-with-32-plus-chars",
        "debug": False,
        "demo_mode": False,
        "cors_origins": ["https://example.gov"],
        "trusted_hosts": ["api.example.gov"],
    }
    values.update(overrides)
    candidate = SimpleNamespace(**values)
    with pytest.raises(RuntimeError):
        validate_runtime_settings(candidate)


def test_production_requires_malware_scanning() -> None:
    candidate = SimpleNamespace(
        app_env="production",
        secret_key="a-secure-production-secret-with-32-plus-chars",
        debug=False,
        demo_mode=False,
        cors_origins=["https://example.gov"],
        trusted_hosts=["api.example.gov"],
        malware_scan_mode="disabled",
    )
    with pytest.raises(RuntimeError, match="MALWARE_SCAN_MODE"):
        validate_runtime_settings(candidate)


def test_production_requires_source_artifact_storage() -> None:
    candidate = SimpleNamespace(
        app_env="production",
        secret_key="a-secure-production-secret-with-32-plus-chars",
        debug=False,
        demo_mode=False,
        cors_origins=["https://example.gov"],
        trusted_hosts=["api.example.gov"],
        malware_scan_mode="clamav",
        circular_artifact_storage_enabled=False,
    )
    with pytest.raises(RuntimeError, match="CIRCULAR_ARTIFACT_STORAGE_ENABLED"):
        validate_runtime_settings(candidate)


def test_production_requires_cookie_auth() -> None:
    candidate = SimpleNamespace(
        app_env="production",
        secret_key="a-secure-production-secret-with-32-plus-chars",
        debug=False,
        demo_mode=False,
        cors_origins=["https://example.gov"],
        trusted_hosts=["api.example.gov"],
        malware_scan_mode="clamav",
        auth_cookie_mode=False,
        auth_cookie_secure=True,
        auth_cookie_samesite="strict",
    )
    with pytest.raises(RuntimeError, match="AUTH_COOKIE_MODE"):
        validate_runtime_settings(candidate)


def test_production_requires_database_authority() -> None:
    candidate = SimpleNamespace(
        app_env="production",
        secret_key="a-secure-production-secret-with-32-plus-chars",
        debug=False,
        demo_mode=False,
        cors_origins=["https://example.gov"],
        trusted_hosts=["api.example.gov"],
        malware_scan_mode="clamav",
        auth_cookie_mode=True,
        auth_cookie_secure=True,
        auth_cookie_samesite="strict",
        legacy_file_store_enabled=True,
    )
    with pytest.raises(RuntimeError, match="LEGACY_FILE_STORE_ENABLED"):
        validate_runtime_settings(candidate)


def test_production_requires_revocable_sessions() -> None:
    candidate = SimpleNamespace(
        app_env="production",
        secret_key="a-secure-production-secret-with-32-plus-chars",
        debug=False,
        demo_mode=False,
        cors_origins=["https://example.gov"],
        trusted_hosts=["api.example.gov"],
        malware_scan_mode="clamav",
        auth_cookie_mode=True,
        auth_cookie_secure=True,
        auth_cookie_samesite="strict",
        legacy_file_store_enabled=False,
        session_records_required=False,
    )
    with pytest.raises(RuntimeError, match="SESSION_RECORDS_REQUIRED"):
        validate_runtime_settings(candidate)


def test_production_requires_database_rate_limiting() -> None:
    candidate = SimpleNamespace(
        app_env="production",
        secret_key="a-secure-production-secret-with-32-plus-chars",
        debug=False,
        demo_mode=False,
        cors_origins=["https://example.gov"],
        trusted_hosts=["api.example.gov"],
        malware_scan_mode="clamav",
        auth_cookie_mode=True,
        auth_cookie_secure=True,
        auth_cookie_samesite="strict",
        legacy_file_store_enabled=False,
        session_records_required=True,
        rate_limit_backend="memory",
    )
    with pytest.raises(RuntimeError, match="RATE_LIMIT_BACKEND"):
        validate_runtime_settings(candidate)


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


def test_demo_otp_endpoints_disappear_when_demo_mode_is_disabled(
    client, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "demo_mode", False)
    response = client.post(
        "/api/security/otp/request",
        json={"channel": "sms", "destination": "9876543210"},
    )
    assert response.status_code == 404
    assert response.json()["error"]["message"] == "Sandbox endpoint is disabled outside demo mode."


def test_ops_status_does_not_disclose_filesystem_paths(client, viewer_headers) -> None:
    response = client.get("/api/ops/status", headers=viewer_headers)
    assert response.status_code == 200
    dataset = response.json()["dataset"]
    assert "pack" in dataset
    assert "pack_dir" not in dataset
    assert ":\\" not in str(dataset)
