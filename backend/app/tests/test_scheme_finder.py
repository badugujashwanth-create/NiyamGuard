def test_scheme_finder_recommends_income_certificate_for_student_scholarship(client) -> None:
    response = client.post(
        "/api/scheme-finder/recommend",
        json={
            "age": 19,
            "income": 180000,
            "category": "BC",
            "student": True,
            "occupation": "student",
            "district": "Hyderabad",
            "purpose": "scholarship",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["recommendations"][0]["form_id"] == "income_certificate"
    assert body["recommendations"][0]["safe_note"].startswith("You may be eligible")
    assert body["recommendations"][0]["source"]["type"] == "local_demo_rules"


def test_scheme_finder_recommends_widow_and_disability_services(client) -> None:
    response = client.post(
        "/api/scheme-finder/recommend",
        json={"age": 42, "income": 90000, "widow": True, "disability": True, "purpose": "pension"},
    )

    assert response.status_code == 200
    form_ids = {item["form_id"] for item in response.json()["recommendations"]}
    assert "widow_pension_assistance" in form_ids
    assert "disability_certificate_assistance" in form_ids
