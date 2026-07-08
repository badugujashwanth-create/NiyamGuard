def test_versioned_public_api_alias_works(client) -> None:
    response = client.get(
        "/api/v1/public/rules/latest?service_id=income_certificate&rule_key=validity"
    )
    assert response.status_code == 200
    assert response.json()["source"]["circular_number"] == "GO-138"


def test_versioned_protected_api_alias_still_requires_auth(client) -> None:
    response = client.get("/api/v1/admin/summary")
    assert response.status_code == 401


def test_versioned_protected_api_alias_accepts_token(client, viewer_headers) -> None:
    response = client.get("/api/v1/admin/summary", headers=viewer_headers)
    assert response.status_code == 200
    assert response.json()["summary"]["verified_rules"] >= 1
