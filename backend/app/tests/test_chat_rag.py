def test_chat_scholarship_documents_uses_rag_with_sources(client) -> None:
    response = client.post("/api/chat", json={"message": "scholarship documents enti"})
    body = response.json()
    assert response.status_code == 200
    assert body["source"]["type"] == "deterministic_rule_engine"
    assert body["scheme_or_service"] == "post_matric_scholarship"
    assert body["verified"] is True
    assert body["provider"] == "deterministic"
    assert "Caste Certificate" in body["answer"]


def test_chat_validity_still_uses_verified_rule_first(client) -> None:
    response = client.post("/api/chat", json={"message": "income certificate validity entha"})
    body = response.json()
    assert response.status_code == 200
    assert body["source"]["type"] == "verified_rule"
    assert body["verified"] is True
    assert body["provider"] == "deterministic"


def test_unknown_question_returns_required_safe_fallback(client) -> None:
    response = client.post("/api/chat", json={"message": "unknown secret subsidy rule"})
    body = response.json()
    assert response.status_code == 200
    assert body["fallback"] is True
    assert body["answer"] == "Verified data is not available for this question."
