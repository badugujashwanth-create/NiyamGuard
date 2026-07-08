def test_reports_summary_works(client) -> None:
    response = client.get("/api/reports/summary")
    assert response.status_code == 200
    assert response.json()["summary"]["verified_rules"] >= 1


def test_compliance_report_works(client) -> None:
    client.post("/api/compliance/run")
    response = client.get("/api/reports/compliance")
    assert response.status_code == 200
    assert response.json()["report"]


def test_conflict_report_works(client) -> None:
    client.post("/api/conflicts/scan")
    response = client.get("/api/reports/conflicts")
    assert response.status_code == 200
    assert response.json()["report"]


def test_csv_export_works(client) -> None:
    client.post("/api/compliance/run")
    response = client.get("/api/reports/export?type=compliance&format=csv")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "verified_rule_id" in response.text


def test_json_export_works(client) -> None:
    response = client.get("/api/reports/export?type=rules&format=json")
    assert response.status_code == 200
    assert response.json()["rows"]
