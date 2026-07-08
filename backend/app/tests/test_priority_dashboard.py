def test_portal_validity_drift_becomes_high_or_critical(client, reviewer_headers) -> None:
    client.post("/api/compliance/run", headers=reviewer_headers)
    response = client.post("/api/dashboard/recalculate-priority", headers=reviewer_headers)
    scores = response.json()["priority_findings"]
    portal_score = next(
        item for item in scores if item["finding_id"] == "find_rule_001_sys_meeseva_portal"
    )
    assert portal_score["priority_level"] in {"high", "critical"}
    assert portal_score["reason"]


def test_dashboard_summary_counts_findings(client, reviewer_headers) -> None:
    client.post("/api/compliance/run", headers=reviewer_headers)
    client.post("/api/dashboard/recalculate-priority", headers=reviewer_headers)
    response = client.get("/api/dashboard/summary")
    summary = response.json()["summary"]
    assert response.status_code == 200
    assert summary["compliance_findings"] >= 4
    assert summary["drifted_findings"] >= 3


def test_high_impact_endpoint_returns_high_findings(client, reviewer_headers, viewer_headers) -> None:
    client.post("/api/compliance/run", headers=reviewer_headers)
    client.post("/api/dashboard/recalculate-priority", headers=reviewer_headers)
    response = client.get("/api/dashboard/high-impact", headers=viewer_headers)
    assert response.status_code == 200
    assert response.json()["priority_findings"]
