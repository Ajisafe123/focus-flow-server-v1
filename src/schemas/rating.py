from pydantic import BaseModel
from uuid import UUID

class RatingCreate(BaseModel):
    conversationId: UUID
    rating: int
