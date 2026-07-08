def test_unauthenticated_admin_access_is_blocked(client) -> None:
    response = client.get("/api/admin/summary")
    assert response.status_code == 401


def test_viewer_cannot_create_users(client, viewer_headers) -> None:
    response = client.post(
        "/api/auth/users",
        headers=viewer_headers,
        json={
            "email": "newuser@niyamguard.test",
            "password": "NewUser@12345",
            "role": "viewer",
        },
    )
    assert response.status_code == 403


def test_reviewer_can_run_compliance(client, reviewer_headers) -> None:
    response = client.post("/api/compliance/run", headers=reviewer_headers)
    assert response.status_code == 200
    assert response.json()["findings"]


def test_public_rule_api_stays_open(client) -> None:
    response = client.get(
        "/api/public/rules/latest?service_id=income_certificate&rule_key=validity"
    )
    assert response.status_code == 200
    assert response.json()["source"]["circular_number"] == "GO-138"


def test_viewer_cannot_export_reports(client, viewer_headers) -> None:
    response = client.get(
        "/api/reports/export?type=rules&format=json",
        headers=viewer_headers,
    )
    assert response.status_code == 403
