from app.knowledge_base.platform_store import read_store


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
    assert summary["compliant_findings"] == 1
    assert summary["compliance_score"] == 25.0


def test_department_readiness_aggregates_real_findings(client, reviewer_headers, viewer_headers) -> None:
    client.post("/api/compliance/run", headers=reviewer_headers)
    client.post("/api/dashboard/recalculate-priority", headers=reviewer_headers)

    response = client.get("/api/dashboard/departments", headers=viewer_headers)

    assert response.status_code == 200
    departments = response.json()["departments"]
    revenue = next(item for item in departments if item["department"] == "Revenue")
    assert revenue["total_systems"] >= 1
    assert revenue["checked_systems"] >= 1
    assert revenue["compliance_score"] is not None
    assert revenue["readiness_status"] in {"ready", "attention", "at_risk"}


def test_dashboard_metrics_exclude_inactive_connected_systems(client, reviewer_headers) -> None:
    client.post("/api/compliance/run", headers=reviewer_headers)
    store = read_store()
    system_with_finding = next(
        system
        for system in store.connected_systems
        if any(finding.connected_system_id == system.id for finding in store.compliance_findings)
    )
    original_status = system_with_finding.status
    try:
        system_with_finding.status = "inactive"
        summary = client.get("/api/dashboard/summary", headers=reviewer_headers).json()["summary"]

        assert summary["checked_systems"] <= len(
            [system for system in store.connected_systems if system.status == "active"]
        )
        assert summary["coverage_score"] is None or summary["coverage_score"] <= 100
    finally:
        system_with_finding.status = original_status


def test_high_impact_endpoint_returns_high_findings(client, reviewer_headers, viewer_headers) -> None:
    client.post("/api/compliance/run", headers=reviewer_headers)
    client.post("/api/dashboard/recalculate-priority", headers=reviewer_headers)
    response = client.get("/api/dashboard/high-impact", headers=viewer_headers)
    assert response.status_code == 200
    assert response.json()["priority_findings"]
