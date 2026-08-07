from __future__ import annotations

import hashlib
import os
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any, Protocol

from app.config import settings


class ObjectStorageError(RuntimeError):
    """Raised when an object cannot be read or written safely."""


class ObjectStorageUnavailable(ObjectStorageError):
    """Raised when a configured object-storage service is unavailable."""


class StorageBackend(Protocol):
    def put(self, key: str, content: bytes, *, content_type: str, metadata: dict[str, str] | None = None) -> dict[str, Any]: ...

    def get(self, key: str) -> bytes: ...

    def exists(self, key: str) -> bool: ...

    def delete(self, key: str) -> None: ...

    def metadata(self, key: str) -> dict[str, Any]: ...

    def health(self) -> dict[str, Any]: ...


def _safe_key(key: str) -> str:
    raw = str(key or "").replace("\\", "/")
    if raw.startswith("/") or (len(raw) >= 2 and raw[1] == ":"):
        raise ObjectStorageError("Object key is invalid.")
    normalized = raw.strip("/")
    path = PurePosixPath(normalized)
    if not normalized or path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise ObjectStorageError("Object key is invalid.")
    if any(ord(char) < 32 for char in normalized):
        raise ObjectStorageError("Object key contains control characters.")
    return "/".join(path.parts)


class LocalObjectStorage:
    """Filesystem-backed implementation for development and tests only."""

    def __init__(self, root: Path) -> None:
        self.root = Path(root).resolve()

    def _path(self, key: str) -> Path:
        safe_key = _safe_key(key)
        candidate = (self.root / Path(*PurePosixPath(safe_key).parts)).resolve()
        if not candidate.is_relative_to(self.root):
            raise ObjectStorageError("Object key escapes the storage root.")
        return candidate

    def put(self, key: str, content: bytes, *, content_type: str, metadata: dict[str, str] | None = None) -> dict[str, Any]:
        target = self._path(key)
        temporary: Path | None = None
        try:
            target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            with tempfile.NamedTemporaryFile(mode="wb", prefix=".object-", dir=target.parent, delete=False) as handle:
                temporary = Path(handle.name)
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
            os.chmod(temporary, 0o600)
            os.replace(temporary, target)
            return {
                "key": _safe_key(key),
                "size": len(content),
                "etag": hashlib.md5(content).hexdigest(),  # noqa: S324 - local object identity, not security
                "content_type": content_type,
                "metadata": metadata or {},
            }
        except OSError as exc:
            raise ObjectStorageUnavailable("Local object storage is unavailable.") from exc
        finally:
            if temporary and temporary.exists():
                temporary.unlink(missing_ok=True)

    def get(self, key: str) -> bytes:
        try:
            return self._path(key).read_bytes()
        except FileNotFoundError as exc:
            raise ObjectStorageError("Object was not found.") from exc
        except OSError as exc:
            raise ObjectStorageUnavailable("Local object storage is unavailable.") from exc

    def exists(self, key: str) -> bool:
        try:
            return self._path(key).is_file()
        except ObjectStorageError:
            return False

    def delete(self, key: str) -> None:
        try:
            self._path(key).unlink(missing_ok=True)
        except OSError as exc:
            raise ObjectStorageUnavailable("Local object storage is unavailable.") from exc

    def metadata(self, key: str) -> dict[str, Any]:
        try:
            stat = self._path(key).stat()
        except FileNotFoundError as exc:
            raise ObjectStorageError("Object was not found.") from exc
        except OSError as exc:
            raise ObjectStorageUnavailable("Local object storage is unavailable.") from exc
        return {"key": _safe_key(key), "size": stat.st_size, "last_modified": stat.st_mtime}

    def health(self) -> dict[str, Any]:
        try:
            self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
            probe: Path | None = None
            with tempfile.NamedTemporaryFile(prefix=".health-", dir=self.root, delete=False) as handle:
                probe = Path(handle.name)
                handle.write(b"ok")
            if probe:
                probe.unlink(missing_ok=True)
            return {"backend": "local", "ready": True, "required": False}
        except OSError as exc:
            return {"backend": "local", "ready": False, "required": False, "error": str(exc)}


class S3ObjectStorage:
    """S3-compatible implementation with lazy boto3 import."""

    def __init__(
        self,
        *,
        bucket: str,
        region: str,
        endpoint_url: str = "",
        access_key_id: str = "",
        secret_access_key: str = "",
        use_ssl: bool = True,
    ) -> None:
        if not bucket:
            raise ObjectStorageUnavailable("OBJECT_STORAGE_BUCKET is required for S3 storage.")
        try:
            import boto3
        except ImportError as exc:
            raise ObjectStorageUnavailable("The boto3 package is required for S3 object storage.") from exc
        self.bucket = bucket
        self.client = boto3.client(
            "s3",
            region_name=region,
            endpoint_url=endpoint_url or None,
            aws_access_key_id=access_key_id or None,
            aws_secret_access_key=secret_access_key or None,
            use_ssl=use_ssl,
        )

    def put(self, key: str, content: bytes, *, content_type: str, metadata: dict[str, str] | None = None) -> dict[str, Any]:
        safe_key = _safe_key(key)
        try:
            response = self.client.put_object(
                Bucket=self.bucket,
                Key=safe_key,
                Body=content,
                ContentType=content_type,
                Metadata=metadata or {},
            )
        except Exception as exc:  # boto3 exposes provider-specific exception classes
            raise ObjectStorageUnavailable("S3 object storage is unavailable.") from exc
        return {"key": safe_key, "size": len(content), "etag": str(response.get("ETag", "")).strip('"'), "content_type": content_type, "metadata": metadata or {}}

    def get(self, key: str) -> bytes:
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=_safe_key(key))
            return response["Body"].read()
        except Exception as exc:
            raise ObjectStorageError("Object was not found or could not be read.") from exc

    def exists(self, key: str) -> bool:
        try:
            self.client.head_object(Bucket=self.bucket, Key=_safe_key(key))
            return True
        except Exception:
            return False

    def delete(self, key: str) -> None:
        try:
            self.client.delete_object(Bucket=self.bucket, Key=_safe_key(key))
        except Exception as exc:
            raise ObjectStorageUnavailable("S3 object storage is unavailable.") from exc

    def metadata(self, key: str) -> dict[str, Any]:
        try:
            response = self.client.head_object(Bucket=self.bucket, Key=_safe_key(key))
        except Exception as exc:
            raise ObjectStorageError("Object metadata is unavailable.") from exc
        return {"key": _safe_key(key), "size": response.get("ContentLength", 0), "content_type": response.get("ContentType"), "metadata": response.get("Metadata", {})}

    def health(self) -> dict[str, Any]:
        try:
            self.client.head_bucket(Bucket=self.bucket)
            return {"backend": "s3", "ready": True, "required": True, "bucket": self.bucket}
        except Exception as exc:
            return {"backend": "s3", "ready": False, "required": True, "bucket": self.bucket, "error": str(exc)}


def get_object_storage() -> StorageBackend:
    backend = getattr(settings, "object_storage_backend", "local").strip().lower()
    if backend == "local":
        return LocalObjectStorage(settings.object_storage_root)
    if backend == "s3":
        return S3ObjectStorage(
            bucket=settings.object_storage_bucket,
            region=settings.object_storage_region,
            endpoint_url=settings.object_storage_endpoint_url,
            access_key_id=settings.object_storage_access_key_id,
            secret_access_key=settings.object_storage_secret_access_key,
            use_ssl=settings.object_storage_use_ssl,
        )
    raise ObjectStorageUnavailable("Unsupported object storage backend.")
