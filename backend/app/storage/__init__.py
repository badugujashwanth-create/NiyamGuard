"""Document/object storage backends."""

from app.storage.object_storage import (
    ObjectStorageError,
    ObjectStorageUnavailable,
    get_object_storage,
)

__all__ = ["ObjectStorageError", "ObjectStorageUnavailable", "get_object_storage"]
