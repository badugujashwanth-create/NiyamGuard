from app.knowledge_base.knowledge_base_service import latest_rule, supersede_older_rules


def test_seed_verified_rule_exists() -> None:
    result = latest_rule("income_certificate", "validity")
    assert result.success is True
    assert result.verified is True
    assert result.current_value == "6"
    assert result.unit == "months"
    assert result.source.circular_number == "GO-138"


def test_latest_rule_endpoint_returns_active_rule(client) -> None:
    response = client.get(
        "/api/knowledge/rules/latest?service_id=income_certificate&rule_key=validity"
    )
    body = response.json()
    assert response.status_code == 200
    assert body["success"] is True
    assert body["current_value"] == "6"
    assert body["previous_value"] == "12"


def test_search_finds_income_certificate_validity(client) -> None:
    response = client.get("/api/knowledge/search?q=income certificate validity")
    body = response.json()
    assert response.status_code == 200
    assert any(rule["rule_key"] == "validity" for rule in body["rules"])


def test_missing_rule_returns_safe_not_found(client) -> None:
    response = client.get("/api/knowledge/rules/latest?service_id=missing&rule_key=validity")
    body = response.json()
    assert response.status_code == 200
    assert body["success"] is False
    assert body["verified"] is False
    assert body["answer"] == "Verified rule not found."


def test_certificate_baseline_uses_form_catalog_and_verified_rule(client) -> None:
    response = client.get("/api/knowledge/certificates/income_certificate")
    body = response.json()
    assert response.status_code == 200
    certificate = body["certificate"]
    assert certificate["service_id"] == "income_certificate"
    assert certificate["title"] == "Income Certificate"
    assert certificate["required_documents"]
    assert certificate["validity"]["verified"] is True
    assert certificate["validity"]["source"]["circular_number"] == "GO-138"
    assert certificate["how_to_verify"]["route"] == "/verify-certificate"


def test_superseding_older_rule_marks_old_rule_superseded() -> None:
    updated = supersede_older_rules("rule_001")
    assert updated is not None
    assert updated.supersedes_rule_id == "rule_conflict_001"
