from __future__ import annotations


def _complete_income_values() -> dict[str, object]:
    return {
        "applicant_name": "Ravi Kumar",
        "mobile_number": "9876543210",
        "district": "Hyderabad",
        "mandal": "Ameerpet",
        "address": "House 1, Ameerpet, Hyderabad",
        "purpose": "Post-matric scholarship",
        "annual_income": 180000,
        "occupation": "Student family",
    }


def _create_income_application(client, headers) -> dict:
    response = client.post(
        "/api/applications",
        headers=headers,
        json={"service_id": "income_certificate", "form_values": _complete_income_values()},
    )
    assert response.status_code == 201
    return response.json()["application"]


def _upload_required_docs(client, headers, application_id: str) -> None:
    for document_type in ("aadhaar", "income_proof", "address_proof"):
        response = client.post(
            f"/api/applications/{application_id}/documents",
            headers=headers,
            data={"document_type": document_type},
            files={"file": (f"{document_type}.pdf", b"%PDF-1.4 demo", "application/pdf")},
        )
        assert response.status_code == 201


def test_service_portal_seeded_catalog(client):
    response = client.get("/api/portal/services")

    assert response.status_code == 200
    services = response.json()["services"]
    assert len(services) >= 10
    income = next(item for item in services if item["service_id"] == "income_certificate")
    assert income["fee_amount"] == 35
    assert income["rule_bindings_json"]["latest_rule_id"] == "rule_001"

    detail = client.get("/api/portal/services/income_certificate").json()["service"]
    assert detail["form"]["service_id"] == "income_certificate"
    assert "aadhaar" in detail["form"]["validation_rules_json"]["required_documents"]


def test_application_upload_payment_review_certificate_flow(client, citizen_headers, officer_headers):
    application = _create_income_application(client, citizen_headers)
    assert application["application_number"].startswith("NGSP-")
    assert application["status"] == "draft"

    missing_response = client.post(f"/api/applications/{application['id']}/submit", headers=citizen_headers)
    assert missing_response.status_code == 422
    assert "Missing required items" in missing_response.json()["error"]["message"]

    invalid_upload = client.post(
        f"/api/applications/{application['id']}/documents",
        headers=citizen_headers,
        data={"document_type": "aadhaar"},
        files={"file": ("aadhaar.txt", b"bad", "text/plain")},
    )
    assert invalid_upload.status_code == 400

    _upload_required_docs(client, citizen_headers, application["id"])
    submitted = client.post(f"/api/applications/{application['id']}/submit", headers=citizen_headers)
    assert submitted.status_code == 200
    assert submitted.json()["application"]["status"] == "payment_pending"

    payment_response = client.post(f"/api/payments/{application['id']}/create", headers=citizen_headers)
    assert payment_response.status_code == 201
    payment = payment_response.json()["payment"]
    assert payment["amount"] == 35
    paid = client.post(f"/api/payments/{payment['id']}/simulate-success", headers=citizen_headers)
    assert paid.status_code == 200

    refreshed = client.get(f"/api/applications/{application['id']}", headers=citizen_headers).json()["application"]
    assert refreshed["status"] == "under_review"
    assert refreshed["sla"]["status"] in {"within_sla", "due_soon"}

    pending = client.get("/api/officer/pending", headers=officer_headers)
    assert pending.status_code == 200
    assert any(item["id"] == application["id"] for item in pending.json()["applications"])

    approved_response = client.post(
        f"/api/officer/applications/{application['id']}/approve",
        headers=officer_headers,
        json={"notes": "All evidence accepted."},
    )
    assert approved_response.status_code == 200
    approved = approved_response.json()["application"]
    assert approved["status"] == "certificate_issued"
    certificate = approved["certificate"]
    assert certificate["certificate_number"].startswith("NGCERT-")
    assert certificate["source_rule_version_id"] == "version_rule_001_2"

    verify = client.get(f"/api/certificates/verify/{certificate['verification_hash']}")
    assert verify.status_code == 200
    assert verify.json()["valid"] is True
    assert verify.json()["service_name"] == "Income Certificate"

    download = client.get(f"/api/certificates/{certificate['id']}/download", headers=citizen_headers)
    assert download.status_code == 200
    assert download.headers["content-type"].startswith("application/pdf")

    track = client.get(f"/api/track/{approved['application_number']}")
    assert track.status_code == 200
    assert track.json()["tracking"]["status"] == "certificate_issued"

    notifications = client.get("/api/notifications", headers=citizen_headers).json()["notifications"]
    assert any(item["notification_type"] == "certificate_issued" for item in notifications)


def test_service_portal_access_control(client, citizen_headers, viewer_headers):
    application = _create_income_application(client, citizen_headers)

    forbidden = client.get(f"/api/applications/{application['id']}", headers=viewer_headers)
    assert forbidden.status_code == 403

    officer_only = client.get("/api/officer/applications", headers=citizen_headers)
    assert officer_only.status_code == 403
