from __future__ import annotations

import hashlib
from pathlib import Path

from app.config import settings
from app.storage.object_storage import ObjectStorageError, ObjectStorageUnavailable, get_object_storage


class SourceArtifactStorageUnavailable(RuntimeError):
    """Raised when a verified source cannot be persisted safely."""


def persist_circular_source(content: bytes, filename: str, content_type: str) -> dict[str, str | int]:
    """Persist a scanned upload without trusting its user-controlled filename.

    The returned path is an opaque relative storage key. The absolute storage
    root is never returned to an API caller.
    """

    digest = hashlib.sha256(content).hexdigest()
    suffix = Path(filename).suffix.casefold()
    if suffix not in {".pdf", ".txt"}:
        raise SourceArtifactStorageUnavailable("Unsupported source artifact type.")
    key = f"circulars/{digest}{suffix}"
    try:
        storage = get_object_storage()
        existing = storage.exists(key)
        if existing:
            # Content-addressed keys make the original immutable.  Never
            # overwrite an existing artifact, even when a provider permits it.
            if storage.get(key) != content:
                raise SourceArtifactStorageUnavailable("Existing source artifact failed integrity checks.")
            result = {"key": key}
        else:
            result = storage.put(
                key,
                content,
                content_type=content_type,
                metadata={"sha256": digest, "artifact": "original"},
            )
    except SourceArtifactStorageUnavailable:
        raise
    except (ObjectStorageError, ObjectStorageUnavailable) as exc:
        raise SourceArtifactStorageUnavailable("Source artifact storage is unavailable.") from exc

    return {
        "storage_path": str(result["key"]),
        "_storage_created": not existing,
        "source_sha256": digest,
        "source_filename": Path(filename).name[:160],
        "source_content_type": content_type,
        "source_size_bytes": len(content),
    }


def persist_circular_ocr_derivative(
    content: bytes,
    *,
    source_sha256: str,
    content_type: str = "application/pdf",
) -> str:
    """Store OCR output separately from the immutable original artifact."""

    key = f"circulars/ocr/{source_sha256}.pdf"
    try:
        storage = get_object_storage()
        if storage.exists(key):
            if storage.get(key) != content:
                raise SourceArtifactStorageUnavailable("Existing OCR derivative failed integrity checks.")
            return key
        return str(storage.put(
            key,
            content,
            content_type=content_type,
            metadata={"sha256": source_sha256, "artifact": "ocr-derivative"},
        )["key"])
    except (ObjectStorageError, ObjectStorageUnavailable) as exc:
        raise SourceArtifactStorageUnavailable("OCR derivative storage is unavailable.") from exc


def delete_circular_artifact(storage_path: str | None) -> None:
    """Best-effort cleanup for an upload that never became an ingested record."""

    if not storage_path:
        return
    try:
        get_object_storage().delete(storage_path)
    except (ObjectStorageError, ObjectStorageUnavailable):
        # Cleanup must not replace the controlled processing error.  Readiness
        # and object-store health expose an unavailable provider separately.
        return
