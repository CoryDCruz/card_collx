from typing import Tuple
from fastapi import UploadFile, HTTPException
from .image_processor import ImageProcessor
from .storage import get_storage_backend, StorageBackend
from app.core.config import settings


class ImageService:
    """High-level service for managing card images"""

    def __init__(
        self,
        storage_backend: StorageBackend = None,
        image_processor: ImageProcessor = None
    ):
        """
        Initialize image service

        Args:
            storage_backend: Storage backend to use (defaults to configured backend)
            image_processor: Image processor to use (defaults to new instance)
        """
        self.storage = storage_backend or get_storage_backend()
        self.processor = image_processor or ImageProcessor()

    async def save_card_image(
        self,
        upload_file: UploadFile,
        card_id: int
    ) -> str:
        """
        Process and save uploaded card image

        Args:
            upload_file: Uploaded file from FastAPI
            card_id: ID of the card this image belongs to

        Returns:
            Image URL for database storage

        Raises:
            HTTPException: If validation or processing fails
        """
        # Read file data
        file_data = await upload_file.read()

        # Validate file
        self.processor.validate_file(
            file_data,
            upload_file.content_type
        )

        # Process image (resize, optimize)
        processed_io, format_ext = self.processor.process_image(file_data)

        # Generate safe filename
        filename = self.processor.generate_filename(
            upload_file.filename,
            file_data,
            card_id
        )

        # Save to storage
        relative_path = await self.storage.save(
            processed_io,
            filename,
            card_id
        )

        # Return URL for database storage
        return self.storage.get_url(relative_path)

    async def save_card_image_with_bytes(
        self,
        upload_file: UploadFile,
        card_id: int
    ) -> Tuple[str, bytes]:
        """
        Process and save uploaded card image, also returning processed bytes.

        Returns:
            Tuple of (image_url, processed_bytes)
        """
        file_data = await upload_file.read()

        self.processor.validate_file(
            file_data,
            upload_file.content_type
        )

        processed_io, format_ext = self.processor.process_image(file_data)

        # Capture processed bytes before storage consumes the stream
        processed_bytes = processed_io.read()
        processed_io.seek(0)

        filename = self.processor.generate_filename(
            upload_file.filename,
            file_data,
            card_id
        )

        relative_path = await self.storage.save(
            processed_io,
            filename,
            card_id
        )

        return self.storage.get_url(relative_path), processed_bytes

    async def delete_card_image(self, image_url: str) -> bool:
        """
        Delete a card image by its URL

        Args:
            image_url: URL of the image to delete (local /uploads/... or R2 https://...)

        Returns:
            True if deleted successfully, False otherwise
        """
        if image_url.startswith('/uploads/'):
            relative_path = image_url[9:]  # Remove '/uploads/' prefix
            return await self.storage.delete(relative_path)
        elif settings.S3_PUBLIC_URL and image_url.startswith(settings.S3_PUBLIC_URL):
            # S3 URL — extract the key after the public URL prefix
            s3_key = image_url[len(settings.S3_PUBLIC_URL.rstrip("/")) + 1:]
            return await self.storage.delete(s3_key)
        return False

    async def image_exists(self, image_url: str) -> bool:
        """
        Check if image exists

        Args:
            image_url: URL of the image to check

        Returns:
            True if image exists, False otherwise
        """
        if image_url.startswith('/uploads/'):
            relative_path = image_url[9:]
            return await self.storage.exists(relative_path)
        return False
