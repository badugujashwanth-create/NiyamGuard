def _finding_id(client, system_id: str) -> str:
    response = client.post("/api/compliance/run")
    assert response.status_code == 200
    return next(
        item["id"]
        for item in response.json()["findings"]
        if item["connected_system_id"] == system_id
    )


def test_portal_finding_creates_portal_cascade(client) -> None:
    finding_id = _finding_id(client, "sys_meeseva_portal")
    response = client.post(f"/api/cascade/generate/{finding_id}")
    trace = response.json()["trace"]
    assert response.status_code == 200
    assert trace["trace_type"] == "portal"
    assert "Portal Not Updated" in [node["label"] for node in trace["nodes_json"]]


def test_faq_finding_creates_faq_cascade(client) -> None:
    finding_id = _finding_id(client, "sys_public_faq")
    response = client.get(f"/api/cascade/finding/{finding_id}")
    trace = response.json()["trace"]
    assert response.status_code == 200
    assert trace["trace_type"] == "faq"
    assert "Public FAQ Not Updated" in [node["label"] for node in trace["nodes_json"]]


def test_sop_finding_creates_sop_cascade(client) -> None:
    finding_id = _finding_id(client, "sys_officer_sop")
    response = client.get(f"/api/cascade/finding/{finding_id}")
    trace = response.json()["trace"]
    assert response.status_code == 200
    assert trace["trace_type"] == "sop"
    assert "SOP Manual Not Updated" in [node["label"] for node in trace["nodes_json"]]


def test_cascade_endpoint_returns_nodes_and_edges(client) -> None:
    finding_id = _finding_id(client, "sys_meeseva_portal")
    trace = client.get(f"/api/cascade/finding/{finding_id}").json()["trace"]
    assert trace["nodes_json"]
    assert trace["edges_json"]
