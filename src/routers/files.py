import os
from uuid import uuid4
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, BackgroundTasks
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..database import get_db
from ..config import settings
from ..utils.cloudinary_uploader import upload_bytes

router = APIRouter(prefix="/api/files", tags=["Files"])

MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", settings.__dict__.get("MAX_UPLOAD_SIZE", 10 * 1024 * 1024)))


@router.post("/upload", response_model=None)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    conversationId: Optional[str] = Form(None),
    messageId: Optional[str] = Form(None),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    contents = await file.read()
    size = len(contents)
    if size == 0:
        raise HTTPException(status_code=400, detail="Empty file")
    if size > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail=f"File too large (max {MAX_UPLOAD_SIZE} bytes)")

    filename = file.filename or f"upload-{uuid4().hex}"
    content_type = file.content_type or "application/octet-stream"

    try:
        result = await upload_bytes(
            contents=contents,
            filename=filename,
            folder="uploads",
            resource_type="auto",
            content_type=content_type,
        )
        file_url = result.get("secure_url") or result.get("url")
        if not file_url:
            raise RuntimeError("Cloudinary did not return a URL")
        cloudinary_public_id = result.get("public_id")
    except Exception:
        raise HTTPException(status_code=500, detail="Cloudinary upload failed")

    file_record = {
        "message_id": messageId,
        "file_name": filename,
        "file_type": content_type,
        "file_size": size,
        "file_url": file_url,
        "cloudinary_public_id": cloudinary_public_id,
        "uploaded_at": datetime.utcnow().isoformat()
    }
    
    files_collection = db["files"]
    result = await files_collection.insert_one(file_record)

    return {"fileUrl": file_url, "fileId": str(result.inserted_id), "cloudinary_public_id": cloudinary_public_id}
