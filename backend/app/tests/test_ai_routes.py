def test_ai_status_returns_fallback_without_ollama(client) -> None:
    response = client.get("/api/ai/status")
    body = response.json()
    assert response.status_code == 200
    assert body["enabled"] is False
    assert body["provider"] == "ollama"
    assert body["status"] == "fallback"
    assert body["rag_enabled"] is True


def test_ai_finding_impact_summary_fallback_works(client, admin_headers) -> None:
    run_response = client.post("/api/compliance/run", headers=admin_headers)
    finding_id = run_response.json()["findings"][0]["id"]

    response = client.post(f"/api/ai/finding/{finding_id}/impact-summary")
    body = response.json()
    assert response.status_code == 200
    assert body["success"] is True
    assert body["provider"] == "fallback"
    assert body["fallback"] is True
    assert body["source"]["circular"] == "GO-138"
    assert "AI summary is explanatory only" in body["limitations"]


def test_ai_chat_alias_uses_chat_contract(client) -> None:
    response = client.post("/api/ai/chat", json={"message": "scholarship documents enti"})
    body = response.json()
    assert response.status_code == 200
    assert body["source"]["type"] == "deterministic_rule_engine"
    assert body["provider"] == "deterministic"
    assert body["verified"] is True
