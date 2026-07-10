from app.data_pipeline.dataset_pack_loader import (
    PACK_VERSION,
    build_dataset_pack_index,
    import_dataset_pack,
)
from app.repositories.dataset_repository import dataset_repository
from app.demo.dataset_service import rag_search


def test_dataset_import_is_idempotent() -> None:
    first = import_dataset_pack()
    second = import_dataset_pack()
    assert first["total_records"] == 18531
    assert second["total_records"] == 18531
    assert dataset_repository.count(PACK_VERSION) == 18531
    assert second["collections"]["regulatory_circulars"] == 220
    assert second["collections"]["obligations"] == 758


def test_dataset_rag_index_searches_pack_content() -> None:
    build_dataset_pack_index()
    results = rag_search("Why is ORG-0029 high risk?", top_k=3)
    assert results
    assert results[0]["source"]["type"] in {
        "policy_qa_pair",
        "risk_scoring_label",
        "regulatory_circular",
        "obligation",
    }
