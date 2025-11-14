import os
import mimetypes
from uuid import uuid4
from botocore.exceptions import ClientError
import boto3
from datetime import datetime
from ..config import settings

s3_client = None
if settings.USE_S3:
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )

def generate_s3_key(prefix: str, filename: str) -> str:
    ext = os.path.splitext(filename)[1]
    unique = uuid4().hex
    date = datetime.utcnow().strftime("%Y/%m/%d")
    key = f"{prefix}/{date}/{unique}{ext}"
    return key

def upload_bytes_to_s3(data: bytes, filename: str, prefix: str = "uploads", content_type: str | None = None) -> str:
    if not settings.USE_S3 or s3_client is None:
        raise RuntimeError("S3 disabled or client not configured")

    key = generate_s3_key(prefix, filename)
    if content_type is None:
        content_type, _ = mimetypes.guess_type(filename)
        if content_type is None:
            content_type = "application/octet-stream"

    try:
        s3_client.put_object(
            Bucket=settings.AWS_S3_BUCKET,
            Key=key,
            Body=data,
            ContentType=content_type,
            ACL="private",
        )
    except ClientError as exc:
        raise

    return key

def generate_presigned_url(key: str, expires_in: int = 3600) -> str:
    if not settings.USE_S3 or s3_client is None:
        raise RuntimeError("S3 disabled or client not configured")
    try:
        url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.AWS_S3_BUCKET, "Key": key},
            ExpiresIn=expires_in,
        )
        return url
    except ClientError as exc:
        raise
