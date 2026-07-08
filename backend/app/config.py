import os
from pathlib import Path

from dotenv import load_dotenv

APP_DIR = Path(__file__).resolve().parent
BACKEND_DIR = APP_DIR.parent
load_dotenv(BACKEND_DIR / ".env")


def _bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _int_env(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


def _csv_env(name: str, default: str) -> list[str]:
    raw = os.getenv(name, default)
    return [item.strip() for item in raw.split(",") if item.strip()]


class Settings:
    app_name: str = os.getenv("APP_NAME", "NiyamGuard AI")
    app_env: str = os.getenv("APP_ENV", "development")
    debug: bool = _bool_env("DEBUG", True)

    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./niyamguard.db")

    secret_key: str = os.getenv("SECRET_KEY", "change-this-secret-key")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = _int_env("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
    refresh_token_expire_days: int = _int_env("REFRESH_TOKEN_EXPIRE_DAYS", 7)

    cors_origins: list[str] = _csv_env(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    )
    trusted_hosts: list[str] = _csv_env(
        "TRUSTED_HOSTS",
        "localhost,127.0.0.1,testserver",
    )

    rate_limit_enabled: bool = _bool_env("RATE_LIMIT_ENABLED", True)
    rate_limit_per_minute: int = _int_env("RATE_LIMIT_PER_MINUTE", 60)

    demo_mode: bool = _bool_env("DEMO_MODE", True)
    seed_demo_on_startup: bool = _bool_env("SEED_DEMO_ON_STARTUP", False)

    log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()


settings = Settings()

APP_NAME = settings.app_name
APP_VERSION = "1.0.0"
PYTHON_REQUIREMENT = "3.12"
SUPPORTED_LANGUAGES = {"english", "telugu", "hindi", "mixed"}

FORMS_DIR = APP_DIR / "data" / "forms"
FORM_SCHEMA_PATH = FORMS_DIR / "income_certificate.json"
TELANGANA_LOCATIONS_PATH = APP_DIR / "data" / "telangana_locations.json"
SESSION_STORAGE_PATH = APP_DIR / "storage" / "sessions.json"
TTS_CACHE_DIR = APP_DIR / "storage" / "tts_cache"
TTS_PROVIDER = os.getenv("TTS_PROVIDER", "auto").strip().lower() or "auto"
ENABLE_GTTS = _bool_env("ENABLE_GTTS", True)
ENABLE_BHASHINI = _bool_env("ENABLE_BHASHINI", False)
