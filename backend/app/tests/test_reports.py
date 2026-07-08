def test_reports_summary_works(client, viewer_headers) -> None:
    response = client.get("/api/reports/summary", headers=viewer_headers)
    assert response.status_code == 200
    assert response.json()["summary"]["verified_rules"] >= 1


def test_compliance_report_works(client, reviewer_headers, viewer_headers) -> None:
    client.post("/api/compliance/run", headers=reviewer_headers)
    response = client.get("/api/reports/compliance", headers=viewer_headers)
    assert response.status_code == 200
    assert response.json()["report"]


def test_conflict_report_works(client, reviewer_headers, viewer_headers) -> None:
    client.post("/api/conflicts/scan", headers=reviewer_headers)
    response = client.get("/api/reports/conflicts", headers=viewer_headers)
    assert response.status_code == 200
    assert response.json()["report"]


def test_csv_export_works(client, reviewer_headers) -> None:
    client.post("/api/compliance/run", headers=reviewer_headers)
    response = client.get("/api/reports/export?type=compliance&format=csv", headers=reviewer_headers)
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "verified_rule_id" in response.text


def test_json_export_works(client, reviewer_headers) -> None:
    response = client.get("/api/reports/export?type=rules&format=json", headers=reviewer_headers)
    assert response.status_code == 200
    assert response.json()["rows"]
