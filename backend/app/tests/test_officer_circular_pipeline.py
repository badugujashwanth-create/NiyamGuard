def test_officer_upload_extract_approve_compliance_and_audit(client, officer_headers):
    circular_text = (
        "GO-204 Revenue Department circular. Income Certificate validity is changed "
        "from 12 months to 6 months. This officer upload is effective immediately."
    )
    upload = client.post(
        "/api/circulars/upload-file",
        headers=officer_headers,
        data={
            "circular_number": "GO-204",
            "title": "Income Certificate Validity Update",
            "department": "Revenue Department",
            "effective_date": "2026-08-01",
        },
        files={"file": ("go-204.txt", circular_text.encode(), "text/plain")},
    )
    assert upload.status_code == 200
    body = upload.json()
    assert body["document"]["status"] == "pending_review"
    assert body["extraction"]["status"] == "success"
    assert body["candidates"][0]["status"] == "pending_review"
    assert body["candidates"][0]["confidence_score"] == 0.91

    candidate_id = body["candidates"][0]["id"]
    approval = client.post(
        f"/api/rule-candidates/{candidate_id}/approve",
        headers=officer_headers,
        json={"notes": "Verified against the uploaded circular."},
    )
    assert approval.status_code == 200
    approved = approval.json()
    assert approved["candidate"]["status"] == "approved"
    assert approved["publication"]["rule_version"]["source_circular_number"] == "GO-204"
    assert approved["publication"]["compliance_run"] is not None

    assert client.get("/api/circulars", headers=officer_headers).status_code == 200
    assert client.get("/api/compliance/findings", headers=officer_headers).status_code == 200
    assert client.get("/api/dashboard/priority-findings", headers=officer_headers).status_code == 200
    finding_id = client.get("/api/compliance/findings", headers=officer_headers).json()["findings"][0]["id"]
    assert client.get(f"/api/cascade/finding/{finding_id}", headers=officer_headers).status_code == 200

    audit = client.get("/api/government/audit/events?limit=500", headers=officer_headers)
    assert audit.status_code == 200
    actions = {event["action"] for event in audit.json()["events"]}
    assert {"circular_ingested", "rule_extracted", "candidate_approved", "rule_published"} <= actions
