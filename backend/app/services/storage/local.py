from pathlib import Path
from typing import BinaryIO
import aiofiles

from .base import StorageBackend


class LocalStorageBackend(StorageBackend):
    """Local filesystem storage implementation"""

    def __init__(self, base_dir: str):
        """
        Initialize local storage backend

        Args:
            base_dir: Base directory for file storage
        """
        self.base_dir = Path(base_dir).resolve()

    async def save(
        self,
        file_data: BinaryIO,
        filename: str,
        card_id: int
    ) -> str:
        """
        Save file to uploads/{card_id}/{filename}

        Returns:
            Relative path from base_dir
        """
        # Create card-specific directory
        card_dir = self.base_dir / str(card_id)
        card_dir.mkdir(parents=True, exist_ok=True)

        # Full file path
        file_path = card_dir / filename

        # Write file asynchronously
        async with aiofiles.open(file_path, 'wb') as f:
            content = file_data.read()
            await f.write(content)

        # Return relative path for database storage
        return f"{card_id}/{filename}"

    async def delete(self, file_path: str) -> bool:
        """Delete file from filesystem"""
        full_path = self.base_dir / file_path
        try:
            full_path.unlink()
            # Clean up empty directories
            parent = full_path.parent
            if parent != self.base_dir and not any(parent.iterdir()):
                parent.rmdir()
            return True
        except FileNotFoundError:
            return False

    async def exists(self, file_path: str) -> bool:
        """Check if file exists"""
        return (self.base_dir / file_path).exists()

    def get_url(self, file_path: str) -> str:
        """Get URL path for static file serving"""
        return f"/uploads/{file_path}"
