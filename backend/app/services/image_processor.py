from PIL import Image
from io import BytesIO
from typing import Tuple
import hashlib
from datetime import datetime
import re
from fastapi import HTTPException


class ImageProcessor:
    """Service for processing and validating uploaded images"""

    # Supported formats
    ALLOWED_FORMATS = {'JPEG', 'PNG', 'WEBP', 'HEIC', 'HEIF'}
    ALLOWED_MIME_TYPES = {
        'image/jpeg', 'image/jpg', 'image/png',
        'image/webp', 'image/heic', 'image/heif'
    }

    # Processing settings
    MAX_DIMENSION = 1024
    JPEG_QUALITY = 85
    PNG_OPTIMIZE = True

    def validate_file(
        self,
        file_data: bytes,
        content_type: str,
        max_size: int = 10 * 1024 * 1024
    ) -> None:
        """
        Validate uploaded file
        Raises HTTPException if validation fails

        Args:
            file_data: Raw file bytes
            content_type: MIME type of the file
            max_size: Maximum allowed file size in bytes
        """
        # Check file size
        if len(file_data) > max_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {max_size / (1024*1024):.1f}MB"
            )

        # Check MIME type
        if content_type not in self.ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {', '.join(self.ALLOWED_MIME_TYPES)}"
            )

        # Validate image can be opened
        try:
            img = Image.open(BytesIO(file_data))
            img.verify()  # Verify it's actually an image
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid or corrupted image file: {str(e)}"
            )

    def process_image(
        self,
        file_data: bytes
    ) -> Tuple[BytesIO, str]:
        """
        Process image: resize, optimize, convert format if needed
        Returns (processed_file_io, format)

        Args:
            file_data: Raw image bytes

        Returns:
            Tuple of (processed image BytesIO, output format)
        """
        # Open image
        img = Image.open(BytesIO(file_data))

        # Convert RGBA to RGB if necessary (for JPEG)
        if img.mode in ('RGBA', 'LA', 'P'):
            # Create white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        # Resize if needed while maintaining aspect ratio
        if img.width > self.MAX_DIMENSION or img.height > self.MAX_DIMENSION:
            img.thumbnail(
                (self.MAX_DIMENSION, self.MAX_DIMENSION),
                Image.Resampling.LANCZOS
            )

        # Save to BytesIO with optimization
        output = BytesIO()

        # Determine output format (always use JPEG for consistency and compression)
        output_format = 'JPEG'
        img.save(
            output,
            format=output_format,
            quality=self.JPEG_QUALITY,
            optimize=True
        )

        output.seek(0)
        return output, output_format.lower()

    def generate_filename(
        self,
        original_filename: str,
        file_data: bytes,
        card_id: int
    ) -> str:
        """
        Generate safe, unique filename
        Format: {timestamp}_{hash}_{sanitized_original}.jpg

        Args:
            original_filename: Original uploaded filename
            file_data: Raw file bytes
            card_id: ID of the card

        Returns:
            Safe, unique filename
        """
        # Get timestamp
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')

        # Get hash of first 1KB for uniqueness
        file_hash = hashlib.md5(file_data[:1024]).hexdigest()[:8]

        # Sanitize original filename (keep only alphanumeric and basic chars)
        safe_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', original_filename)
        name_without_ext = safe_name.rsplit('.', 1)[0][:50]  # Limit length

        return f"{timestamp}_{file_hash}_{name_without_ext}.jpg"
