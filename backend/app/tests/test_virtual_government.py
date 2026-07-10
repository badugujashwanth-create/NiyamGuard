def test_virtual_government_scenario_catalog(client) -> None:
    response = client.get("/api/virtual-gov/scenarios")
    body = response.json()
    assert response.status_code == 200
    assert body["success"] is True
    assert body["scenarios"][0]["scenario_id"] == "income_certificate_full_flow"


def test_virtual_government_full_flow(client) -> None:
    response = client.post(
        "/api/virtual-gov/run",
        json={"scenario_id": "income_certificate_full_flow", "reset_before_run": True},
    )
    body = response.json()
    assert response.status_code == 200
    assert body["success"] is True
    assert body["artifacts"]["application_number"].startswith("NGSP-")
    assert body["artifacts"]["certificate_number"].startswith("NGCERT-")
    assert body["artifacts"]["tracking"]["status"] == "certificate_issued"
    assert body["steps"][0]["payload"]["method"] == "exact_rule_engine"

    verify = client.get(f"/api/certificates/verify/{body['artifacts']['verification_hash']}")
    assert verify.status_code == 200
    assert verify.json()["valid"] is True

    status = client.get("/api/virtual-gov/status").json()
    assert status["applications"] >= 1
    assert status["certificates"] >= 1
    assert status["audit_events"] >= 1
