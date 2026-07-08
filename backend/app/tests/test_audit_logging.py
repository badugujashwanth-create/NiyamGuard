def test_compliance_run_creates_audit_event(client, reviewer_headers, viewer_headers) -> None:
    client.post("/api/compliance/run", headers=reviewer_headers)
    response = client.get("/api/audit/events", headers=viewer_headers)
    actions = {event["action"] for event in response.json()["events"]}
    assert response.status_code == 200
    assert "compliance_run" in actions or "compliance_run_completed" in actions


def test_conflict_resolve_creates_audit_event(client, reviewer_headers, viewer_headers) -> None:
    conflict_id = client.post("/api/conflicts/scan", headers=reviewer_headers).json()["conflicts"][0]["id"]
    client.post(f"/api/conflicts/{conflict_id}/resolve", headers=reviewer_headers)
    response = client.get("/api/audit/events", headers=viewer_headers)
    actions = {event["action"] for event in response.json()["events"]}
    assert "conflict_resolved_by_user" in actions or "conflict_resolved" in actions


def test_report_export_creates_audit_event(client, reviewer_headers, viewer_headers) -> None:
    client.get("/api/reports/export?type=rules&format=json", headers=reviewer_headers)
    response = client.get("/api/audit/events", headers=viewer_headers)
    actions = {event["action"] for event in response.json()["events"]}
    assert "report_exported" in actions


def test_audit_hash_chain_verifies(client, reviewer_headers, viewer_headers) -> None:
    client.post("/api/compliance/run", headers=reviewer_headers)
    response = client.get("/api/audit/verify", headers=viewer_headers)
    body = response.json()
    assert response.status_code == 200
    assert body["chain_intact"] is True
    assert body["checked_events"] >= 1
