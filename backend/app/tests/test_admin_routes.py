def test_admin_summary_works(client) -> None:
    client.post("/api/compliance/run")
    response = client.get("/api/admin/summary")
    assert response.status_code == 200
    assert response.json()["summary"]["verified_rules"] >= 1


def test_module_status_lists_all_built_modules(client) -> None:
    response = client.get("/api/admin/module-status")
    modules = {item["name"] for item in response.json()["modules"]}
    assert response.status_code == 200
    assert "central_verified_knowledge_base" in modules
    assert "public_verified_rule_apis" in modules
