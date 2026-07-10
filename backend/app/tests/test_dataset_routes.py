def test_dataset_status_and_import(client) -> None:
    response = client.post("/api/dataset/import")
    assert response.status_code == 200
    assert response.json()["result"]["total_records"] == 18531

    status = client.get("/api/dataset/status").json()
    assert status["success"] is True
    assert status["loaded_records"] == 18531
    assert status["collections"]["policy_qa_pairs"] == 900


def test_regulatory_qa_uses_dataset_grounding(client) -> None:
    response = client.post("/api/dataset/qa", json={"question": "Why is ORG-0029 high risk?"})
    body = response.json()
    assert response.status_code == 200
    assert body["success"] is True
    assert body["provider"] == "dataset"
    assert body["references"]
    assert body["references"][0]["source"]["type"] == "policy_qa_pair"


def test_obligation_search_returns_dataset_records(client) -> None:
    response = client.get("/api/dataset/obligations/search?q=privacy&limit=2")
    body = response.json()
    assert response.status_code == 200
    assert body["count"] >= 1
    assert body["records"][0]["collection"] == "obligations"


def test_gap_detection_returns_gaps_and_mappings(client) -> None:
    response = client.get("/api/dataset/gaps?org_id=ORG-0029&limit=3")
    body = response.json()
    assert response.status_code == 200
    assert body["success"] is True
    assert body["gaps"] or body["mappings"]


def test_evidence_review_returns_evidence(client) -> None:
    response = client.get("/api/dataset/evidence?org_id=ORG-0029&limit=2")
    body = response.json()
    assert response.status_code == 200
    assert body["success"] is True
    assert body["evidence"]


def test_drift_detection_returns_cases(client) -> None:
    response = client.get("/api/dataset/drift?org_id=ORG-0029&limit=2")
    body = response.json()
    assert response.status_code == 200
    assert body["success"] is True
    assert "drift_cases" in body


def test_risk_scoring_explanation(client) -> None:
    response = client.get("/api/dataset/risk/ORG-0029")
    body = response.json()
    assert response.status_code == 200
    assert body["success"] is True
    assert "ORG-0029 has risk band" in body["explanation"]


def test_audit_lookup_returns_events(client) -> None:
    response = client.get("/api/dataset/audit?org_id=ORG-0029&limit=2")
    body = response.json()
    assert response.status_code == 200
    assert body["success"] is True
    assert body["events"]


def test_dataset_demo_flow_is_end_to_end(client) -> None:
    response = client.get("/api/dataset/demo-flow?org_id=ORG-0029")
    body = response.json()
    assert response.status_code == 200
    assert body["success"] is True
    assert body["regulation"]
    assert body["obligation"]
    assert body["internal_policy"]
    assert body["gap"] or body["drift"]
    assert body["risk"]
    assert body["evidence"]
    assert body["audit_trail"]
