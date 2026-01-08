import asyncio
from io import BytesIO
from typing import Any, Dict, Optional

from ..config import settings


def _get_cloudinary():
    try:
        import cloudinary
        import cloudinary.uploader
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Cloudinary dependency is not installed. Install dependencies (e.g. pip install -r requirements.txt)."
        ) from exc
    return cloudinary


def _is_configured() -> bool:
    return bool(
        getattr(settings, "CLOUDINARY_CLOUD_NAME", None)
        and getattr(settings, "CLOUDINARY_API_KEY", None)
        and getattr(settings, "CLOUDINARY_API_SECRET", None)
    )


def _configure() -> None:
    if not _is_configured():
        raise RuntimeError("Cloudinary is not configured")

    cloudinary = _get_cloudinary()

    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True,
    )


async def upload_bytes(
    *,
    contents: bytes,
    filename: str,
    folder: str,
    resource_type: str = "auto",
    content_type: Optional[str] = None,
) -> Dict[str, Any]:
    _configure()

    cloudinary = _get_cloudinary()

    data = BytesIO(contents)
    data.name = filename

    options: Dict[str, Any] = {
        "folder": folder,
        "resource_type": resource_type,
        "use_filename": True,
        "unique_filename": True,
        "overwrite": False,
    }

    if content_type:
        options["type"] = "upload"

    result = await asyncio.to_thread(cloudinary.uploader.upload, data, **options)
    return result
