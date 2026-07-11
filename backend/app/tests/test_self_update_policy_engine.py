def _extract_candidate(client, headers) -> str:
    sync = client.post("/api/sources/src_revenue_demo/sync", headers=headers)
    assert sync.status_code == 200
    extraction = client.post("/api/circulars/cirdoc_go_138/extract-rules", headers=headers)
    assert extraction.status_code == 200
    return extraction.json()["candidates"][0]["id"]


def _publish_candidate(client, headers) -> dict:
    candidate_id = _extract_candidate(client, headers)
    approval = client.post(f"/api/rule-candidates/{candidate_id}/approve", json={"notes": "approved"}, headers=headers)
    assert approval.status_code == 200
    publish = client.post(f"/api/policy-updates/{candidate_id}/publish", json={"notes": "publish"}, headers=headers)
    assert publish.status_code == 200
    return publish.json()


def test_source_registry_lists_demo_source(client, viewer_headers) -> None:
    response = client.get("/api/sources", headers=viewer_headers)
    assert response.status_code == 200
    sources = response.json()["sources"]
    assert sources[0]["id"] == "src_revenue_demo"
    assert sources[0]["source_type"] == "local_demo"


def test_circular_sync_ingests_demo_document_idempotently(client, reviewer_headers) -> None:
    first = client.post("/api/sources/src_revenue_demo/sync", headers=reviewer_headers)
    second = client.post("/api/sources/src_revenue_demo/sync", headers=reviewer_headers)

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["job"]["new_documents_found"] == 1
    assert second.json()["job"]["new_documents_found"] == 0
    circulars = client.get("/api/circulars", headers=reviewer_headers).json()["circulars"]
    assert [item["id"] for item in circulars] == ["cirdoc_go_138"]


def test_rule_extraction_creates_candidate_and_delta(client, reviewer_headers) -> None:
    candidate_id = _extract_candidate(client, reviewer_headers)
    response = client.get("/api/rule-candidates", headers=reviewer_headers)

    assert response.status_code == 200
    candidate = response.json()["candidates"][0]
    assert candidate["id"] == candidate_id
    assert candidate["service_id"] == "income_certificate"
    assert candidate["new_value"] == "6"
    assert candidate["delta"]["change_type"] == "no_change"
    assert candidate["delta"]["impact_level"] == "high"


def test_publication_updates_policy_knowledge_propagation_and_compliance(client, reviewer_headers) -> None:
    result = _publish_candidate(client, reviewer_headers)

    assert result["success"] is True
    assert result["rule_version"]["version_number"] == 3
    assert result["knowledge_update"]["status"] == "completed"
    assert len(result["propagation_plan"]["task_ids"]) == 4
    assert result["compliance_run"]["trigger_type"] == "policy_update"

    history = client.get("/api/policy-updates/history", headers=reviewer_headers)
    versions = client.get("/api/policy-updates/rules/rule_001/versions", headers=reviewer_headers)
    assert history.status_code == 200
    assert versions.status_code == 200
    assert len(versions.json()["versions"]) == 3


def test_knowledge_reindex_records_current_rule_versions(client, reviewer_headers) -> None:
    response = client.post("/api/knowledge/reindex", headers=reviewer_headers)

    assert response.status_code == 200
    assert response.json()["events"][0]["rule_version_id"] == "version_rule_001_2"
    events = client.get("/api/knowledge/update-events", headers=reviewer_headers)
    assert events.status_code == 200
    assert events.json()["events"][0]["status"] == "completed"


def test_propagation_demo_patch_updates_snapshot_and_mock_system(client, reviewer_headers) -> None:
    _publish_candidate(client, reviewer_headers)
    tasks = client.get("/api/propagation/tasks", headers=reviewer_headers).json()["tasks"]
    meeseva_task = next(item for item in tasks if item["connected_system_id"] == "sys_meeseva_portal")

    patch = client.post(f"/api/propagation/tasks/{meeseva_task['id']}/apply-demo-patch", headers=reviewer_headers)
    assert patch.status_code == 200
    assert patch.json()["task"]["status"] == "auto_patched"

    mock = client.get("/api/mock-systems/meeseva", headers=reviewer_headers).json()["system"]
    assert mock["displayed_value"] == "6 months"
    assert mock["sync_status"] == "updated"


def test_compliance_rerun_for_rule_records_run(client, reviewer_headers) -> None:
    response = client.post("/api/compliance/rerun-for-rule/rule_001", headers=reviewer_headers)
    assert response.status_code == 200
    assert response.json()["run"]["affected_rule_id"] == "rule_001"

    runs = client.get("/api/compliance/runs", headers=reviewer_headers)
    assert runs.status_code == 200
    assert runs.json()["runs"][0]["finding_count"] >= 4


def test_scheduler_status_and_run_now(client, reviewer_headers) -> None:
    status = client.get("/api/scheduler/status", headers=reviewer_headers)
    run = client.post("/api/scheduler/run-now", headers=reviewer_headers)

    assert status.status_code == 200
    assert "interval_minutes" in status.json()["scheduler"]
    assert run.status_code == 200
    assert run.json()["results"][0]["success"] is True


def test_self_update_demo_flow_can_patch_mock_systems(client, reviewer_headers) -> None:
    response = client.post(
        "/api/demo/run-self-update-scenario",
        json={"apply_demo_patch": True, "reset_mock_systems": True},
        headers=reviewer_headers,
    )

    assert response.status_code == 200
    steps = response.json()["steps"]
    assert steps["publication"]["success"] is True
    assert steps["patches"]
    assert steps["mock_systems"]["meeseva"]["sync_status"] == "updated"
    assert steps["mock_systems"]["public_faq"]["faq_value"] == "6 months"


def test_mock_systems_reset_and_patch_endpoints(client, reviewer_headers) -> None:
    patched = client.post("/api/mock-systems/apply-demo-patch", headers=reviewer_headers)
    reset = client.post("/api/mock-systems/reset-demo", headers=reviewer_headers)

    assert patched.status_code == 200
    assert patched.json()["systems"]["meeseva"]["displayed_value"] == "6 months"
    assert reset.status_code == 200
    assert reset.json()["systems"]["meeseva"]["displayed_value"] == "12 months"
