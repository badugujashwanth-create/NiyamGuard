from __future__ import annotations

import pytest

from app.demo.pdf_generator import build_simple_pdf
from app.documents import processing
from app.documents.processing import OCRRequiredError, extract_document


def test_text_processing_preserves_native_provenance() -> None:
    result = extract_document(
        b"Income Certificate validity changed from 12 months to 6 months. Effective 2026-08-01.",
        "circular.txt",
        "text/plain",
    )

    assert result.extraction_source == "NATIVE_TEXT"
    assert result.ocr_used is False
    assert result.ocr_derivative is None
    assert result.page_provenance[0]["source"] == "NATIVE_TEXT"
    assert result.page_provenance[0]["start_offset"] == 0


def test_native_pdf_text_is_preferred_when_sufficient() -> None:
    content = build_simple_pdf([
        "Income Certificate validity changed from 12 months to 6 months. "
        "Effective 2026-08-01. This native text is intentionally long enough for the threshold."
    ])

    result = extract_document(content, "circular.pdf", "application/pdf")

    assert result.extraction_source == "NATIVE_TEXT"
    assert result.ocr_used is False
    assert result.page_provenance[0]["page_number"] == 1


def test_scanned_pdf_fails_closed_when_ocr_is_not_available(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(processing.settings, "ocr_enabled", False)
    scanned_pdf = build_simple_pdf(["x"])

    with pytest.raises(OCRRequiredError, match="requires OCR"):
        extract_document(scanned_pdf, "scanned.pdf", "application/pdf")


def test_ocr_derivative_is_separate_and_page_provenance_is_retained(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(processing.settings, "ocr_enabled", True)
    derivative = build_simple_pdf(["Income Certificate validity changed from 12 months to 6 months."])
    monkeypatch.setattr(
        processing,
        "_run_ocr",
        lambda *_args, **_kwargs: (
            derivative,
            [{"page_number": 1, "text": "Income Certificate validity changed from 12 months to 6 months.", "source": "OCR"}],
        ),
    )

    result = extract_document(build_simple_pdf(["x"]), "scanned.pdf", "application/pdf")

    assert result.extraction_source == "OCR"
    assert result.ocr_used is True
    assert result.ocr_derivative == derivative
    assert result.page_provenance[0]["source"] == "OCR"
    assert result.page_provenance[0]["start_offset"] == 0
