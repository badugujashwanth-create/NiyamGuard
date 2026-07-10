from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    pass


def _engine_kwargs(database_url: str) -> dict:
    if database_url.startswith("sqlite"):
        return {"connect_args": {"check_same_thread": False}}
    return {}


def make_engine(database_url: str | None = None) -> Engine:
    url = database_url or settings.database_url
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return create_engine(url, pool_pre_ping=True, **_engine_kwargs(url))


engine = make_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def import_database_models() -> None:
    import app.models.audit_models  # noqa: F401
    import app.models.auth_models  # noqa: F401
    import app.models.database_models  # noqa: F401
    import app.models.dataset_models  # noqa: F401


def init_db() -> None:
    import_database_models()
    try:
        Base.metadata.create_all(bind=engine)
    except OperationalError as exc:
        if "already exists" not in str(exc).lower():
            raise
    _ensure_runtime_columns()


def _ensure_runtime_columns() -> None:
    inspector = inspect(engine)
    if "audit_events" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("audit_events")}
    additions = []
    if "previous_hash" not in columns:
        additions.append("ALTER TABLE audit_events ADD COLUMN previous_hash VARCHAR(64)")
    if "current_hash" not in columns:
        additions.append("ALTER TABLE audit_events ADD COLUMN current_hash VARCHAR(64)")
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
        return True
    except Exception:
        return False
