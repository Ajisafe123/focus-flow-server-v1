from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from bson import ObjectId
from datetime import datetime
from ..database import get_db
from ..utils.users import get_current_user
from ..schemas.teaching import (
    TeachingCategory,
    LessonCreate,
    LessonUpdate,
    LessonRead,
    StudyGuideCreate,
    StudyGuideUpdate,
    StudyGuideRead,
    TeachingResourceCreate,
    TeachingResourceUpdate,
    TeachingResourceRead,
)

router = APIRouter(prefix="/api", tags=["Teaching"])


def serialize_category(doc):
    return {
        "id": str(doc.get("_id")),
        "name": doc.get("name", "Untitled"),
        "description": doc.get("description", "") or "",
        "image_url": doc.get("image_url"),
        "slug": doc.get("slug"),
    }


def serialize_doc(doc):
    doc["_id"] = str(doc.get("_id"))
    return doc


def admin_required(user: dict):
    if not user or user.get("role", "").lower() != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")


@router.get("/teaching-categories")
async def list_teaching_categories(db: AsyncIOMotorDatabase = Depends(get_db)) -> List[dict]:
    """
    Return teaching categories for landing/navigation.
    Falls back to an empty list if none exist.
    """
    cursor = db["teaching_categories"].find({}, {"name": 1, "description": 1, "image_url": 1, "slug": 1})
    categories = [serialize_category(doc) async for doc in cursor]
    return categories


@router.get("/teaching-categories/{category_id}")
async def get_teaching_category(category_id: str, db: AsyncIOMotorDatabase = Depends(get_db)) -> dict:
    filter_id = category_id
    try:
        filter_id = ObjectId(category_id)
    except Exception:
        pass
    doc = await db["teaching_categories"].find_one({"_id": filter_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Teaching category not found")
    return serialize_category(doc)


# -------------------- Lessons --------------------
@router.get("/lessons", response_model=None)
async def list_lessons(
    db: AsyncIOMotorDatabase = Depends(get_db),
    category: str = None,
    level: str = None,
):
    query = {}
    if category:
        query["category"] = category
    if level:
        query["level"] = level
    cursor = db["lessons"].find(query).sort("created_at", -1)
    docs = await cursor.to_list(length=None)
    return [LessonRead(**serialize_doc(d)) for d in docs]


@router.post("/lessons", response_model=None)
async def create_lesson(
    payload: LessonCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    admin_required(current_user)
    data = payload.model_dump()
    data["created_at"] = datetime.utcnow().isoformat()
    data["updated_at"] = datetime.utcnow().isoformat()
    res = await db["lessons"].insert_one(data)
    doc = await db["lessons"].find_one({"_id": res.inserted_id})
    return LessonRead(**serialize_doc(doc))


@router.patch("/lessons/{lesson_id}", response_model=None)
async def update_lesson(
    lesson_id: str,
    payload: LessonUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    admin_required(current_user)
    try:
        lid = ObjectId(lesson_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid lesson id")
    update = {k: v for k, v in payload.model_dump(exclude_unset=True).items()}
    update["updated_at"] = datetime.utcnow().isoformat()
    res = await db["lessons"].update_one({"_id": lid}, {"$set": update})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Lesson not found")
    doc = await db["lessons"].find_one({"_id": lid})
    return LessonRead(**serialize_doc(doc))


@router.delete("/lessons/{lesson_id}", response_model=None)
async def delete_lesson(
    lesson_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    admin_required(current_user)
    try:
        lid = ObjectId(lesson_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid lesson id")
    res = await db["lessons"].delete_one({"_id": lid})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return {"ok": True}


# -------------------- Study Guides --------------------
@router.get("/study-guides", response_model=None)
async def list_study_guides(
    db: AsyncIOMotorDatabase = Depends(get_db),
    category: str = None,
    difficulty: str = None,
):
    query = {}
    if category:
        query["category"] = category
    if difficulty:
        query["difficulty"] = difficulty
    cursor = db["study_guides"].find(query).sort("created_at", -1)
    docs = await cursor.to_list(length=None)
    return [StudyGuideRead(**serialize_doc(d)) for d in docs]


@router.post("/study-guides", response_model=None)
async def create_study_guide(
    payload: StudyGuideCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    admin_required(current_user)
    data = payload.model_dump()
    data["created_at"] = datetime.utcnow().isoformat()
    data["updated_at"] = datetime.utcnow().isoformat()
    res = await db["study_guides"].insert_one(data)
    doc = await db["study_guides"].find_one({"_id": res.inserted_id})
    return StudyGuideRead(**serialize_doc(doc))


@router.patch("/study-guides/{guide_id}", response_model=None)
async def update_study_guide(
    guide_id: str,
    payload: StudyGuideUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    admin_required(current_user)
    try:
        gid = ObjectId(guide_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid guide id")
    update = {k: v for k, v in payload.model_dump(exclude_unset=True).items()}
    update["updated_at"] = datetime.utcnow().isoformat()
    res = await db["study_guides"].update_one({"_id": gid}, {"$set": update})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Study guide not found")
    doc = await db["study_guides"].find_one({"_id": gid})
    return StudyGuideRead(**serialize_doc(doc))


@router.delete("/study-guides/{guide_id}", response_model=None)
async def delete_study_guide(
    guide_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    admin_required(current_user)
    try:
        gid = ObjectId(guide_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid guide id")
    res = await db["study_guides"].delete_one({"_id": gid})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Study guide not found")
    return {"ok": True}


# -------------------- Teaching Resources --------------------
@router.get("/teaching-resources", response_model=None)
async def list_teaching_resources(
    db: AsyncIOMotorDatabase = Depends(get_db),
    category: str = None,
    type: str = None,
):
    query = {}
    if category:
        query["category"] = category
    if type:
        query["type"] = type
    cursor = db["teaching_resources"].find(query).sort("created_at", -1)
    docs = await cursor.to_list(length=None)
    return [TeachingResourceRead(**serialize_doc(d)) for d in docs]


@router.post("/teaching-resources", response_model=None)
async def create_teaching_resource(
    payload: TeachingResourceCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    admin_required(current_user)
    data = payload.model_dump()
    data["created_at"] = datetime.utcnow().isoformat()
    data["updated_at"] = datetime.utcnow().isoformat()
    res = await db["teaching_resources"].insert_one(data)
    doc = await db["teaching_resources"].find_one({"_id": res.inserted_id})
    return TeachingResourceRead(**serialize_doc(doc))


@router.patch("/teaching-resources/{resource_id}", response_model=None)
async def update_teaching_resource(
    resource_id: str,
    payload: TeachingResourceUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    admin_required(current_user)
    try:
        rid = ObjectId(resource_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid resource id")
    update = {k: v for k, v in payload.model_dump(exclude_unset=True).items()}
    update["updated_at"] = datetime.utcnow().isoformat()
    res = await db["teaching_resources"].update_one({"_id": rid}, {"$set": update})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Teaching resource not found")
    doc = await db["teaching_resources"].find_one({"_id": rid})
    return TeachingResourceRead(**serialize_doc(doc))


@router.delete("/teaching-resources/{resource_id}", response_model=None)
async def delete_teaching_resource(
    resource_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    admin_required(current_user)
    try:
        rid = ObjectId(resource_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid resource id")
    res = await db["teaching_resources"].delete_one({"_id": rid})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Teaching resource not found")
    return {"ok": True}

