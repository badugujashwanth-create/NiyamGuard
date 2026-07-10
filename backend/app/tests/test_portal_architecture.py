from __future__ import annotations

import pytest

from app.services.auth_service import seed_default_users
from app.repositories.auth_repository import auth_repository


def _login(client, email: str, password: str) -> dict:
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def _seed_users() -> None:
    seed_default_users()


def test_sandbox_circular_create_generate_publish_and_government_inbox(client) -> None:
    sandbox_login = _login(client, "sandbox@niyamguard.local", "Sandbox@12345")
    sandbox_token = sandbox_login["access_token"]

    create = client.post(
        "/api/sandbox/circulars",
        json={
            "department": "Revenue Department",
            "circular_number": "GO-138",
            "title": "Income Certificate Validity Update",
            "service_affected": "Income Certificate",
            "rule_key": "validity",
            "old_value": "12 months",
            "new_value": "6 months",
        },
        headers=_auth_headers(sandbox_token),
    )
    assert create.status_code == 200
    circular_id = create.json()["circular"]["id"]

    pdf = client.post(
        f"/api/sandbox/circulars/{circular_id}/generate-pdf",
        headers=_auth_headers(sandbox_token),
    )
    assert pdf.status_code == 200
    body = pdf.json()
    assert body["success"] is True
    assert body["circular_number"] == "GO-138"
    assert body["pdf_url"].endswith("/pdf")

    pdf_download = client.get(f"/api/sandbox/circulars/{circular_id}/pdf")
    assert pdf_download.status_code == 200
    assert pdf_download.headers["content-type"].startswith("application/pdf")
    assert pdf_download.content[:4] == b"%PDF"

    publish = client.post(
        f"/api/sandbox/circulars/{circular_id}/publish",
        headers=_auth_headers(sandbox_token),
    )
    assert publish.status_code == 200
    assert publish.json()["success"] is True
    assert publish.json()["government_document"]["circular_number"] == "GO-138"

    admin_login = _login(client, "admin@niyamguard.local", "Admin@12345")
    admin_token = admin_login["access_token"]

    inbox = client.get("/api/government/circular-inbox", headers=_auth_headers(admin_token))
    assert inbox.status_code == 200
    circulars = inbox.json()["circulars"]
    assert any(item["circular_number"] == "GO-138" for item in circulars)
    government_doc_id = next(item["id"] for item in circulars if item["circular_number"] == "GO-138")

    parsed = client.post(
        f"/api/government/circulars/{government_doc_id}/parse",
        headers=_auth_headers(admin_token),
    )
    assert parsed.status_code == 200
    assert parsed.json()["success"] is True
    assert parsed.json()["detected_change"] is not None

    candidate_id = parsed.json()["detected_change"]["candidate"]["id"]
    approved = client.post(
        f"/api/government/policy-updates/{candidate_id}/approve",
        json={"notes": "Verified in test."},
        headers=_auth_headers(admin_token),
    )
    assert approved.status_code == 200
    assert approved.json()["success"] is True
    assert approved.json()["verified_rule"]["status"] == "Verified"


def test_chatbot_ask_requires_auth_and_returns_answer(client) -> None:
    citizen_login = _login(client, "citizen@niyamguard.local", "Citizen@12345")
    response = client.post(
        "/api/chatbot/ask",
        json={"message": "What documents are needed for income certificate?"},
        headers=_auth_headers(citizen_login["access_token"]),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["answer"]
    assert body["mode"] == "citizen"

    unauth = client.post("/api/chatbot/ask", json={"message": "hello"})
    assert unauth.status_code == 401


def test_auth_role_access_for_portals(client) -> None:
    citizen = _login(client, "citizen@niyamguard.local", "Citizen@12345")
    denied = client.get("/api/sandbox/circulars", headers=_auth_headers(citizen["access_token"]))
    assert denied.status_code == 403

    sandbox = _login(client, "sandbox@niyamguard.local", "Sandbox@12345")
    allowed = client.get("/api/sandbox/circulars", headers=_auth_headers(sandbox["access_token"]))
    assert allowed.status_code == 200

    officer = _login(client, "officer@niyamguard.local", "Officer@12345")
    inbox = client.get("/api/government/circular-inbox", headers=_auth_headers(officer["access_token"]))
    assert inbox.status_code == 200


def test_portal_summary_and_sandbox_status(client) -> None:
    summary = client.get("/api/demo/portal-summary")
    assert summary.status_code == 200
    assert summary.json()["success"] is True
    assert "citizen" in summary.json()["portals"]

    status = client.get("/api/sandbox/status")
    assert status.status_code == 200
    assert status.json()["sandbox"] == "virtual_government"

    sandbox_user = auth_repository.get_user_by_email("sandbox@niyamguard.local")
    assert sandbox_user is not None
    assert sandbox_user.role == "sandbox_admin"
