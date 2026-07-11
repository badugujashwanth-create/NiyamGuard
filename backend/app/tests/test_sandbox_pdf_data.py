from io import BytesIO

from pypdf import PdfReader


def _sandbox_headers(client) -> dict[str, str]:
    login = client.post(
        "/api/auth/login",
        json={"email": "sandbox@niyamguard.local", "password": "Sandbox@12345"},
    )
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def _generate_and_read(client, headers, payload) -> tuple[dict, str]:
    created = client.post("/api/sandbox/circulars", headers=headers, json=payload)
    assert created.status_code == 200
    circular = created.json()["circular"]
    generated = client.post(
        f"/api/sandbox/circulars/{circular['id']}/generate-pdf",
        headers=headers,
    )
    assert generated.status_code == 200
    downloaded = client.get(f"/api/sandbox/circulars/{circular['id']}/pdf", headers=headers)
    assert downloaded.status_code == 200
    text = "\n".join(page.extract_text() or "" for page in PdfReader(BytesIO(downloaded.content)).pages)
    return circular, text


def test_sandbox_pdfs_render_each_circulars_real_values(client):
    headers = _sandbox_headers(client)
    income, income_text = _generate_and_read(
        client,
        headers,
        {
            "department": "Revenue Department",
            "circular_number": "REV-INC-901",
            "title": "Income Certificate Validity Revision",
            "service_affected": "Income Certificate",
            "rule_key": "validity_period",
            "old_value": "12 months",
            "new_value": "6 months",
            "effective_date": "2026-09-01",
            "body": "Income certificate validity is revised for scholarship applications.",
        },
    )
    pension, pension_text = _generate_and_read(
        client,
        headers,
        {
            "department": "Social Welfare Department",
            "circular_number": "SW-PEN-772",
            "title": "Old-Age Pension Eligibility Revision",
            "service_affected": "Old-Age Pension",
            "rule_key": "eligibility_age",
            "old_value": "60 years",
            "new_value": "65 years",
            "effective_date": "2026-10-15",
            "body": "The minimum eligibility age is revised for new pension applications.",
        },
    )

    for expected in (
        "Revenue Department", "REV-INC-901", "Income Certificate", "Validity Period",
        "12 months", "6 months", "2026-09-01",
    ):
        assert expected in income_text
    for expected in (
        "Social Welfare Department", "SW-PEN-772", "Old-Age Pension", "Eligibility Age",
        "60 years", "65 years", "2026-10-15",
    ):
        assert expected in pension_text
    assert pension["id"] != income["id"]
    assert "SW-PEN-772" not in income_text
    assert "REV-INC-901" not in pension_text
