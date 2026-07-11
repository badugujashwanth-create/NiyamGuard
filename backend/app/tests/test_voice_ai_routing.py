def test_voice_assistant_form_help_stays_local(client, session_id) -> None:
    response = client.post(
        "/api/assistant/ask",
        json={
            "session_id": session_id,
            "form_id": "income_certificate",
            "message": "monthly income fifteen thousand what should I enter",
        },
    )
    body = response.json()
    assert response.status_code == 200
    assert body["field"] == "monthly_income"
    assert body["auto_fill"] is False
    assert "provider" not in body


def test_scheme_document_question_uses_chat_rag_route(client) -> None:
    response = client.post("/api/chat", json={"message": "scholarship documents enti"})
    body = response.json()
    assert response.status_code == 200
    assert body["source"]["type"] == "deterministic_rule_engine"
    assert body["fallback"] is False
    assert body["verified"] is True
