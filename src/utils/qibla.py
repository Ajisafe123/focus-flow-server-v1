from ..schemas.qibla import QiblaRequest
from ..services.qibla_service import calculate_qibla

def get_qibla_direction(req: QiblaRequest):
    bearing, distance = calculate_qibla(req.latitude, req.longitude)
    return {"bearing": round(bearing, 3), "distance_km": round(distance, 3)}
