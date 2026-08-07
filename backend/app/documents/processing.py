from __future__ import annotations

from dataclasses import dataclass
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from app.config import HARDENED_ENVIRONMENTS, settings


MAX_DOCUMENT_PAGES = 100


class DocumentProcessingError(RuntimeError):
    """Raised when a document cannot be safely converted into evidence text."""


class OCRRequiredError(DocumentProcessingError):
    """Raised when native text is insufficient and OCR is unavailable."""


class OCRProcessingError(DocumentProcessingError):
    """Raised when the OCR command fails or returns an unusable derivative."""


@dataclass(frozen=True)
class DocumentExtraction:
    text: str
    extraction_source: str
    ocr_used: bool
    ocr_derivative: bytes | None
    page_provenance: list[dict[str, Any]]


def _pypdf_pages(content: bytes) -> list[dict[str, Any]]:
    from io import BytesIO
    from pypdf import PdfReader

    reader = PdfReader(BytesIO(content), strict=True)
    if reader.is_encrypted:
        raise DocumentProcessingError("Encrypted PDFs are not accepted.")
    return [
        {"page_number": index + 1, "text": (page.extract_text() or "").strip(), "source": "NATIVE_TEXT"}
        for index, page in enumerate(reader.pages)
    ]


def _native_pdf_pages(content: bytes) -> list[dict[str, Any]]:
    """Try PyMuPDF first and use pypdf when it preserves more native text."""

    fitz_pages: list[dict[str, Any]] | None = None
    try:
        try:
            import pymupdf as fitz  # PyMuPDF's current import name
        except ImportError:
            import fitz  # type: ignore[no-redef]  # older PyMuPDF import name

        document = fitz.open(stream=content, filetype="pdf")
        try:
            if getattr(document, "is_encrypted", False):
                raise DocumentProcessingError("Encrypted PDFs are not accepted.")
            fitz_pages = [
                {"page_number": index + 1, "text": (page.get_text("text") or "").strip(), "source": "NATIVE_TEXT"}
                for index, page in enumerate(document)
            ]
        finally:
            document.close()
    except DocumentProcessingError:
        raise
    except Exception:
        fitz_pages = None

    # Some valid PDFs expose text differently to the two native parsers.  A
    # pypdf fallback is still native extraction, not OCR, and prevents a
    # parser-specific omission from triggering the scanned-document path.
    try:
        fallback_pages = _pypdf_pages(content)
    except Exception as exc:
        if fitz_pages is not None:
            if len(fitz_pages) > MAX_DOCUMENT_PAGES:
                raise DocumentProcessingError(f"PDF contains too many pages; the limit is {MAX_DOCUMENT_PAGES}.")
            return fitz_pages
        raise DocumentProcessingError("PDF could not be parsed safely for native text extraction.") from exc
    fitz_chars = sum(len(str(page.get("text") or "")) for page in fitz_pages or [])
    fallback_chars = sum(len(str(page.get("text") or "")) for page in fallback_pages)
    pages = fallback_pages if fitz_pages is None or fallback_chars > fitz_chars else fitz_pages
    if len(pages) > MAX_DOCUMENT_PAGES:
        raise DocumentProcessingError(f"PDF contains too many pages; the limit is {MAX_DOCUMENT_PAGES}.")
    return pages


def _needs_ocr(content: bytes, pages: list[dict[str, Any]]) -> bool:
    text_chars = sum(len(str(page.get("text") or "")) for page in pages)
    page_count = max(len(pages), 1)
    density = text_chars / max(len(content), 1)
    return (
        text_chars < max(settings.ocr_min_text_chars, 1)
        or (text_chars / page_count) < max(settings.ocr_min_text_chars / 2, 1)
        or density < max(settings.ocr_min_text_density, 0.0)
    )


