from fastapi import APIRouter
from src.schemas.qibla import QiblaRequest, QiblaOut
from src.services.qibla_service import calculate_qibla

router = APIRouter(prefix="/qibla", tags=["Qibla"])

@router.post("/", response_model=QiblaOut)
def qibla_find(req: QiblaRequest):
    bearing, distance = calculate_qibla(req.latitude, req.longitude)
    return {"bearing": round(bearing, 3), "distance_km": round(distance, 3)}
