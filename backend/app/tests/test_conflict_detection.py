def test_conflict_scan_detects_two_active_validity_rules(client) -> None:
    response = client.post("/api/conflicts/scan")
    body = response.json()
    assert response.status_code == 200
    assert any(item["conflict_type"] == "active_value_conflict" for item in body["conflicts"])


def test_conflict_resolve_works(client) -> None:
    conflict_id = client.post("/api/conflicts/scan").json()["conflicts"][0]["id"]
    response = client.post(f"/api/conflicts/{conflict_id}/resolve")
    assert response.status_code == 200
    assert response.json()["conflict"]["status"] == "resolved"


def test_conflict_ignore_works(client) -> None:
    conflict_id = client.post("/api/conflicts/scan").json()["conflicts"][0]["id"]
    response = client.post(f"/api/conflicts/{conflict_id}/ignore")
    assert response.status_code == 200
    assert response.json()["conflict"]["status"] == "ignored"


def test_list_conflicts_works(client) -> None:
    client.post("/api/conflicts/scan")
    response = client.get("/api/conflicts")
    assert response.status_code == 200
    assert response.json()["conflicts"]
