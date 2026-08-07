def test_ops_status_requires_authenticated_viewer(client, viewer_headers) -> None:
    response = client.get("/api/ops/status", headers=viewer_headers)
    body = response.json()
    assert response.status_code == 200
    assert body["success"] is True
    assert body["database"]["reachable"] is True
    assert "ai" in body


def test_admin_readiness_report(client, admin_headers) -> None:
    client.post("/api/dataset/import", headers=admin_headers)
    response = client.get("/api/admin/readiness", headers=admin_headers)
    body = response.json()
    assert response.status_code == 200
    assert body["success"] is True
    assert body["pilot_status"] == "ready"
    assert body["ready_controls"] == body["total_controls"]


def test_sandbox_otp_flow(client) -> None:
    request_response = client.post(
        "/api/security/otp/request",
        json={"channel": "sms", "destination": "9876543210"},
    )
    request_body = request_response.json()
    assert request_response.status_code == 200
    assert request_body["demo_code"] == "123456"

    verify_response = client.post(
        "/api/security/otp/verify",
        json={"otp_id": request_body["otp_id"], "code": "123456"},
    )
    assert verify_response.status_code == 200
    assert verify_response.json()["verified"] is True
