def test_compliance_report_filters_work(client, reviewer_headers, viewer_headers) -> None:
    client.post("/api/compliance/run", headers=reviewer_headers)
    response = client.get(
        "/api/reports/compliance?service_id=income_certificate&severity=high&status=drifted",
        headers=viewer_headers,
    )
    rows = response.json()["report"]
    assert response.status_code == 200
    assert rows
    assert all(row["service_id"] == "income_certificate" for row in rows)
    assert all(row["severity"] == "high" for row in rows)
    assert all(row["status"] == "drifted" for row in rows)


def test_report_export_includes_metadata(client, reviewer_headers) -> None:
    response = client.get("/api/reports/export?type=rules&format=json", headers=reviewer_headers)
    body = response.json()
    assert response.status_code == 200
    assert body["metadata"]["report_type"] == "rules"
    assert body["metadata"]["generated_by"] == "reviewer@niyamguard.local"
    assert body["metadata"]["total_records"] >= 1


def test_printable_html_export_works(client, reviewer_headers) -> None:
    response = client.get("/api/reports/export?type=compliance&format=html", headers=reviewer_headers)
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Compliance Report" in response.text
