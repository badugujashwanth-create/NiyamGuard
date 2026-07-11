from app.services.answer_engine import answer_question
from app.services.answer_engine import bm25_search, hybrid_retriever


def test_hybrid_answer_exact_rule_has_source(client) -> None:
    response = client.post("/api/hybrid/answer", json={"question": "income certificate validity entha"})
    body = response.json()
    assert response.status_code == 200
    assert body["method"] == "exact_rule_engine"
    assert body["verified"] is True
    assert body["sources"][0]["circular_number"] == "GO-138"


def test_hybrid_answer_decision_table_for_documents(client) -> None:
    response = client.post("/api/hybrid/answer", json={"question": "scholarship documents enti"})
    body = response.json()
    assert response.status_code == 200
    assert body["method"] == "decision_table"
    assert body["service_id"] == "post_matric_scholarship"
    assert body["sources"][0]["type"] == "service_definition"
    assert "Caste Certificate" in body["answer"]


def test_hybrid_answer_compares_schemes_from_structured_rules(client) -> None:
    response = client.post("/api/hybrid/answer", json={"question": "compare post matric scholarship vs old age pension"})
    body = response.json()
    assert response.status_code == 200
    assert body["method"] == "decision_table"
    assert body["verified"] is True
    assert "Post-Matric Scholarship" in body["answer"]
    assert "Old-Age Pension" in body["answer"]


def test_hybrid_unknown_question_uses_safe_fallback(client) -> None:
    response = client.post("/api/hybrid/answer", json={"question": "unknown secret subsidy rule"})
    body = response.json()
    assert response.status_code == 200
    assert body["method"] == "safe_fallback"
    assert body["fallback"] is True
    assert body["sources"] == []


def test_search_status_and_results(client) -> None:
    status_response = client.get("/api/search/status")
    assert status_response.status_code == 200
    assert status_response.json()["indexed_chunks"] > 0

    search_response = client.get("/api/search", params={"q": "income certificate validity"})
    body = search_response.json()
    assert search_response.status_code == 200
    assert body["success"] is True
    assert body["results"]


def test_search_reindex_requires_admin(client, admin_headers) -> None:
    response = client.post("/api/search/reindex", headers=admin_headers)
    body = response.json()
    assert response.status_code == 200
    assert body["success"] is True
    assert body["indexed_chunks"] > 0


def test_answer_engine_facade_and_bm25_search() -> None:
    answer = answer_question("income certificate validity entha")
    assert answer["method"] == "exact_rule_engine"

    bm25_results = bm25_search.search("income certificate validity", top_k=3)
    hybrid_results = hybrid_retriever.retrieve("income certificate validity", top_k=3)
    assert bm25_results
    assert hybrid_results
