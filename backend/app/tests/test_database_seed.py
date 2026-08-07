import pytest

from app.database import SessionLocal
from app.config import settings
from app.models.database_models import (
    CircularDocumentRecord,
    ConnectedSystemSnapshotRecord,
    PolicyRecord,
    PolicyRuleVersionRecord,
)
from app.seed_demo import main as seed_demo_main
from app.knowledge_base import platform_store
from app.knowledge_base.platform_store import read_store
from app.knowledge_base.platform_store import write_store
from app.repositories.policy_store_repository import PolicyStoreConflict


def test_seed_demo_inserts_go_138_into_database(capsys) -> None:
    seed_demo_main()
    output = capsys.readouterr().out
    store = read_store()
    assert "Seeded NiyamGuard" in output
    assert any(circular.circular_number == "GO-138" for circular in store.circulars)
    assert any(rule.current_value == "6" and rule.unit == "months" for rule in store.verified_rules)
    with SessionLocal() as session:
        assert session.query(PolicyRecord).filter_by(collection="verified_rules").count() >= 1
        assert session.query(CircularDocumentRecord).count() >= 2
        assert session.query(PolicyRuleVersionRecord).count() >= 2
        assert session.query(ConnectedSystemSnapshotRecord).count() >= 1


def test_non_demo_runtime_does_not_fall_back_to_legacy_file_store(monkeypatch) -> None:
    monkeypatch.setattr(settings, "legacy_file_store_enabled", False)
    monkeypatch.setattr(platform_store._repository, "load", lambda: None)
    store = read_store()
    assert store.verified_rules == []


def test_stale_policy_store_write_is_rejected() -> None:
    current = read_store()
    stale = read_store()
    current.service_definitions = current.service_definitions[:1]
    write_store(current)

    with pytest.raises(PolicyStoreConflict):
        write_store(stale)
