from .base import StorageBackend
from .local import LocalStorageBackend
from app.core.config import settings


def get_storage_backend() -> StorageBackend:
    """Factory function to get configured storage backend"""
    if settings.STORAGE_TYPE == "s3":
        from .s3 import S3StorageBackend
        return S3StorageBackend()
    return LocalStorageBackend(base_dir=settings.UPLOAD_DIR)


__all__ = ['StorageBackend', 'LocalStorageBackend', 'get_storage_backend']
