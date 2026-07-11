from __future__ import annotations


def _ask(client, message: str, headers: dict[str, str] | None = None) -> dict:
    session = client.post(
        "/api/sessions",
        headers=headers,
        json={"form_id": "income_certificate", "language": "auto"},
    ).json()["session_id"]
    response = client.post(
        "/api/assistant/ask",
        headers=headers,
        json={"session_id": session, "form_id": "income_certificate", "message": message},
    )
    assert response.status_code == 200
    return response.json()


def test_voice_form_assistant_understands_mandal(client):
    body = _ask(client, "mandalam")
    assert body["field"] == "mandal"
    assert "administrative area" in body["reply"]
    assert "address proof" in body["reply"]


def test_voice_occupation_guidance(client):
    body = _ask(client, "occupation lo emi rayali")
    assert body["field"] == "occupation"
    assert all(value in body["reply"] for value in ("Student", "Employee", "Farmer", "Homemaker"))


def test_voice_form_assistant_understands_occupation_wrong_name(client):
    body = _ask(client, "occupation lag raha hai Imran Ali")
    assert body["field"] == "occupation"
    assert body["detected_language"] == "hindi"
    assert "आपका नाम नहीं" in body["reply"]


def test_voice_form_assistant_understands_monthly_income(client):
    body = _ask(client, "manual income")
    assert body["field"] == "monthly_income"
    assert "one month" in body["reply"] and "15000" in body["reply"]


def test_voice_annual_income_guidance(client):
    body = _ask(client, "annual income")
    assert body["field"] == "annual_income"
    assert "multiplied by 12" in body["reply"] and "180000" in body["reply"]


def test_voice_aadhaar_guidance(client):
    body = _ask(client, "aadhaar")
    assert body["field"] == "aadhaar_number"
    assert "12-digit" in body["reply"] and "private" in body["reply"]


def test_voice_mobile_guidance(client):
    body = _ask(client, "mobile number")
    assert body["field"] == "mobile_number"
    assert "10-digit" in body["reply"] and "OTP" in body["reply"]


def test_voice_documents_guidance(client):
    body = _ask(client, "documents enti")
    assert body["field"] == "document_upload"
    assert "Aadhaar" in body["reply"] and "Income Proof" in body["reply"]


def test_voice_form_assistant_validity_source_go_138(client):
    body = _ask(client, "income certificate validity entha")
    assert body["field"] == "validity"
    assert "6 months" in body["reply"] and "GO-138" in body["reply"]


def test_voice_unknown_fallback(client):
    body = _ask(client, "random words")
    assert body["field"] is None
    assert "which field" in body["reply"].lower()


def test_citizen_can_call_voice_assistant(client, citizen_headers):
    assert _ask(client, "monthly income", citizen_headers)["field"] == "monthly_income"


def test_officer_can_load_pending_applications(client, officer_headers):
    assert client.get("/api/government/applications/pending", headers=officer_headers).status_code == 200


def test_admin_routes_allow_admin(client, admin_headers):
    assert client.get("/api/applications", headers=admin_headers).status_code == 200
    assert client.get("/api/government/applications", headers=admin_headers).status_code == 200


