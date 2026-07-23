from __future__ import annotations

import pytest

from app.demo.pdf_generator import build_simple_pdf
from app.knowledge_base.circular_ingestion_service import extract_temporal_metadata


def test_temporal_metadata_extracts_effective_and_expiry_dates() -> None:
    effective, expiry = extract_temporal_metadata(
        "Effective 2026-07-01. This synthetic circular expires on 2027-06-30."
    )
    assert effective == "2026-07-01"
    assert expiry == "2027-06-30"


def test_temporal_metadata_rejects_expiry_before_effective_date() -> None:
    with pytest.raises(ValueError, match="earlier"):
        extract_temporal_metadata(
            "Effective 2026-07-01. Expires on 2026-06-30."
        )


def test_text_and_pdf_circular_uploads_are_validated(client, reviewer_headers) -> None:
    text = (
        "Income Certificate validity changed from 12 months to 6 months. "
        "Effective 2026-08-01. Expires on 2027-07-31."
    )
    text_response = client.post(
        "/api/circulars/upload-file",
        headers=reviewer_headers,
        data={
            "circular_number": "SYN-TEXT-1",
            "title": "Synthetic text circular",
            "department": "Revenue",
            "published_date": "2026-07-20",
        },
        files={"file": ("synthetic.txt", text.encode("utf-8"), "text/plain")},
    )
    assert text_response.status_code == 200
    assert text_response.json()["synthetic_only"] is True
    assert text_response.json()["document"]["expiry_date"] == "2027-07-31"

    pdf = build_simple_pdf(
        [
            "Income Certificate validity changed from 12 months to 6 months.",
            "Effective 2026-09-01. Expires on 2027-08-31.",
        ]
    )
    pdf_response = client.post(
        "/api/circulars/upload-file",
        headers=reviewer_headers,
        data={
            "circular_number": "SYN-PDF-1",
            "title": "Synthetic PDF circular",
            "department": "Revenue",
            "published_date": "2026-07-21",
        },
        files={"file": ("synthetic.pdf", pdf, "application/pdf")},
    )
    assert pdf_response.status_code == 200
    assert pdf_response.json()["document"]["effective_date"] == "2026-09-01"
    assert pdf_response.json()["document"]["expiry_date"] == "2027-08-31"


def test_circular_upload_rejects_mime_mismatch_and_oversized_file(client, reviewer_headers) -> None:
    data = {
        "circular_number": "SYN-BAD",
        "title": "Invalid synthetic circular",
        "department": "Revenue",
        "published_date": "2026-07-21",
    }
    mismatch = client.post(
        "/api/circulars/upload-file",
        headers=reviewer_headers,
        data=data,
        files={"file": ("synthetic.pdf", b"not a pdf", "text/plain")},
    )
    assert mismatch.status_code == 415

    oversized = client.post(
        "/api/circulars/upload-file",
        headers=reviewer_headers,
        data=data,
        files={"file": ("synthetic.txt", b"x" * (2 * 1024 * 1024 + 1), "text/plain")},
    )
    assert oversized.status_code == 413


def test_circular_upload_requires_reviewer_or_admin_role(client, viewer_headers) -> None:
    response = client.post(
        "/api/circulars/upload-file",
        headers=viewer_headers,
        data={
            "circular_number": "SYN-FORBIDDEN",
            "title": "Forbidden synthetic circular",
            "department": "Revenue",
            "published_date": "2026-07-21",
        },
        files={
            "file": (
                "synthetic.txt",
                b"Effective 2026-08-01. Income Certificate validity changed from 12 months to 6 months.",
                "text/plain",
            )
        },
    )
    assert response.status_code == 403


def test_connected_policy_lifecycle_returns_source_grounded_outputs(client) -> None:
    response = client.post("/api/demo/run-policy-lifecycle")
    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert body["synthetic_only"] is True
    assert [item["key"] for item in body["steps"]] == [
        "reset",
        "ingest",
        "extract",
        "compare",
        "conflicts",
        "impact",
        "review",
        "publish",
        "explain",
        "eligibility",
        "audit",
    ]
    assert body["circular"]["effective_date"] == "2026-07-01"
    assert body["circular"]["expiry_date"] == "2027-06-30"
    assert body["source_evidence"]["excerpt"]
    assert body["source_evidence"]["content_hash"]
    assert body["comparison"]["supersedes_version_id"] == "version_rule_001_2"
    assert body["review_queue"]["available_decisions"] == [
        "approve",
        "reject",
        "request_revision",
    ]
    assert body["publication"]["rule_version"]["previous_version_id"] == "version_rule_001_2"
    assert body["officer_summary"]
    assert body["citizen_explanation"]["source_evidence"]["circular_number"] == "GO-138"
    assert body["eligibility"]["scenario_count"] == 4
    assert body["eligibility"]["changed_count"] == 1
    assert body["audit_events"]


def test_review_queue_supports_revision_request(client, reviewer_headers) -> None:
    sync = client.post("/api/sources/src_revenue_demo/sync", headers=reviewer_headers)
    assert sync.status_code == 200
    extracted = client.post(
        "/api/circulars/cirdoc_go_138/extract-rules",
        headers=reviewer_headers,
    )
    candidate_id = extracted.json()["candidates"][0]["id"]

    response = client.post(
        f"/api/rule-candidates/{candidate_id}/request-revision",
        headers=reviewer_headers,
        json={"notes": "Clarify the expiry clause before publication."},
    )

    assert response.status_code == 200
    assert response.json()["candidate"]["status"] == "needs_revision"
    assert response.json()["workflow"]["status"] == "needs_clarification"
