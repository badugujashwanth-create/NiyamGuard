from fastapi.testclient import TestClient


def ask(client: TestClient, session_id: str, message: str, **extra: str):
    payload = {"session_id": session_id, "message": message, **extra}
    response = client.post("/api/assistant/ask", json=payload)
    assert response.status_code == 200
    return response.json()


def test_health_endpoint(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "NiyamGuard Call Assistant Backend is running",
        "version": "1.0.0",
        "python": "3.12",
    }


def test_get_income_certificate_form(client: TestClient) -> None:
    response = client.get("/api/forms/income-certificate")
    body = response.json()
    assert response.status_code == 200
    assert body["success"] is True
    assert body["form"]["form_id"] == "income_certificate"
    assert len(body["form"]["fields"]) == 13
    assert len(body["form"]["required_documents"]) >= 3


def test_create_and_get_session(client: TestClient) -> None:
    create_response = client.post(
        "/api/sessions",
        json={"form_id": "income_certificate", "language": "telugu"},
    )
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["success"] is True
    assert created["language"] == "telugu"

    get_response = client.get(f"/api/sessions/{created['session_id']}")
    session = get_response.json()["session"]
    assert get_response.status_code == 200
    assert session["conversation"] == []


def test_monthly_income_guidance(client: TestClient, session_id: str) -> None:
    body = ask(client, session_id, "monthly income fifteen thousand what should I enter")
    assert body["field"] == "monthly_income"
    assert body["suggested_value"] == "15000"
    assert body["related_values"] == {"annual_income": "180000"}


def test_annual_income_guidance(client: TestClient, session_id: str) -> None:
    body = ask(client, session_id, "what is annual income for 15000 monthly")
    assert body["field"] == "annual_income"
    assert body["suggested_value"] == "180000"
    assert body["related_values"] == {"monthly_income": "15000"}


def test_invalid_mobile_guidance(client: TestClient, session_id: str) -> None:
    body = ask(client, session_id, "my mobile number is 987654321")
    assert body["field"] == "mobile_number"
    assert body["suggested_value"] is None
    assert body["warning"] == "Mobile number must be 10 digits."
    assert "only 9 digits" in body["reply"]


def test_purpose_guidance_for_mixed_language(client: TestClient, session_id: str) -> None:
    body = ask(client, session_id, "purpose lo scholarship ani rayacha")
    assert body["field"] == "purpose"
    assert body["suggested_value"] == "Scholarship"


def test_address_guidance_for_mixed_language(client: TestClient, session_id: str) -> None:
    body = ask(client, session_id, "address lo emi rayali")
    assert body["field"] == "address"
    assert body["suggested_value"] is None
    assert "house number" in body["reply"].lower()


def test_unknown_field_guidance(client: TestClient, session_id: str) -> None:
    body = ask(client, session_id, "I need help")
    assert body["field"] is None
    assert "which field" in body["reply"]


def test_document_upload_guidance(client: TestClient, session_id: str) -> None:
    body = ask(client, session_id, "income proof upload cheyali ante emi upload cheyali")
    assert body["field"] == "document_upload"
    assert body["detected_language"] == "telugu"
    assert body["auto_fill"] is False
    assert body["should_submit"] is False
    assert "Income Proof" in body["reply"]
    assert "AI file upload" in body["reply"]


def test_catalog_session_suggests_income_certificate(client: TestClient) -> None:
    create_response = client.post(
        "/api/sessions",
        json={"form_id": "catalog", "language": "auto"},
    )
    session_id = create_response.json()["session_id"]
    body = ask(
        client,
        session_id,
        "Scholarship kosam income certificate kavali",
        form_id="catalog",
    )
    assert body["suggested_form_id"] == "income_certificate"
    assert body["suggested_form_name"] == "Income Certificate"
    assert body["detected_language"] == "telugu"
    assert body["auto_fill"] is False
    assert body["should_submit"] is False


