from app.database import SessionLocal
from app.models.database_models import PolicyRecord
from app.seed_demo import main as seed_demo_main
from app.knowledge_base.platform_store import read_store


def test_seed_demo_inserts_go_138_into_database(capsys) -> None:
    seed_demo_main()
    output = capsys.readouterr().out
    store = read_store()
    assert "Seeded NiyamGuard" in output
    assert any(circular.circular_number == "GO-138" for circular in store.circulars)
    assert any(rule.current_value == "6" and rule.unit == "months" for rule in store.verified_rules)
    with SessionLocal() as session:
        assert session.query(PolicyRecord).filter_by(collection="verified_rules").count() >= 1
