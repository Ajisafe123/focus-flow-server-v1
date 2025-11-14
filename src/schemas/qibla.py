from pydantic import BaseModel
from typing import Optional

class QiblaRequest(BaseModel):
    latitude: float
    longitude: float

class QiblaOut(BaseModel):
    bearing: float
    distance_km: Optional[float]
