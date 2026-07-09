def test_chat_validity_returns_verified_go_138_source(client) -> None:
    response = client.post(
        "/api/chat",
        json={
            "message": "income certificate validity entha",
            "language": "auto",
            "context": {"service_id": "income_certificate"},
        },
    )
    body = response.json()
    assert response.status_code == 200
    assert body["verified"] is True
    assert body["intent"] == "validity"
    assert body["source"]["type"] == "verified_rule"
    assert body["source"]["references"][0]["circular_number"] == "GO-138"
    assert body["language"] == "telugu"


def test_chat_scholarship_documents_returns_source(client) -> None:
    response = client.post("/api/chat", json={"message": "scholarship documents enti"})
    body = response.json()
    assert response.status_code == 200
    assert body["intent"] == "documents"
    assert body["scheme_or_service"] == "post_matric_scholarship"
    assert "Income Certificate" in body["answer"]
    assert body["source"]["references"]


def test_chat_old_age_pension_eligibility_is_safe(client) -> None:
    response = client.post("/api/chat", json={"message": "am I eligible for old age pension"})
    body = response.json()
    assert response.status_code == 200
    assert body["intent"] == "eligibility"
    assert body["scheme_or_service"] == "old_age_pension"
    assert body["verified"] is False
    assert body["source"]["type"] == "rag"
    assert body["source"]["references"][0]["source_type"] == "seed_demo"


def test_chat_unknown_rule_uses_no_hallucination_fallback(client) -> None:
    response = client.post("/api/chat", json={"message": "unknown secret subsidy rule"})
    body = response.json()
    assert response.status_code == 200
    assert body["fallback"] is True
    assert body["verified"] is False
    assert body["source"]["type"] == "none"


def test_chat_hindi_process_answer_tracks_language(client) -> None:
    response = client.post("/api/chat", json={"message": "caste certificate process kya hai"})
    body = response.json()
    assert response.status_code == 200
    assert body["language"] == "hindi"
    assert body["intent"] == "process"
    assert body["scheme_or_service"] == "caste_certificate"
