from __future__ import annotations

import hashlib
import os
import tempfile
from pathlib import Path

from app.config import settings


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
    root = settings.circular_artifact_storage_dir.resolve()
    target_dir = root
    target = target_dir / f"{digest}{suffix}"
    try:
        target_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        if target.exists():
            if target.is_symlink():
                raise SourceArtifactStorageUnavailable("Existing source artifact failed integrity checks.")
            if target.stat().st_size != len(content):
                raise SourceArtifactStorageUnavailable("Existing source artifact failed integrity checks.")
        else:
            temporary_path: Path | None = None
            try:
                with tempfile.NamedTemporaryFile(
                    mode="wb",
                    prefix=f".{digest}.",
                    suffix=".upload",
                    dir=target_dir,
                    delete=False,
                ) as handle:
                    temporary_path = Path(handle.name)
                    handle.write(content)
                    handle.flush()
                    os.fsync(handle.fileno())
                os.chmod(temporary_path, 0o600)
                os.replace(temporary_path, target)
            finally:
                if temporary_path and temporary_path.exists():
                    temporary_path.unlink(missing_ok=True)
    except (OSError, ValueError) as exc:
        raise SourceArtifactStorageUnavailable("Source artifact storage is unavailable.") from exc

    return {
        "storage_path": f"circulars/{digest}{suffix}",
        "source_sha256": digest,
        "source_filename": Path(filename).name[:160],
        "source_content_type": content_type,
        "source_size_bytes": len(content),
    }
