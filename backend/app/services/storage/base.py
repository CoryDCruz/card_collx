from abc import ABC, abstractmethod
from typing import BinaryIO


class StorageBackend(ABC):
    """Abstract storage backend for image files"""

    @abstractmethod
    async def save(
        self,
        file_data: BinaryIO,
        filename: str,
        card_id: int
    ) -> str:
        """
        Save file and return the storage path

        Args:
            file_data: Binary file data to save
            filename: Name of the file
            card_id: ID of the card this image belongs to

        Returns:
            Relative path from base directory
        """
        pass

    @abstractmethod
    async def delete(self, file_path: str) -> bool:
        """
        Delete file from storage

        Args:
            file_path: Relative path to the file

        Returns:
            True if deleted successfully, False if file not found
        """
        pass

    @abstractmethod
    async def exists(self, file_path: str) -> bool:
        """
        Check if file exists

        Args:
            file_path: Relative path to the file

        Returns:
            True if file exists, False otherwise
        """
        pass

    @abstractmethod
    def get_url(self, file_path: str) -> str:
        """
        Get accessible URL for the file

        Args:
            file_path: Relative path to the file

        Returns:
            URL path that can be used to access the file
        """
        pass
