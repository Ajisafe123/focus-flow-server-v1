import os
from uuid import uuid4
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..config import settings
from src.models.files import File as FileModel
from src.utils.s3_clients import upload_bytes_to_s3, generate_presigned_url

router = APIRouter(prefix="/api/files", tags=["Files"])

MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", settings.__dict__.get("MAX_UPLOAD_SIZE", 10 * 1024 * 1024)))


@router.post("/upload")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    conversationId: Optional[str] = Form(None),
    messageId: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    contents = await file.read()
    size = len(contents)
    if size == 0:
        raise HTTPException(status_code=400, detail="Empty file")
    if size > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail=f"File too large (max {MAX_UPLOAD_SIZE} bytes)")

    filename = file.filename or f"upload-{uuid4().hex}"
    content_type = file.content_type or "application/octet-stream"

    if settings.USE_S3:
        try:
            key = upload_bytes_to_s3(contents, filename, prefix="uploads", content_type=content_type)
            presigned_url = generate_presigned_url(key, expires_in=60 * 60 * 24)
            file_url = presigned_url
            s3_key = key
        except Exception as e:
            raise HTTPException(status_code=500, detail="S3 upload failed")
    else:
        upload_dir = settings.FILE_UPLOAD_DIR
        os.makedirs(upload_dir, exist_ok=True)
        save_name = f"{uuid4().hex}_{filename}"
        path = os.path.join(upload_dir, save_name)
        with open(path, "wb") as f:
            f.write(contents)
        file_url = f"/files/{save_name}"
        s3_key = None

    file_record = FileModel(
        message_id=messageId,
        file_name=filename,
        file_type=content_type,
        file_size=size,
        file_url=file_url,
        uploaded_at=datetime.utcnow()
    )
    db.add(file_record)
    await db.commit()
    await db.refresh(file_record)

    return {"fileUrl": file_url, "fileId": str(file_record.id), "s3_key": s3_key}
