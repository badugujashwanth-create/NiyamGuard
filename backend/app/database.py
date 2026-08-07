from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


REQUIRED_RUNTIME_TABLES = frozenset(
    {
        "users",
        "refresh_tokens",
        "audit_events",
        "policy_records",
        "policy_store_revisions",
        "rate_limit_buckets",
        "circular_documents",
        "policy_rule_candidates",
        "policy_rule_deltas",
        "rule_approval_workflows",
        "policy_publication_events",
        "knowledge_update_events",
        "compliance_runs",
        "propagation_plans",
        "propagation_tasks",
        "connected_system_patches",
        "rollback_events",
        "policy_rule_versions",
        "connected_system_snapshots",
        "compliance_findings",
    }
)


class Base(DeclarativeBase):
    pass


def _engine_kwargs(database_url: str) -> dict:
    if database_url.startswith("sqlite"):
        return {"connect_args": {"check_same_thread": False}}
    return {}


def normalize_database_url(database_url: str) -> str:
    url = database_url
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


def make_engine(database_url: str | None = None) -> Engine:
    url = normalize_database_url(database_url or settings.database_url)
    return create_engine(url, pool_pre_ping=True, **_engine_kwargs(url))


engine = make_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def import_database_models() -> None:
    import app.models.audit_models  # noqa: F401
    import app.models.auth_models  # noqa: F401
    import app.models.database_models  # noqa: F401
    import app.models.dataset_models  # noqa: F401
    import app.models.rate_limit_models  # noqa: F401


def init_db() -> None:
    import_database_models()
    if settings.auto_create_tables:
        try:
            Base.metadata.create_all(bind=engine)
        except OperationalError as exc:
            if "already exists" not in str(exc).lower():
                raise
        _ensure_runtime_columns()


def _ensure_runtime_columns() -> None:
    inspector = inspect(engine)
    if "audit_events" not in inspector.get_table_names():
        additions = []
    else:
        additions = []
        columns = {column["name"] for column in inspector.get_columns("audit_events")}
        if "previous_hash" not in columns:
            additions.append("ALTER TABLE audit_events ADD COLUMN previous_hash VARCHAR(64)")
        if "current_hash" not in columns:
            additions.append("ALTER TABLE audit_events ADD COLUMN current_hash VARCHAR(64)")
    if "refresh_tokens" in inspector.get_table_names():
        refresh_columns = {column["name"] for column in inspector.get_columns("refresh_tokens")}
        if "session_id" not in refresh_columns:
            additions.append("ALTER TABLE refresh_tokens ADD COLUMN session_id VARCHAR(120)")
    if "user_sessions" in inspector.get_table_names():
        session_columns = {column["name"] for column in inspector.get_columns("user_sessions")}
        if "revoked_at" not in session_columns:
            additions.append("ALTER TABLE user_sessions ADD COLUMN revoked_at VARCHAR(40)")
    if "policy_rule_candidates" in inspector.get_table_names():
        candidate_columns = {column["name"] for column in inspector.get_columns("policy_rule_candidates")}
        if "source_start_offset" not in candidate_columns:
            additions.append("ALTER TABLE policy_rule_candidates ADD COLUMN source_start_offset INTEGER")
        if "source_end_offset" not in candidate_columns:
            additions.append("ALTER TABLE policy_rule_candidates ADD COLUMN source_end_offset INTEGER")
    if additions:
        with engine.begin() as connection:
            for statement in additions:
                connection.execute(text(statement))


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def database_ready() -> bool:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            tables = set(inspect(connection).get_table_names())
        return REQUIRED_RUNTIME_TABLES.issubset(tables)
    except Exception:
        return False