def _run_ocr(content: bytes, filename: str) -> tuple[bytes, list[dict[str, Any]]]:
    if not settings.ocr_enabled:
        raise OCRRequiredError(
            "This document requires OCR, but OCR_ENABLED is false. No incomplete policy text was accepted."
        )
    executable = shutil.which(settings.ocr_command)
    if not executable:
        raise OCRRequiredError(
            "This document requires OCR, but the configured OCRmyPDF command is unavailable."
        )
    suffix = Path(filename).suffix.casefold() or ".pdf"
    try:
        with tempfile.TemporaryDirectory(prefix="niyamguard-ocr-") as directory:
            input_path = Path(directory) / f"source{suffix}"
            output_path = Path(directory) / "ocr-derivative.pdf"
            input_path.write_bytes(content)
            result = subprocess.run(
                [executable, "--skip-text", "-l", settings.ocr_languages, str(input_path), str(output_path)],
                capture_output=True,
                text=True,
                timeout=settings.ocr_timeout_seconds,
                check=False,
            )
            if result.returncode != 0 or not output_path.is_file() or output_path.stat().st_size == 0:
                raise OCRProcessingError("OCR processing failed; the original document was not replaced.")
            derivative = output_path.read_bytes()
    except OCRRequiredError:
        raise
    except OCRProcessingError:
        raise
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise OCRProcessingError("OCR processing failed; the original document was not replaced.") from exc

    pages = _native_pdf_pages(derivative)
    if not any(page.get("text") for page in pages):
        raise OCRProcessingError("OCR completed without usable text; the document requires manual review.")
    for page in pages:
        page["source"] = "OCR"
    return derivative, pages


def extract_document(content: bytes, filename: str, content_type: str) -> DocumentExtraction:
    """Extract normalized evidence text without mutating the original bytes."""

    suffix = Path(filename).suffix.casefold()
    if suffix == ".txt" and content_type == "text/plain":
        try:
            text = content.decode("utf-8").strip()
        except UnicodeDecodeError as exc:
            raise DocumentProcessingError("Text circular must use UTF-8.") from exc
        if len(text) < 20:
            raise DocumentProcessingError("No usable text was found in the uploaded document.")
        return DocumentExtraction(
            text=text[:250_000],
            extraction_source="NATIVE_TEXT",
            ocr_used=False,
            ocr_derivative=None,
            page_provenance=[{"page_number": 1, "start_offset": 0, "end_offset": len(text), "source": "NATIVE_TEXT"}],
        )

    if suffix != ".pdf" or content_type != "application/pdf" or not content.startswith(b"%PDF"):
        raise DocumentProcessingError("Only valid PDF or UTF-8 text documents are accepted.")
    pages = _native_pdf_pages(content)
    if not _needs_ocr(content, pages):
        extraction_source = "NATIVE_TEXT"
        derivative = None
    else:
        derivative, pages = _run_ocr(content, filename)
        extraction_source = "OCR"
    text_parts: list[str] = []
    provenance: list[dict[str, Any]] = []
    cursor = 0
    for page in pages:
        page_text = str(page.get("text") or "").strip()
        if not page_text:
            continue
        if text_parts:
            cursor += 1
        start = cursor
        text_parts.append(page_text)
        cursor += len(page_text)
        provenance.append(
            {
                "page_number": page["page_number"],
                "start_offset": start,
                "end_offset": cursor,
                "source": extraction_source,
            }
        )
    text = "\n".join(text_parts).strip()
    if len(text) < 20:
        if extraction_source == "NATIVE_TEXT":
            raise OCRRequiredError("This document requires OCR; native PDF text was insufficient.")
        raise DocumentProcessingError("No usable text was found after OCR processing.")
    return DocumentExtraction(
        text=text[:250_000],
        extraction_source=extraction_source,
        ocr_used=extraction_source == "OCR",
        ocr_derivative=derivative,
        page_provenance=provenance,
    )


def ocr_health() -> dict[str, Any]:
    hardened = settings.app_env.strip().lower() in HARDENED_ENVIRONMENTS
    if not settings.ocr_enabled:
        return {
            "enabled": False,
            "available": not hardened,
            "ready": not hardened,
            "required": hardened,
            "command": settings.ocr_command,
        }
    executable = shutil.which(settings.ocr_command)
    if not executable:
        return {
            "enabled": True,
            "available": False,
            "ready": False,
            "required": hardened,
            "command": settings.ocr_command,
            "languages": settings.ocr_languages,
        }
    try:
        version = subprocess.run(
            [executable, "--version"],
            capture_output=True,
            text=True,
            timeout=min(settings.ocr_timeout_seconds, 10),
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {
            "enabled": True,
            "available": False,
            "ready": False,
            "required": hardened,
            "command": settings.ocr_command,
            "languages": settings.ocr_languages,
            "error": str(exc),
        }
    ready = version.returncode == 0
    return {
        "enabled": True,
        "available": ready,
        "ready": ready,
        "required": hardened,
        "command": settings.ocr_command,
        "languages": settings.ocr_languages,
        "version": (version.stdout or version.stderr).strip().splitlines()[0][:120] if (version.stdout or version.stderr) else None,
    }
