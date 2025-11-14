from pydantic import BaseModel

class AllahNameSchema(BaseModel):
    id: int
    arabic: str
    transliteration: str
    meaning: str

    class Config:
        from_attributes = True