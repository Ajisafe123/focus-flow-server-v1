import os
from typing import Optional

def generate_s3_key(prefix: str, filename: str) -> str:
    raise RuntimeError("S3 support has been removed. Use Cloudinary instead.")

def upload_bytes_to_s3(data: bytes, filename: str, prefix: str = "uploads", content_type: str | None = None) -> str:
    raise RuntimeError("S3 support has been removed. Use Cloudinary instead.")

def generate_presigned_url(key: str, expires_in: int = 3600) -> str:
    raise RuntimeError("S3 support has been removed. Use Cloudinary instead.")
