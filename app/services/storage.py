from __future__ import annotations

import os
from pathlib import Path
from typing import Protocol, runtime_checkable, BinaryIO

from app.core.config import get_settings

@runtime_checkable
class FileStorageBackend(Protocol):
    """
    Interface for file storage backends.

    Implementations can store files on local disk, S3, Mongo GridFS, etc.
    """

    def save(self, relative_path: str, data: bytes) -> str:
        """
        Save bytes at the given relative path.

        Returns the normalized storage path that should be stored in the DB.
        """
        ...

    def open(self, relative_path: str) -> BinaryIO:
        """
        Open a file for reading in binary mode.
        """
        ...

    def delete(self, relative_path: str) -> None:
        """
        Delete a stored file. Should not raise if the file does not exist.
        """
        ...

class LocalFileStorageBackend:
    """
    Store files under a local directory pointed to by STORAGE_ROOT.

    Example final path:
        {STORAGE_ROOT}/collections/{collection_id}/documents/{document_id}/{filename}
    """
    def __init__(self,root:Path) -> None:
        self.root = root
    
    def _full_path(self,relative_path:str) -> Path:
        """
        Build an absolute Path under the storage root, preventing path traversal.
        """
        # Normalize relative path to avoid ".." shenanigans
        safe_relative = os.path.normpath(relative_path).lstrip(os.sep)
        full_path = self.root / safe_relative
        return full_path

    def save(self, relative_path: str,data:bytes) -> str:
        full_path = self._full_path(relative_path)
        full_path.parent.mkdir(parents=True,exist_ok=True)

        with full_path.open("wb") as f:
            f.write(data)

        # Return the normalized relative path to store in DB
        return str(full_path.relative_to(self.root))

    def open(self, relative_path:str) -> BinaryIO:
        full_path = self._full_path(relative_path)
        return full_path.open("rb")

    def delete(self, relative_path:str)-> None:
        full_path = self._full_path(relative_path)

        try:
            full_path.unlink()
        except FileNotFoundError:
        # Idempotent delete: ignore missing files
            return
    
def get_default_storage_backend() -> FileStorageBackend:
    """
    Factory for the default storage backend used by the application.

    For now this is local filesystem storage, but it could later be
    replaced with S3, MinIO, Mongo GridFS, etc.
    """
    settings = get_settings()
    root = Path(settings.STORAGE_ROOT)
    root.mkdir(parents=True, exist_ok=True)
    return LocalFileStorageBackend(root=root)
