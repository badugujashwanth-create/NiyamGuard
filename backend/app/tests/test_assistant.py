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
    assert len(body["form"]["fields"]) == 11


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
    assert "house number" in body["reply"]


def test_unknown_field_guidance(client: TestClient, session_id: str) -> None:
    body = ask(client, session_id, "I need help")
    assert body["field"] is None
    assert "which field" in body["reply"]


def test_current_field_is_used_as_fallback(client: TestClient, session_id: str) -> None:
    body = ask(client, session_id, "what do I type here", current_field="address")
    assert body["field"] == "address"


def test_conversation_is_saved_but_suggested_values_are_not(
    client: TestClient, session_id: str
) -> None:
    ask(client, session_id, "monthly income fifteen thousand")
    session = client.get(f"/api/sessions/{session_id}").json()["session"]
    assert [entry["role"] for entry in session["conversation"]] == ["user", "assistant"]
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
    assert body["reply"].startswith("You can enter 15000")
    assert body["auto_fill"] is False
    assert body["should_submit"] is False


def test_complete_summary(
    client: TestClient, session_id: str, complete_form_values: dict[str, str]
) -> None:
    response = client.post(
        "/api/assistant/summary",
        json={"session_id": session_id, "form_values": complete_form_values},
    )
    body = response.json()
    assert response.status_code == 200
    assert body["missing_fields"] == []
    assert body["warnings"] == []
    assert "Ravi Kumar" in body["summary"]
    assert "submit the application yourself" in body["summary"]
    assert body["auto_fill"] is False
    assert body["should_submit"] is False


def test_summary_with_missing_values(
    client: TestClient, session_id: str, complete_form_values: dict[str, str]
) -> None:
    complete_form_values.pop("aadhaar_number")
    complete_form_values["address"] = ""
    response = client.post(
        "/api/assistant/summary",
        json={"session_id": session_id, "form_values": complete_form_values},
    )
    body = response.json()
    assert response.status_code == 200
    assert body["summary"] == "Some required details are still missing."
    assert body["missing_fields"] == ["aadhaar_number", "address"]
    assert "Aadhaar Number is required." in body["warnings"]
    assert "Address is required." in body["warnings"]
    assert body["auto_fill"] is False
    assert body["should_submit"] is False


def test_summary_uses_requested_language(
    client: TestClient, session_id: str, complete_form_values: dict[str, str]
) -> None:
    response = client.post(
        "/api/assistant/summary",
        json={
            "session_id": session_id,
            "form_values": complete_form_values,
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
