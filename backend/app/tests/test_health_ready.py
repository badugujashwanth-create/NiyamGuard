def test_health_endpoint_works(client) -> None:
    response = client.get("/api/health")
    body = response.json()
    assert response.status_code == 200
    assert body["status"] == "ok"
    assert body["app"] == "NiyamGuard AI"


def test_ready_checks_database_and_demo_data(client) -> None:
    response = client.get("/api/ready")
    body = response.json()
    assert response.status_code == 200
    assert body["database"]["reachable"] is True
    assert body["demo_data"]["available"] is True


def test_integration_health_lists_modules(client) -> None:
    response = client.get("/api/integration/health")
    modules = set(response.json()["modules"])
    assert response.status_code == 200
    assert {"knowledge_base", "voice_assistant", "forms", "public_rules"} <= modules
