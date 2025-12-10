from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        try:
            return ObjectId(str(v))
        except Exception:
            raise ValueError("Invalid ObjectId")


class MongoModel(BaseModel):
    id: PyObjectId = Field(alias="_id")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class TeachingCategory(BaseModel):
    name: str
    description: Optional[str] = ""
    image_url: Optional[str] = None
    slug: Optional[str] = None

    class Config:
        from_attributes = True


class LessonBase(BaseModel):
    title: str
    description: Optional[str] = ""
    category: Optional[str] = None
    level: Optional[str] = None
    duration: Optional[str] = None
    thumbnail: Optional[str] = None
    resource_url: Optional[str] = None


class LessonCreate(LessonBase):
    pass


class LessonUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    level: Optional[str] = None
    duration: Optional[str] = None
    thumbnail: Optional[str] = None
    resource_url: Optional[str] = None


class LessonRead(LessonBase, MongoModel):
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class StudyGuideBase(BaseModel):
    title: str
    summary: Optional[str] = ""
    category: Optional[str] = None
    difficulty: Optional[str] = None
    pages: Optional[int] = None
    duration: Optional[str] = None
    thumbnail: Optional[str] = None
    download_url: Optional[str] = None


class StudyGuideCreate(StudyGuideBase):
    pass


class StudyGuideUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    category: Optional[str] = None
    difficulty: Optional[str] = None
    pages: Optional[int] = None
    duration: Optional[str] = None
    thumbnail: Optional[str] = None
    download_url: Optional[str] = None


class StudyGuideRead(StudyGuideBase, MongoModel):
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class TeachingResourceBase(BaseModel):
    title: str
    description: Optional[str] = ""
    category: Optional[str] = None
    type: Optional[str] = None  # worksheet, template, tool
    thumbnail: Optional[str] = None
    file_url: Optional[str] = None


class TeachingResourceCreate(TeachingResourceBase):
    pass


class TeachingResourceUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    type: Optional[str] = None
    thumbnail: Optional[str] = None
    file_url: Optional[str] = None


class TeachingResourceRead(TeachingResourceBase, MongoModel):
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

