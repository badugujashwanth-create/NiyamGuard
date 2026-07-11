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
    assert "Caste Certificate" in body["answer"]
    assert body["source"]["type"] == "deterministic_rule_engine"
    assert body["verified"] is True
    assert body["source"]["references"]


def test_chat_certificate_documents_use_certificate_baseline(client) -> None:
    response = client.post("/api/chat", json={"message": "residence certificate documents"})
    body = response.json()
    assert response.status_code == 200
    assert body["intent"] == "documents"
    assert body["scheme_or_service"] == "residence_certificate"
    assert body["source"]["type"] == "certificate_baseline"
    assert "Residence Certificate" in body["answer"]
    assert body["verified"] is True


def test_chat_honors_selected_telugu_for_grounded_document_answer(client) -> None:
    response = client.post(
        "/api/chat",
        json={
            "message": "what documents are needed for residence certificate",
            "language": "telugu",
            "context": {"service_id": "residence_certificate"},
        },
    )
    body = response.json()
    assert response.status_code == 200
    assert body["language"] == "telugu"
    assert body["language_code"] == "te-IN"
    assert "అవసరమైన పత్రాలు" in body["answer"]
    assert body["source"]["type"] == "certificate_baseline"


def test_chat_old_age_pension_eligibility_is_safe(client) -> None:
    response = client.post("/api/chat", json={"message": "am I eligible for old age pension age 62 income 120000"})
    body = response.json()
    assert response.status_code == 200
    assert body["intent"] == "eligibility"
    assert body["scheme_or_service"] == "old_age_pension"
    assert body["verified"] is True
    assert body["source"]["type"] == "deterministic_rule_engine"
    assert "Eligible based on the provided profile" in body["answer"]


def test_chat_old_age_pension_eligibility_explains_failed_rule(client) -> None:
    response = client.post("/api/chat", json={"message": "am I eligible for old age pension age 55 income 120000"})
    body = response.json()
    assert response.status_code == 200
    assert body["intent"] == "eligibility"
    assert body["scheme_or_service"] == "old_age_pension"
    assert body["verified"] is True
    assert "short by 5" in body["answer"]


def test_chat_income_old_vs_new_includes_photo_requirement(client) -> None:
    response = client.post("/api/chat", json={"message": "income certificate what changed"})
    body = response.json()
    assert response.status_code == 200
    assert body["intent"] == "old_vs_new"
    assert body["scheme_or_service"] == "income_certificate"
    assert body["source"]["type"] == "deterministic_rule_engine"
    assert "GO-112" in body["answer"]
    assert "GO-138" in body["answer"]
    assert "Passport-size photograph" in body["answer"]


def test_chat_compares_scholarship_and_pension_deterministically(client) -> None:
    response = client.post("/api/chat", json={"message": "compare post matric scholarship vs old age pension"})
    body = response.json()
    assert response.status_code == 200
    assert body["intent"] == "scheme_comparison"
    assert body["source"]["type"] == "deterministic_rule_engine"
    assert "Post-Matric Scholarship" in body["answer"]
    assert "Old-Age Pension" in body["answer"]
    assert "250000" in body["answer"]


def test_chat_unknown_rule_uses_no_hallucination_fallback(client) -> None:
    response = client.post("/api/chat", json={"message": "unknown secret subsidy rule"})
    body = response.json()
    assert response.status_code == 200
    assert body["fallback"] is True
    assert body["verified"] is False
    assert body["source"]["type"] == "none"


def test_chat_out_of_scope_question_is_not_replaced_by_page_service(client) -> None:
    response = client.post(
        "/api/chat",
        json={
            "message": "quantum physics enti",
            "language": "telugu",
            "context": {"service_id": "income_certificate"},
        },
    )
    body = response.json()
    assert response.status_code == 200
    assert body["fallback"] is True
    assert body["verified"] is False
    assert body["source"]["type"] == "none"
    assert "Income Certificate" not in body["answer"]
    assert "ధృవీకరించిన సమాచారం" in body["answer"]


def test_chat_hindi_process_answer_tracks_language(client) -> None:
    response = client.post("/api/chat", json={"message": "caste certificate process kya hai"})
    body = response.json()
    assert response.status_code == 200
    assert body["language"] == "hindi"
    assert body["intent"] == "process"
    assert body["scheme_or_service"] == "caste_certificate"
