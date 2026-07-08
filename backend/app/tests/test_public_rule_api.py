def test_public_latest_rule_returns_citizen_safe_source(client) -> None:
    response = client.get(
        "/api/public/rules/latest?service_id=income_certificate&rule_key=validity"
    )
    body = response.json()
    assert response.status_code == 200
    assert body["success"] is True
    assert body["verified"] is True
    assert "6 months" in body["answer"]
    assert body["source"]["circular_number"] == "GO-138"


def test_public_search_works(client) -> None:
    response = client.get("/api/public/search?q=income certificate validity")
    assert response.status_code == 200
    assert response.json()["verified"] is True


def test_missing_public_rule_is_safe(client) -> None:
    response = client.get("/api/public/rules/latest?service_id=missing&rule_key=missing")
    body = response.json()
    assert response.status_code == 200
    assert body["success"] is False
    assert body["verified"] is False
    assert body["source"] is None
