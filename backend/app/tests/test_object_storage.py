from __future__ import annotations

import io
import sys
from types import SimpleNamespace

import pytest

from app.storage.object_storage import LocalObjectStorage, ObjectStorageError, S3ObjectStorage


def test_local_object_storage_round_trip_and_metadata(tmp_path) -> None:
    storage = LocalObjectStorage(tmp_path)
    result = storage.put("circulars/original.pdf", b"pdf", content_type="application/pdf", metadata={"sha256": "abc"})

    assert result["key"] == "circulars/original.pdf"
    assert storage.get("circulars/original.pdf") == b"pdf"
    assert storage.exists("circulars/original.pdf") is True
    assert storage.metadata("circulars/original.pdf")["size"] == 3
    storage.delete("circulars/original.pdf")
    assert storage.exists("circulars/original.pdf") is False


@pytest.mark.parametrize("key", ["../escape", "/absolute", "circulars/../escape", "circulars\\..\\escape"])
def test_local_object_storage_rejects_path_traversal(tmp_path, key: str) -> None:
    storage = LocalObjectStorage(tmp_path)

    with pytest.raises(ObjectStorageError):
        storage.put(key, b"unsafe", content_type="text/plain")


def test_local_object_storage_health(tmp_path) -> None:
    assert LocalObjectStorage(tmp_path).health()["ready"] is True


def test_s3_storage_uses_safe_keys_and_provider_client(monkeypatch) -> None:
    objects: dict[str, bytes] = {}

    class FakeClient:
        def put_object(self, **kwargs):
            objects[kwargs["Key"]] = kwargs["Body"]
            return {"ETag": '"etag"'}

        def get_object(self, **kwargs):
            return {"Body": io.BytesIO(objects[kwargs["Key"]])}

        def head_object(self, **kwargs):
            return {"ContentLength": len(objects[kwargs["Key"]]), "ContentType": "text/plain", "Metadata": {}}

        def delete_object(self, **kwargs):
            objects.pop(kwargs["Key"], None)

        def head_bucket(self, **kwargs):
            return {}

    monkeypatch.setitem(sys.modules, "boto3", SimpleNamespace(client=lambda *_args, **_kwargs: FakeClient()))
    storage = S3ObjectStorage(bucket="documents", region="us-east-1")

    storage.put("circulars/document.txt", b"text", content_type="text/plain")
    assert storage.get("circulars/document.txt") == b"text"
    assert storage.health()["ready"] is True