def test_catalog_only_suggestion_says_coming_soon(client: TestClient) -> None:
    create_response = client.post(
        "/api/sessions",
        json={"form_id": "catalog", "language": "auto"},
    )
    session_id = create_response.json()["session_id"]
    body = ask(
        client,
        session_id,
        "I need a loan eligibility card",
        form_id="catalog",
    )
    assert body["suggested_form_id"] == "loan_eligibility_card"
    assert body["suggested_form_name"] == "Loan Eligibility Card"
    assert "detailed guided form is coming soon" in body["reply"]
    assert body["auto_fill"] is False
    assert body["should_submit"] is False


def test_current_field_is_used_as_fallback(client: TestClient, session_id: str) -> None:
    body = ask(client, session_id, "what do I type here", current_field="address")
    assert body["field"] == "address"


def test_conversation_is_saved_but_suggested_values_are_not(
    client: TestClient, session_id: str
) -> None:
    ask(client, session_id, "monthly income fifteen thousand")
    session = client.get(f"/api/sessions/{session_id}").json()["session"]
    assert [entry["role"] for entry in session["conversation"]] == ["user", "assistant"]
    assert session["last_detected_language"] == "english"
    assert session["last_field"] == "monthly_income"
    assert "form_values" not in session
    assert "filled_fields" not in session


def test_ask_requires_existing_session(client: TestClient) -> None:
    response = client.post(
        "/api/assistant/ask",
        json={"session_id": "missing", "message": "help with income"},
    )
    assert response.status_code == 404


def test_every_ask_response_has_safety_flags(client: TestClient, session_id: str) -> None:
    messages = [
        "monthly income fifteen thousand",
        "aadhaar number 12345678901",
        "purpose mein kya likhna hai",
        "I need help",
    ]
    for message in messages:
        body = ask(client, session_id, message)
        assert body["auto_fill"] is False
        assert body["should_submit"] is False


def test_telugu_roman_input_returns_telugu_guidance(
    client: TestClient, session_id: str
) -> None:
    body = ask(client, session_id, "purpose lo scholarship ani rayacha")
    assert body["detected_language"] == "telugu"
    assert body["language_code"] == "te-IN"
    assert "అవును" in body["reply"]
    assert body["auto_fill"] is False
    assert body["should_submit"] is False


def test_telugu_monthly_income_explains_everyday_meaning(
    client: TestClient, session_id: str
) -> None:
    body = ask(client, session_id, "monthly income ante enti")
    assert body["detected_language"] == "telugu"
    assert "నెలవారీ ఆదాయం" in body["reply"]
    assert "ఒక నెలలో వచ్చే మొత్తం డబ్బు" in body["reply"]


def test_selected_telugu_language_localizes_occupation_guidance(
    client: TestClient, session_id: str
) -> None:
    body = ask(
        client,
        session_id,
        "what should I enter for occupation",
        language="telugu",
        current_field="occupation",
    )
    assert body["detected_language"] == "telugu"
    assert body["language_code"] == "te-IN"
    assert "మీ పేరు కాదు" in body["reply"]


def test_generic_validity_guidance_does_not_claim_income_rule_for_every_service(
    client: TestClient, session_id: str
) -> None:
    body = ask(
        client,
        session_id,
        "what is the validity",
        form_id="residence_certificate",
        current_field="validity",
        language="english",
    )
    assert body["field"] == "validity"
    assert "differs by service" in body["reply"]
    assert "Income Certificate validity is 6 months" not in body["reply"]


def test_telugu_unicode_input_returns_telugu_guidance(
    client: TestClient, session_id: str
) -> None:
    body = ask(
        client,
        session_id,
        "monthly income పదిహేను వేలు అయితే annual income ఎంత",
    )
    assert body["detected_language"] == "telugu"
    assert body["language_code"] == "te-IN"
    assert body["suggested_value"] == "180000"
    assert "అవుతుంది" in body["reply"]
    assert body["auto_fill"] is False
    assert body["should_submit"] is False


def test_hindi_roman_input_returns_hindi_guidance(
    client: TestClient, session_id: str
) -> None:
    body = ask(client, session_id, "purpose mein scholarship likhna hai kya")
    assert body["detected_language"] == "hindi"
    assert body["language_code"] == "hi-IN"
    assert "हाँ" in body["reply"]
    assert body["auto_fill"] is False
    assert body["should_submit"] is False


