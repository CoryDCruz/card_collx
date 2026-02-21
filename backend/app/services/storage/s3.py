import logging
from typing import BinaryIO

import boto3
from botocore.exceptions import ClientError

from .base import StorageBackend
from app.core.config import settings

logger = logging.getLogger(__name__)


class S3StorageBackend(StorageBackend):
    """S3-compatible storage (works with Supabase, Cloudflare R2, AWS S3, MinIO, etc.)"""

    def __init__(self):
        self.bucket = settings.S3_BUCKET_NAME
        self.public_url = settings.S3_PUBLIC_URL.rstrip("/")
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT_URL,
            aws_access_key_id=settings.S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
            region_name="auto",
        )

    async def save(
        self,
        file_data: BinaryIO,
        filename: str,
        card_id: int
    ) -> str:
        key = f"cards/{card_id}/{filename}"
        self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=file_data.read(),
            ContentType="image/jpeg",
        )
        logger.info(f"Uploaded to S3: {key}")
        return key

    async def delete(self, file_path: str) -> bool:
        try:
            self.client.delete_object(Bucket=self.bucket, Key=file_path)
            logger.info(f"Deleted from S3: {file_path}")
            return True
        except ClientError:
            logger.exception(f"Failed to delete from S3: {file_path}")
            return False

    async def exists(self, file_path: str) -> bool:
        try:
            self.client.head_object(Bucket=self.bucket, Key=file_path)
            return True
        except ClientError:
            return False

    def get_url(self, file_path: str) -> str:
        return f"{self.public_url}/{file_path}"