def test_sandbox_routes_allow_sandbox_admin(client):
    login = client.post(
        "/api/auth/login",
        json={"email": "sandbox@niyamguard.local", "password": "Sandbox@12345"},
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    assert client.get("/api/sandbox/circulars", headers=headers).status_code == 200


def _submitted_application(client, citizen_headers) -> dict:
    values = {
        "applicant_name": "Imran Ali",
        "mobile_number": "9876543210",
        "district": "Hyderabad",
        "mandal": "Ameerpet",
        "address": "House 1, Ameerpet, Hyderabad",
        "purpose": "Education",
        "annual_income": 180000,
        "occupation": "Student",
    }
    created = client.post(
        "/api/applications",
        headers=citizen_headers,
        json={"service_id": "income_certificate", "form_values": values},
    ).json()["application"]
    for document_type in ("aadhaar", "ration_card", "income_affidavit", "passport_photo"):
        response = client.post(
            f"/api/applications/{created['id']}/documents",
            headers=citizen_headers,
            data={"document_type": document_type},
            files={"file": (f"{document_type}.pdf", b"%PDF-1.4 test", "application/pdf")},
        )
        assert response.status_code == 201
    assert client.post(f"/api/applications/{created['id']}/submit", headers=citizen_headers).status_code == 200
    payment = client.post(f"/api/payments/{created['id']}/create", headers=citizen_headers).json()["payment"]
    assert client.post(f"/api/payments/{payment['id']}/simulate-success", headers=citizen_headers).status_code == 200
    return created


def test_officer_can_review_application(client, citizen_headers, officer_headers):
    application = _submitted_application(client, citizen_headers)
    pending = client.get("/api/government/applications/pending", headers=officer_headers)
    assert any(item["id"] == application["id"] for item in pending.json()["applications"])


def test_admin_can_review_application(client, citizen_headers, admin_headers):
    application = _submitted_application(client, citizen_headers)
    applications = client.get("/api/government/applications", headers=admin_headers)
    assert any(item["id"] == application["id"] for item in applications.json()["applications"])


def test_officer_can_approve_application(client, citizen_headers, officer_headers):
    application = _submitted_application(client, citizen_headers)
    response = client.post(
        f"/api/government/applications/{application['id']}/approve",
        headers=officer_headers,
        json={"notes": "Evidence verified."},
    )
    assert response.status_code == 200
    assert response.json()["application"]["status"] == "certificate_issued"
    assert response.json()["application"]["certificate"]


def test_application_reject_flow(client, citizen_headers, admin_headers):
    application = _submitted_application(client, citizen_headers)
    response = client.post(
        f"/api/government/applications/{application['id']}/reject",
        headers=admin_headers,
        json={"reason": "Evidence is incomplete."},
    )
    assert response.status_code == 200
    assert response.json()["application"]["status"] == "rejected"


def _sandbox_headers(client) -> dict[str, str]:
    login = client.post(
        "/api/auth/login",
        json={"email": "sandbox@niyamguard.local", "password": "Sandbox@12345"},
    )
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def _sandbox_payload(number: str = "GO-200") -> dict[str, str]:
    return {
        "department": "Social Welfare Department",
        "circular_number": number,
        "title": "Caste Certificate Document Update",
        "service_affected": "Caste Certificate",
        "rule_key": "required_document",
        "old_value": "Legacy address proof",
        "new_value": "Current address proof",
        "effective_date": "2026-08-01",
        "body": "Caste Certificate address proof changed from legacy to current proof.",
    }


def _create_sandbox(client, headers, number: str = "GO-200") -> dict:
    response = client.post("/api/sandbox/circulars", headers=headers, json=_sandbox_payload(number))
    assert response.status_code == 200
    return response.json()["circular"]


def test_sandbox_create_circular(client):
    circular = _create_sandbox(client, _sandbox_headers(client), "GO-200-CREATE")
    assert circular["department"] == "Social Welfare Department"


def test_sandbox_rejects_empty_or_unchanged_circular_data(client):
    headers = _sandbox_headers(client)
    empty = client.post("/api/sandbox/circulars", headers=headers, json={**_sandbox_payload(), "circular_number": ""})
    unchanged = client.post(
        "/api/sandbox/circulars",
        headers=headers,
        json={**_sandbox_payload(), "old_value": "6 months", "new_value": "6 months"},
    )
    assert empty.status_code == 422
    assert unchanged.status_code == 422


def test_sandbox_admin_can_generate_circular_pdf(client):
    headers = _sandbox_headers(client)
    circular = _create_sandbox(client, headers, "GO-200-PDF")
    response = client.post(f"/api/sandbox/circulars/{circular['id']}/generate-pdf", headers=headers)
    assert response.status_code == 200 and response.json()["pdf_url"]


def test_sandbox_pdf_contains_real_data(client):
    headers = _sandbox_headers(client)
    circular = _create_sandbox(client, headers, "GO-200-DATA")
    client.post(f"/api/sandbox/circulars/{circular['id']}/generate-pdf", headers=headers)
    pdf = client.get(f"/api/sandbox/circulars/{circular['id']}/pdf", headers=headers)
    assert pdf.content.startswith(b"%PDF")
    for expected in (b"Social Welfare Department", b"GO-200-DATA", b"Caste Certificate", b"Legacy address proof", b"Current address proof"):
        assert expected in pdf.content


def test_sandbox_publish_delivers_to_government_inbox(client, officer_headers):
    headers = _sandbox_headers(client)
    circular = _create_sandbox(client, headers, "GO-200-PUBLISH")
    client.post(f"/api/sandbox/circulars/{circular['id']}/generate-pdf", headers=headers)
    response = client.post(f"/api/sandbox/circulars/{circular['id']}/publish", headers=headers)
    assert response.status_code == 200
    assert response.json()["government_document"]["id"]
    inbox = client.get("/api/government/circular-inbox", headers=officer_headers).json()["circulars"]
    assert any(item["circular_number"] == "GO-200-PUBLISH" for item in inbox)


def test_public_certificate_verification_still_public(client):
    response = client.get("/api/verify-certificate/does-not-exist")
    assert response.status_code == 200
    assert response.json()["valid"] is False


def test_government_inbox_receives_sandbox_circular(client, officer_headers):
    headers = _sandbox_headers(client)
    circular = _create_sandbox(client, headers, "GO-200-INBOX")
    client.post(f"/api/sandbox/circulars/{circular['id']}/generate-pdf", headers=headers)
    client.post(f"/api/sandbox/circulars/{circular['id']}/publish", headers=headers)
    inbox = client.get("/api/government/circular-inbox", headers=officer_headers).json()["circulars"]
    item = next(item for item in inbox if item["circular_number"] == "GO-200-INBOX")
    assert item["status"] == "Received" and item["pdf_available"] is True
    pdf = client.get(item["pdf_url"], headers=officer_headers)
    assert pdf.status_code == 200 and pdf.content.startswith(b"%PDF")