def test_hindi_unicode_input_returns_hindi_guidance(
    client: TestClient, session_id: str
) -> None:
    body = ask(client, session_id, "मेरा monthly income 15000 है")
    assert body["detected_language"] == "hindi"
    assert body["language_code"] == "hi-IN"
    assert "आप" in body["reply"]
    assert body["auto_fill"] is False
    assert body["should_submit"] is False


def test_english_input_returns_english_guidance(
    client: TestClient, session_id: str
) -> None:
    body = ask(
        client,
        session_id,
        "monthly income fifteen thousand what should I enter",
    )
    assert body["detected_language"] == "english"
    assert body["language_code"] == "en-IN"
    assert "You can enter 15000" in body["reply"]
    assert body["auto_fill"] is False
    assert body["should_submit"] is False


def test_complete_summary(
    client: TestClient,
    session_id: str,
    complete_form_values: dict[str, str],
    complete_uploaded_documents: dict[str, dict[str, object]],
) -> None:
    response = client.post(
        "/api/assistant/summary",
        json={
            "session_id": session_id,
            "form_values": complete_form_values,
            "uploaded_documents": complete_uploaded_documents,
        },
    )
    body = response.json()
    assert response.status_code == 200
    assert body["missing_fields"] == []
    assert body["missing_documents"] == []
    assert body["warnings"] == []
    assert "Ravi Kumar" in body["summary"]
    assert "123456789012" in body["summary"]
    assert "Scholarship" in body["summary"]
    assert "AI does not submit" in body["summary"]
    assert body["auto_fill"] is False
    assert body["should_submit"] is False


def test_summary_with_missing_values(
    client: TestClient,
    session_id: str,
    complete_form_values: dict[str, str],
    complete_uploaded_documents: dict[str, dict[str, object]],
) -> None:
    complete_form_values.pop("aadhaar_number")
    complete_form_values["address"] = ""
    response = client.post(
        "/api/assistant/summary",
        json={
            "session_id": session_id,
            "form_values": complete_form_values,
            "uploaded_documents": complete_uploaded_documents,
        },
    )
    body = response.json()
    assert response.status_code == 200
    assert body["summary"].startswith("Some required details or documents are still missing.")
    assert body["missing_fields"] == ["aadhaar_number", "address"]
    assert body["missing_documents"] == []
    assert "Aadhaar Number is required." in body["warnings"]
    assert "Full Address is required." in body["warnings"]
    assert body["auto_fill"] is False
    assert body["should_submit"] is False


def test_summary_uses_requested_language(
    client: TestClient,
    session_id: str,
    complete_form_values: dict[str, str],
    complete_uploaded_documents: dict[str, dict[str, object]],
) -> None:
    response = client.post(
        "/api/assistant/summary",
        json={
            "session_id": session_id,
            "form_values": complete_form_values,
            "uploaded_documents": complete_uploaded_documents,
            "language": "telugu",
        },
    )
    body = response.json()
    assert response.status_code == 200
    assert body["detected_language"] == "telugu"
    assert body["language_code"] == "te-IN"
    assert "దయచేసి" in body["summary"]
    assert body["auto_fill"] is False
    assert body["should_submit"] is False


def test_summary_uses_session_last_detected_language(
    client: TestClient,
    session_id: str,
    complete_form_values: dict[str, str],
    complete_uploaded_documents: dict[str, dict[str, object]],
) -> None:
    ask(client, session_id, "purpose lo scholarship ani rayacha")
    response = client.post(
        "/api/assistant/summary",
        json={
            "session_id": session_id,
            "form_values": complete_form_values,
            "uploaded_documents": complete_uploaded_documents,
            "language": "auto",
        },
    )
    body = response.json()
    assert response.status_code == 200
    assert body["detected_language"] == "telugu"
    assert body["language_code"] == "te-IN"
    assert "దయచేసి" in body["summary"]


def test_previous_discussed_field_is_reused(
    client: TestClient, session_id: str
) -> None:
    ask(client, session_id, "monthly income fifteen thousand")
    body = ask(client, session_id, "what does this mean")
    assert body["field"] == "monthly_income"
    assert "Monthly income means" in body["reply"]
