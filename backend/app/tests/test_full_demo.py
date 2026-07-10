def test_full_end_to_end_demo_endpoint_creates_real_entities(client) -> None:
    response = client.post("/api/demo/run-full-end-to-end")
    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert len(body["steps"]) == 18
    assert all(step["status"] == "success" for step in body["steps"])
    assert body["entities"]["application_number"].startswith("NGSP-")
    assert body["entities"]["certificate_number"].startswith("NGCERT-")
    assert body["entities"]["verification_hash"]
    assert body["entities"]["rule_id"] == "rule_001"
    assert body["circular_number"] == "GO-138"
    assert body["application_number"] == body["entities"]["application_number"]
    assert body["certificate_number"] == body["entities"]["certificate_number"]
    assert body["verification_hash"] == body["entities"]["verification_hash"]
    assert body["verified_rule"]["rule_key"] == "validity"
    assert body["audit_event_count"] >= 1

    verify = client.get(f"/api/certificates/verify/{body['entities']['verification_hash']}")
    assert verify.status_code == 200
    assert verify.json()["valid"] is True


def test_verified_ai_explanation_uses_safe_fallback_when_ollama_is_off(client) -> None:
    response = client.post(
        "/api/ai/verified-explanation",
        json={"question": "Explain GO-138 in simple words"},
    )
    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert body["source"]["circular_number"] == "GO-138"
    assert body["fallback"] is True
    assert "6 months" in body["answer"]
