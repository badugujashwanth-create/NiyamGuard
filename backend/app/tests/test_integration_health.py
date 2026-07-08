def test_integration_health_lists_modules(client) -> None:
    response = client.get("/api/integration/health")
    body = response.json()
    assert response.status_code == 200
    assert body["status"] == "online"
    assert "verified_knowledge_base" in body["features"]
