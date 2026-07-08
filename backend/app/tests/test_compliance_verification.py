def _run(client, headers):
    response = client.post("/api/compliance/run", headers=headers)
    assert response.status_code == 200
    return response.json()["findings"]


def test_compliance_run_detects_portal_drift(client, reviewer_headers) -> None:
    findings = _run(client, reviewer_headers)
    portal = next(item for item in findings if item["connected_system_id"] == "sys_meeseva_portal")
    assert portal["status"] == "drifted"
    assert portal["expected_value"] == "6 months"
    assert portal["actual_value"] == "12 months"


def test_compliance_run_detects_sop_drift(client, reviewer_headers) -> None:
    findings = _run(client, reviewer_headers)
    sop = next(item for item in findings if item["connected_system_id"] == "sys_officer_sop")
    assert sop["status"] == "drifted"


def test_compliance_run_detects_faq_drift(client, reviewer_headers) -> None:
    findings = _run(client, reviewer_headers)
    faq = next(item for item in findings if item["connected_system_id"] == "sys_public_faq")
    assert faq["status"] == "drifted"


def test_simplified_citizen_form_is_compliant(client, reviewer_headers) -> None:
    findings = _run(client, reviewer_headers)
    form = next(item for item in findings if item["connected_system_id"] == "sys_simplified_form")
    assert form["status"] == "compliant"


def test_findings_endpoint_and_mark_fixed_work(client, reviewer_headers, viewer_headers) -> None:
    _run(client, reviewer_headers)
    listing = client.get("/api/compliance/findings", headers=viewer_headers)
    assert listing.status_code == 200
    finding_id = next(
        item["id"]
        for item in listing.json()["findings"]
        if item["connected_system_id"] == "sys_meeseva_portal"
    )
    fixed = client.post(f"/api/compliance/findings/{finding_id}/mark-fixed", headers=reviewer_headers)
    assert fixed.status_code == 200
    assert fixed.json()["finding"]["status"] == "compliant"
