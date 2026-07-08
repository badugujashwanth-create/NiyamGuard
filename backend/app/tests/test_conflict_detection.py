def test_conflict_scan_detects_two_active_validity_rules(client, reviewer_headers) -> None:
    response = client.post("/api/conflicts/scan", headers=reviewer_headers)
    body = response.json()
    assert response.status_code == 200
    assert any(item["conflict_type"] == "active_value_conflict" for item in body["conflicts"])


def test_conflict_resolve_works(client, reviewer_headers) -> None:
    conflict_id = client.post("/api/conflicts/scan", headers=reviewer_headers).json()["conflicts"][0]["id"]
    response = client.post(f"/api/conflicts/{conflict_id}/resolve", headers=reviewer_headers)
    assert response.status_code == 200
    assert response.json()["conflict"]["status"] == "resolved"


def test_conflict_ignore_works(client, reviewer_headers) -> None:
    conflict_id = client.post("/api/conflicts/scan", headers=reviewer_headers).json()["conflicts"][0]["id"]
    response = client.post(f"/api/conflicts/{conflict_id}/ignore", headers=reviewer_headers)
    assert response.status_code == 200
    assert response.json()["conflict"]["status"] == "ignored"


def test_list_conflicts_works(client, reviewer_headers, viewer_headers) -> None:
    client.post("/api/conflicts/scan", headers=reviewer_headers)
    response = client.get("/api/conflicts", headers=viewer_headers)
    assert response.status_code == 200
    assert response.json()["conflicts"]
