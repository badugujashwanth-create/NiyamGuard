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


def _path_env(name: str, default: Path) -> Path:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    path = Path(raw.strip())
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


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
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5180,http://127.0.0.1:5180",
    )
    trusted_hosts: list[str] = _csv_env(
        "TRUSTED_HOSTS",
        "localhost,127.0.0.1,testserver",
    )

    rate_limit_enabled: bool = _bool_env("RATE_LIMIT_ENABLED", True)
    rate_limit_per_minute: int = _int_env("RATE_LIMIT_PER_MINUTE", 60)

    demo_mode: bool = _bool_env("DEMO_MODE", True)
    seed_demo_on_startup: bool = _bool_env("SEED_DEMO_ON_STARTUP", False)

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
SEED_KNOWLEDGE_PATH = APP_DIR / "data" / "seed_knowledge.json"
