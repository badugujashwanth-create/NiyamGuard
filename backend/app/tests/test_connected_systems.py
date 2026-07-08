def test_connected_systems_list_works(client, viewer_headers) -> None:
    response = client.get("/api/connected-systems", headers=viewer_headers)
    body = response.json()
    assert response.status_code == 200
    names = {item["name"] for item in body["systems"]}
    assert "MeeSeva Income Certificate Portal" in names
    assert "Officer SOP Manual" in names
    assert "Public FAQ" in names


def test_snapshot_creation_works(client, reviewer_headers) -> None:
    response = client.post(
        "/api/connected-systems/sys_meeseva_portal/snapshots",
        headers=reviewer_headers,
        json={
            "service_id": "income_certificate",
            "rule_key": "validity",
            "displayed_value": "6",
            "unit": "months",
            "source_location": "test update",
            "snapshot_source": "demo",
        },
    )
    body = response.json()
    assert response.status_code == 200
    assert body["snapshot"]["displayed_value"] == "6"


def test_seeded_systems_exist(client, viewer_headers) -> None:
    response = client.get("/api/connected-systems/sys_simplified_form", headers=viewer_headers)
    assert response.status_code == 200
    assert response.json()["system"]["name"] == "Simplified Citizen Form"
