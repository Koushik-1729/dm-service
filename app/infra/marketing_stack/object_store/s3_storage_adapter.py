from typing import Optional
from loguru import logger
import boto3
from botocore.exceptions import ClientError

from app.core.marketing_stack.outbound.external.file_storage_port import FileStoragePort
from app.config.app_config import app_config


class S3StorageAdapter(FileStoragePort):
    """AWS S3 / Cloudflare R2 adapter implementing FileStoragePort."""

    def __init__(
        self,
        bucket_name: str = "",
        region: str = "",
        endpoint_url: str = "",
        access_key: str = "",
        secret_key: str = "",
    ):
        self._bucket = bucket_name or app_config.s3_bucket_name
        config = {
            "region_name": region or app_config.aws_region,
            "aws_access_key_id": access_key or app_config.aws_access_key_id,
            "aws_secret_access_key": secret_key or app_config.aws_secret_access_key,
        }
        endpoint = endpoint_url or app_config.s3_endpoint_url
        if endpoint:
            config["endpoint_url"] = endpoint

        self._client = boto3.client("s3", **config)

    async def upload(
        self,
        file_path: str,
        content: bytes,
        content_type: Optional[str] = None,
    ) -> str:
        extra_args = {}
        if content_type:
            extra_args["ContentType"] = content_type

        try:
            self._client.put_object(
                Bucket=self._bucket,
                Key=file_path,
                Body=content,
                **extra_args,
            )
            url = f"https://{self._bucket}.s3.amazonaws.com/{file_path}"
            logger.debug(f"Uploaded to S3: {file_path}")
            return url
        except ClientError as e:
            logger.error(f"S3 upload failed: {e}")
            raise

    async def generate_signed_url(
        self,
        file_path: str,
        expiry_seconds: int = 3600,
    ) -> str:
        try:
            url = self._client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self._bucket, "Key": file_path},
                ExpiresIn=expiry_seconds,
            )
            return url
        except ClientError as e:
            logger.error(f"S3 signed URL generation failed: {e}")
            raise

    async def download(self, file_path: str) -> bytes:
        try:
            response = self._client.get_object(Bucket=self._bucket, Key=file_path)
            return response["Body"].read()
        except ClientError as e:
            logger.error(f"S3 download failed: {e}")
            raise

    async def delete(self, file_path: str) -> bool:
        try:
            self._client.delete_object(Bucket=self._bucket, Key=file_path)
            logger.debug(f"Deleted from S3: {file_path}")
            return True
        except ClientError as e:
            logger.error(f"S3 delete failed: {e}")
            return False
