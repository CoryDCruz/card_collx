from .base import StorageBackend
from .local import LocalStorageBackend
from app.core.config import settings


def get_storage_backend() -> StorageBackend:
    """
    Factory function to get configured storage backend

    Returns:
        Configured storage backend instance
    """
    # For now, always return local storage
    # Future: check settings.STORAGE_TYPE and return S3Backend, etc.
    return LocalStorageBackend(base_dir=settings.UPLOAD_DIR)


__all__ = ['StorageBackend', 'LocalStorageBackend', 'get_storage_backend']
