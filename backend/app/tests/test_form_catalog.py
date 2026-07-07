from app.services.form_service import load_all_forms


def test_form_catalog_returns_seeded_forms(client) -> None:
    response = client.get("/api/forms")
    body = response.json()
    assert response.status_code == 200
    assert body["success"] is True
    assert len(body["forms"]) >= 25
    ready_forms = {
        item["form_id"]
        for item in body["forms"]
        if item["status"] == "ready" and item["has_detailed_schema"] is True
    }
    assert ready_forms == {
        "income_certificate",
        "residence_certificate",
        "caste_community_certificate",
        "birth_certificate",
        "death_certificate",
        "name_change_request",
        "family_member_certificate",
        "no_earning_member_certificate",
        "no_property_certificate",
        "ews_certificate",
    }
    loan = next(item for item in body["forms"] if item["form_id"] == "loan_eligibility_card")
    assert loan["status"] == "catalog_only"
    assert loan["has_detailed_schema"] is False


def test_each_seeded_form_schema_is_valid() -> None:
    forms = load_all_forms()
    assert len(forms) == 10
    assert {form.form_id for form in forms} == {
        "income_certificate",
        "residence_certificate",
        "caste_community_certificate",
        "birth_certificate",
        "death_certificate",
        "name_change_request",
        "family_member_certificate",
        "no_earning_member_certificate",
        "no_property_certificate",
        "ews_certificate",
    }
    for form in forms:
        assert form.form_id
        assert form.service_name
        assert form.department
        assert form.category
        assert form.description
        assert form.fields
        assert form.required_documents
        for field in form.fields:
            assert field.help["english"]
            assert field.help["telugu"]
            assert field.help["hindi"]
        for document in form.required_documents:
            assert document.accepted_file_types
            assert document.max_size_mb > 0
            assert document.help["english"]
            assert document.help["telugu"]
            assert document.help["hindi"]


def test_get_dynamic_form_by_id(client) -> None:
    response = client.get("/api/forms/birth_certificate")
    body = response.json()
    assert response.status_code == 200
    assert body["form"]["form_id"] == "birth_certificate"
    assert any(field["type"] == "date" for field in body["form"]["fields"])


def test_services_and_search_work(client) -> None:
    all_services = client.get("/api/services")
    assert all_services.status_code == 200
    assert len(all_services.json()["services"]) >= 25

    search = client.get("/api/services/search?q=scholarship")
    assert search.status_code == 200
    assert any(
        item["form_id"] == "income_certificate"
        for item in search.json()["services"]
    )


def test_catalog_only_services_are_marked_coming_soon(client) -> None:
    search = client.get("/api/services/search?q=loan")
    assert search.status_code == 200
    loan = next(
        item
        for item in search.json()["services"]
        if item["form_id"] == "loan_eligibility_card"
    )
    assert loan["status"] == "catalog_only"
    assert loan["has_detailed_schema"] is False
    assert loan["required_document_count"] == 0
