def _finding_id(client, system_id: str, headers: dict[str, str]) -> str:
    response = client.post("/api/compliance/run", headers=headers)
    assert response.status_code == 200
    return next(
        item["id"]
        for item in response.json()["findings"]
        if item["connected_system_id"] == system_id
    )


def test_portal_finding_creates_portal_cascade(client, reviewer_headers) -> None:
    finding_id = _finding_id(client, "sys_meeseva_portal", reviewer_headers)
    response = client.post(f"/api/cascade/generate/{finding_id}", headers=reviewer_headers)
    trace = response.json()["trace"]
    assert response.status_code == 200
    assert trace["trace_type"] == "portal"
    assert "Portal Not Updated" in [node["label"] for node in trace["nodes_json"]]


def test_faq_finding_creates_faq_cascade(client, reviewer_headers, viewer_headers) -> None:
    finding_id = _finding_id(client, "sys_public_faq", reviewer_headers)
    response = client.get(f"/api/cascade/finding/{finding_id}", headers=viewer_headers)
    trace = response.json()["trace"]
    assert response.status_code == 200
    assert trace["trace_type"] == "faq"
    assert "Public FAQ Not Updated" in [node["label"] for node in trace["nodes_json"]]


def test_sop_finding_creates_sop_cascade(client, reviewer_headers, viewer_headers) -> None:
    finding_id = _finding_id(client, "sys_officer_sop", reviewer_headers)
    response = client.get(f"/api/cascade/finding/{finding_id}", headers=viewer_headers)
    trace = response.json()["trace"]
    assert response.status_code == 200
    assert trace["trace_type"] == "sop"
    assert "SOP Manual Not Updated" in [node["label"] for node in trace["nodes_json"]]


def test_cascade_endpoint_returns_nodes_and_edges(client, reviewer_headers, viewer_headers) -> None:
    finding_id = _finding_id(client, "sys_meeseva_portal", reviewer_headers)
    trace = client.get(f"/api/cascade/finding/{finding_id}", headers=viewer_headers).json()["trace"]
    assert trace["nodes_json"]
    assert trace["edges_json"]
