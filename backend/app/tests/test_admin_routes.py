def test_admin_summary_works(client, reviewer_headers, viewer_headers) -> None:
    client.post("/api/compliance/run", headers=reviewer_headers)
    response = client.get("/api/admin/summary", headers=viewer_headers)
    assert response.status_code == 200
    assert response.json()["summary"]["verified_rules"] >= 1


def test_module_status_lists_all_built_modules(client, viewer_headers) -> None:
    response = client.get("/api/admin/module-status", headers=viewer_headers)
    modules = {item["name"] for item in response.json()["modules"]}
    assert response.status_code == 200
    assert "central_verified_knowledge_base" in modules
    assert "public_verified_rule_apis" in modules
