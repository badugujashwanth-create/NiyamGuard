def test_validation_error_has_clean_shape_and_request_id(client) -> None:
    response = client.post("/api/auth/login", json={"email": "bad", "password": "short"})
    body = response.json()
    assert response.status_code == 422
    assert response.headers["x-request-id"]
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert body["error"]["request_id"]


def test_security_headers_are_present(client) -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"
