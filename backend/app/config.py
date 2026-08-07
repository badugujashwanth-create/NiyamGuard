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


def _float_env(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except ValueError:
        return default


def _csv_env(name: str, default: str) -> list[str]:
    raw = os.getenv(name, default)
    return [item.strip() for item in raw.split(",") if item.strip()]


PROJECT_ROOT = BACKEND_DIR.parent
HARDENED_ENVIRONMENTS = frozenset({"production", "prod", "staging"})


def _path_env(name: str, default: Path) -> Path:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    path = Path(raw.strip())
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


class Settings:
    app_name: str = os.getenv("APP_NAME", "NiyamGuard")
    app_env: str = os.getenv("APP_ENV", "development")
    debug: bool = _bool_env("DEBUG", True)
    auto_create_tables: bool = _bool_env(
        "AUTO_CREATE_TABLES",
        app_env.strip().lower() not in HARDENED_ENVIRONMENTS,
    )
    legacy_file_store_enabled: bool = _bool_env(
        "LEGACY_FILE_STORE_ENABLED",
        app_env.strip().lower() not in HARDENED_ENVIRONMENTS,
    )

    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./niyamguard.db")

    secret_key: str = os.getenv("SECRET_KEY", "change-this-secret-key")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_issuer: str = os.getenv("JWT_ISSUER", "niyamguard")
    jwt_audience: str = os.getenv("JWT_AUDIENCE", "niyamguard-users")
    access_token_expire_minutes: int = _int_env("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
    refresh_token_expire_days: int = _int_env("REFRESH_TOKEN_EXPIRE_DAYS", 7)
    # Browser deployments can keep tokens out of JavaScript-visible storage by
    # opting into same-origin HttpOnly cookies. Bearer/localStorage remains
    # available for the local synthetic demo only.
    auth_cookie_mode: bool = _bool_env("AUTH_COOKIE_MODE", False)
    auth_cookie_secure: bool = _bool_env("AUTH_COOKIE_SECURE", False)
    auth_cookie_samesite: str = os.getenv("AUTH_COOKIE_SAMESITE", "strict").strip().lower() or "strict"
    session_records_required: bool = _bool_env(
        "SESSION_RECORDS_REQUIRED",
        app_env.strip().lower() in HARDENED_ENVIRONMENTS,
    )

    cors_origins: list[str] = _csv_env(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5180,http://127.0.0.1:5180",
    )
    trusted_hosts: list[str] = _csv_env(
        "TRUSTED_HOSTS",
        "localhost,127.0.0.1,testserver",
    )

    rate_limit_enabled: bool = _bool_env("RATE_LIMIT_ENABLED", True)
    rate_limit_per_minute: int = _int_env("RATE_LIMIT_PER_MINUTE", 60)
    rate_limit_backend: str = os.getenv("RATE_LIMIT_BACKEND", "memory").strip().lower() or "memory"

    # Demo endpoints and seeded identities are opt-in.  A fresh deployment must
    # not expose synthetic credentials or mutation-only sandbox routes by
    # accident simply because an environment variable was omitted.
    demo_mode: bool = _bool_env("DEMO_MODE", False)
    seed_demo_on_startup: bool = _bool_env("SEED_DEMO_ON_STARTUP", False)
    show_demo_credentials: bool = _bool_env("SHOW_DEMO_CREDENTIALS", False)
    enable_demo_reset: bool = _bool_env("ENABLE_DEMO_RESET", False)
    enable_synthetic_controls: bool = _bool_env("ENABLE_SYNTHETIC_CONTROLS", False)

    stt_max_upload_bytes: int = _int_env("STT_MAX_UPLOAD_BYTES", 10 * 1024 * 1024)
    tts_max_characters: int = _int_env("TTS_MAX_CHARACTERS", 2_000)
    tts_cache_max_files: int = _int_env("TTS_CACHE_MAX_FILES", 256)
    tts_cache_max_bytes: int = _int_env("TTS_CACHE_MAX_BYTES", 64 * 1024 * 1024)
    malware_scan_mode: str = os.getenv("MALWARE_SCAN_MODE", "disabled").strip().lower() or "disabled"
    malware_scan_command: str = os.getenv("MALWARE_SCAN_COMMAND", "clamscan").strip() or "clamscan"
    malware_scan_timeout_seconds: int = _int_env("MALWARE_SCAN_TIMEOUT_SECONDS", 30)
    circular_artifact_storage_enabled: bool = _bool_env("CIRCULAR_ARTIFACT_STORAGE_ENABLED", True)
    circular_artifact_storage_dir: Path = _path_env(
        "CIRCULAR_ARTIFACT_STORAGE_DIR",
        BACKEND_DIR / "storage" / "circulars",
    )
    object_storage_backend: str = os.getenv("OBJECT_STORAGE_BACKEND", "local").strip().lower() or "local"
    object_storage_root: Path = _path_env(
        "OBJECT_STORAGE_ROOT",
        BACKEND_DIR / "storage",
    )
    object_storage_bucket: str = os.getenv("OBJECT_STORAGE_BUCKET", "").strip()
    object_storage_endpoint_url: str = os.getenv("OBJECT_STORAGE_ENDPOINT_URL", "").strip()
    object_storage_region: str = os.getenv("OBJECT_STORAGE_REGION", "us-east-1").strip() or "us-east-1"
    object_storage_access_key_id: str = os.getenv("OBJECT_STORAGE_ACCESS_KEY_ID", "").strip()
    object_storage_secret_access_key: str = os.getenv("OBJECT_STORAGE_SECRET_ACCESS_KEY", "").strip()
    object_storage_use_ssl: bool = _bool_env("OBJECT_STORAGE_USE_SSL", True)

    ocr_enabled: bool = _bool_env("OCR_ENABLED", False)
    ocr_command: str = os.getenv("OCR_COMMAND", "ocrmypdf").strip() or "ocrmypdf"
    ocr_languages: str = os.getenv("OCR_LANGUAGES", "eng").strip() or "eng"
    # Keep the scanned-document trigger below the existing 20-character
    # minimum accepted by the circular ingestion boundary.  A short but
    # legitimate native PDF must not be sent through OCR just because it is
    # concise; zero/near-zero native text remains the scanned-PDF signal.
    ocr_min_text_chars: int = _int_env("OCR_MIN_TEXT_CHARS", 20)
    ocr_min_text_density: float = _float_env("OCR_MIN_TEXT_DENSITY", 0.0005)
    ocr_timeout_seconds: int = _int_env("OCR_TIMEOUT_SECONDS", 120)

    ai_provider: str = os.getenv("AI_PROVIDER", "ollama").strip().lower() or "ollama"
    ai_enabled: bool = _bool_env("AI_ENABLED", False)
    answer_engine: str = os.getenv("ANSWER_ENGINE", "hybrid_intelligence").strip().lower() or "hybrid_intelligence"
    search_engine_enabled: bool = _bool_env("SEARCH_ENGINE_ENABLED", True)
    bm25_enabled: bool = _bool_env("BM25_ENABLED", True)
    semantic_search_enabled: bool = _bool_env("SEMANTIC_SEARCH_ENABLED", True)
    answer_templates_enabled: bool = _bool_env("ANSWER_TEMPLATES_ENABLED", True)
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-small")
    vector_store: str = os.getenv("VECTOR_STORE", "local").strip().lower() or "local"
    vector_index_path: Path = _path_env("VECTOR_INDEX_PATH", PROJECT_ROOT / "data" / "vector_index")
    search_index_path: Path = _path_env("SEARCH_INDEX_PATH", PROJECT_ROOT / "data" / "search_index")
    search_top_k: int = _int_env("SEARCH_TOP_K", 5)
    search_min_score: float = _float_env("SEARCH_MIN_SCORE", 0.25)
    llm_optional: bool = _bool_env("LLM_OPTIONAL", True)
    llm_required: bool = _bool_env("LLM_REQUIRED", False)
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "qwen2.5:7b-instruct")
    ollama_fallback_model: str = os.getenv("OLLAMA_FALLBACK_MODEL", "llama3.2:3b")
    ai_timeout_seconds: int = _int_env("AI_TIMEOUT_SECONDS", 45)
    ai_max_retries: int = _int_env("AI_MAX_RETRIES", 2)
    ai_require_sources: bool = _bool_env("AI_REQUIRE_SOURCES", True)
    hf_api_token: str = os.getenv("HF_API_TOKEN", "")
    hf_model: str = os.getenv("HF_MODEL", "Qwen/Qwen2.5-7B-Instruct")
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_model: str = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    rag_enabled: bool = _bool_env("RAG_ENABLED", True)
    rag_top_k: int = _int_env("RAG_TOP_K", 5)
    rag_min_score: float = _float_env("RAG_MIN_SCORE", 0.25)
    rag_index_path: Path = _path_env("RAG_INDEX_PATH", PROJECT_ROOT / "data" / "rag_index")
    dataset_dir: Path = _path_env("DATASET_DIR", PROJECT_ROOT / "data" / "datasets")
    dataset_pack_dir: Path = _path_env(
        "DATASET_PACK_DIR",
        PROJECT_ROOT / "data" / "niyamguard_dataset_pack_v1",
    )
    processed_dataset_dir: Path = _path_env(
        "PROCESSED_DATASET_DIR",
        PROJECT_ROOT / "data" / "processed",
    )

    auto_sync_enabled: bool = _bool_env("AUTO_SYNC_ENABLED", False)
    auto_sync_interval_minutes: int = _int_env("AUTO_SYNC_INTERVAL_MINUTES", 60)
    auto_approve_demo_updates: bool = _bool_env("AUTO_APPROVE_DEMO_UPDATES", False)
    auto_patch_demo_systems: bool = _bool_env("AUTO_PATCH_DEMO_SYSTEMS", False)
    circular_source_mode: str = os.getenv("CIRCULAR_SOURCE_MODE", "manual").strip().lower() or "manual"
    circular_source_registry_path: Path = _path_env(
        "CIRCULAR_SOURCE_REGISTRY_PATH",
        PROJECT_ROOT / "data" / "source_registry.json",
    )
    policy_update_requires_approval: bool = _bool_env("POLICY_UPDATE_REQUIRES_APPROVAL", True)
    policy_rollback_enabled: bool = _bool_env("POLICY_ROLLBACK_ENABLED", True)
    rag_reindex_on_policy_update: bool = _bool_env("RAG_REINDEX_ON_POLICY_UPDATE", True)
    compliance_rerun_on_policy_update: bool = _bool_env("COMPLIANCE_RERUN_ON_POLICY_UPDATE", True)

    log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()


settings = Settings()


_PLACEHOLDER_SECRETS = {
    "change-this-secret-key",
    "change-this-secret-key-before-production",
    "ci-secret-key",
}


def validate_runtime_settings(candidate: Settings = settings) -> None:
    """Fail closed when a hosted/hardened environment uses demo controls."""

    environment = candidate.app_env.strip().lower()
    if environment not in HARDENED_ENVIRONMENTS:
        return
    malware_scan_mode = getattr(candidate, "malware_scan_mode", "disabled")
    if malware_scan_mode != "clamav":
        raise RuntimeError("Production requires MALWARE_SCAN_MODE=clamav for untrusted document uploads.")
    if not getattr(candidate, "circular_artifact_storage_enabled", True):
        raise RuntimeError("Production requires CIRCULAR_ARTIFACT_STORAGE_ENABLED=true for source provenance.")
    secret = candidate.secret_key.strip()
    if len(secret) < 32 or secret.lower() in _PLACEHOLDER_SECRETS:
        raise RuntimeError("Production requires a non-placeholder SECRET_KEY of at least 32 characters.")
    if candidate.debug:
        raise RuntimeError("DEBUG must be false in production.")
    if candidate.demo_mode:
        raise RuntimeError("DEMO_MODE must be false in production.")
    if getattr(candidate, "show_demo_credentials", False):
        raise RuntimeError("SHOW_DEMO_CREDENTIALS must be false in production.")
    if getattr(candidate, "enable_demo_reset", False):
        raise RuntimeError("ENABLE_DEMO_RESET must be false in production.")
    if getattr(candidate, "enable_synthetic_controls", False):
        raise RuntimeError("ENABLE_SYNTHETIC_CONTROLS must be false in production.")
    cors_origins = getattr(candidate, "cors_origins", [])
    if "*" in cors_origins:
        raise RuntimeError("CORS_ORIGINS must list explicit origins when credentials are enabled.")
    trusted_hosts = getattr(candidate, "trusted_hosts", [])
    if not trusted_hosts or "*" in trusted_hosts:
        raise RuntimeError("TRUSTED_HOSTS must list explicit hosts in production.")
    if not getattr(candidate, "auth_cookie_mode", False):
        raise RuntimeError("Production requires AUTH_COOKIE_MODE=true for browser sessions.")
    if not getattr(candidate, "auth_cookie_secure", False):
        raise RuntimeError("Production requires AUTH_COOKIE_SECURE=true.")
    if getattr(candidate, "auth_cookie_samesite", "strict") not in {"strict", "lax"}:
        raise RuntimeError("AUTH_COOKIE_SAMESITE must be strict or lax in production.")
    if getattr(candidate, "legacy_file_store_enabled", True):
        raise RuntimeError("Production requires LEGACY_FILE_STORE_ENABLED=false; authoritative state must come from the database.")
    if not getattr(candidate, "session_records_required", False):
        raise RuntimeError("Production requires SESSION_RECORDS_REQUIRED=true for revocable access sessions.")
    if getattr(candidate, "rate_limit_backend", "memory") != "database":
        raise RuntimeError("Production requires RATE_LIMIT_BACKEND=database for cross-worker request limiting.")
    database_url = str(getattr(candidate, "database_url", "")).strip().lower()
    scheme = database_url.split(":", 1)[0] if ":" in database_url else ""
    if not database_url or scheme == "sqlite" or scheme.startswith("sqlite+"):
        raise RuntimeError("Hardened environments require a PostgreSQL DATABASE_URL; SQLite is local/demo only.")
    if scheme not in {"postgres", "postgresql"} and not scheme.startswith("postgresql+"):
        raise RuntimeError("Hardened environments require a PostgreSQL DATABASE_URL.")
    if getattr(candidate, "object_storage_backend", "local") != "s3":
        raise RuntimeError("Hardened environments require OBJECT_STORAGE_BACKEND=s3 for durable document storage.")
    if not getattr(candidate, "object_storage_bucket", "").strip():
        raise RuntimeError("Hardened environments require OBJECT_STORAGE_BUCKET.")
    if not getattr(candidate, "object_storage_access_key_id", "").strip():
        raise RuntimeError("Hardened environments require OBJECT_STORAGE_ACCESS_KEY_ID.")
    if not getattr(candidate, "object_storage_secret_access_key", "").strip():
        raise RuntimeError("Hardened environments require OBJECT_STORAGE_SECRET_ACCESS_KEY.")
    if not getattr(candidate, "ocr_enabled", False):
        raise RuntimeError("Hardened environments require OCR_ENABLED=true for scanned-document processing.")
    if not getattr(candidate, "ocr_command", "").strip():
        raise RuntimeError("Hardened environments require OCR_COMMAND.")


def runtime_config_health(candidate: Settings = settings) -> dict[str, object]:
    """Return a redacted readiness result without exposing secret values."""

    hardened = candidate.app_env.strip().lower() in HARDENED_ENVIRONMENTS
    if not hardened:
        return {"required": False, "ready": True, "environment": candidate.app_env}
    try:
        validate_runtime_settings(candidate)
    except RuntimeError as exc:
        return {"required": True, "ready": False, "environment": candidate.app_env, "error": str(exc)}
    return {"required": True, "ready": True, "environment": candidate.app_env}

APP_NAME = settings.app_name
APP_VERSION = "1.1.0"
PYTHON_REQUIREMENT = "3.12"
SUPPORTED_LANGUAGES = {"english", "telugu", "hindi", "mixed"}

FORMS_DIR = APP_DIR / "data" / "forms"
FORM_SCHEMA_PATH = FORMS_DIR / "income_certificate.json"
TELANGANA_LOCATIONS_PATH = APP_DIR / "data" / "telangana_locations.json"
SESSION_STORAGE_PATH = APP_DIR / "storage" / "sessions.json"
TTS_CACHE_DIR = APP_DIR / "storage" / "tts_cache"
TTS_PROVIDER = os.getenv("TTS_PROVIDER", "auto").strip().lower() or "auto"
ENABLE_EDGE_TTS = _bool_env("ENABLE_EDGE_TTS", True)
ENABLE_BHASHINI = _bool_env("ENABLE_BHASHINI", False)
SEED_KNOWLEDGE_PATH = APP_DIR / "data" / "seed_knowledge.json"
