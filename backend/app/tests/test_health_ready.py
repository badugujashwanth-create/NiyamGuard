def test_health_endpoint_works(client) -> None:
    response = client.get("/api/health")
    body = response.json()
    assert response.status_code == 200
    assert body["status"] == "ok"
    assert body["app"] == "NiyamGuard"


def test_ready_checks_database_and_demo_data(client) -> None:
    response = client.get("/api/ready")
    body = response.json()
    assert response.status_code == 200
    assert body["database"]["reachable"] is True
    assert body["demo_data"]["available"] is True
    assert body["core_tables"]["missing"] == []
    assert {"object_storage", "malware_scanner", "ocr", "configuration"} <= body.keys()


def test_ready_marks_hardened_configuration_degraded_when_dependencies_are_missing(client, monkeypatch) -> None:
    from app.api import health_routes

    monkeypatch.setattr(health_routes.settings, "app_env", "production")
    monkeypatch.setattr(health_routes.settings, "object_storage_backend", "local")
    monkeypatch.setattr(health_routes.settings, "malware_scan_mode", "disabled")
    monkeypatch.setattr(health_routes.settings, "ocr_enabled", False)

    response = client.get("/api/ready")
    body = response.json()

    assert response.status_code == 200
    assert body["status"] == "degraded"
    assert body["configuration"]["ready"] is False
    assert body["malware_scanner"]["required"] is True
    assert body["ocr"]["required"] is True


def test_integration_health_lists_modules(client) -> None:
    response = client.get("/api/integration/health")
    modules = set(response.json()["modules"])
    assert response.status_code == 200
    assert {"knowledge_base", "voice_assistant", "forms", "public_rules"} <= modules
