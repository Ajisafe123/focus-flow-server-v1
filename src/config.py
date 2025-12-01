from pathlib import Path
from typing import List, Dict, Union, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    DATABASE_URL: str  # MongoDB connection string
    MONGODB_DB_NAME: str = "focus_flow"
    ENVIRONMENT: str
    SECRET_KEY: str
    JWT_SECRET: Optional[str] = None
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    RESET_TOKEN_EXPIRE_MINUTES: int
    PORT: int = 3001
    BACKEND_CORS_ORIGINS: List[str]
    FILE_UPLOAD_DIR: str = "./static./uploads"
    AUDIO_STORAGE_PATH: Path = Field(BASE_DIR / "static" / "audio", env="AUDIO_STORAGE_PATH")
    USE_S3: bool = False
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_S3_BUCKET: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    RESEND_API_KEY: str
    EMAIL_FROM: str
    DEFAULT_LAT: float = 21.3891
    DEFAULT_LON: float = 39.8579
    DEFAULT_CITY: str = "Mecca"
    DEFAULT_RECITERS: List[str] = ["sudais", "alafasy"]
    CALC_METHODS: List[str] = ["MWL", "ISNA", "Egypt", "Makkah", "Karachi"]
    MAJOR_CITIES: List[Dict[str, Union[str, float]]] = [
        {"name": "Mecca", "lat": 21.3891, "lon": 39.8579},
        {"name": "Medina", "lat": 24.4700, "lon": 39.6111},
        {"name": "Cairo", "lat": 30.0444, "lon": 31.2357},
        {"name": "Istanbul", "lat": 41.0082, "lon": 28.9784},
        {"name": "Jakarta", "lat": -6.2088, "lon": 106.8456},
        {"name": "Karachi", "lat": 24.8607, "lon": 67.0011},
        {"name": "London", "lat": 51.5074, "lon": -0.1278},
        {"name": "New York", "lat": 40.7128, "lon": -74.0060},
    ]

settings = Settings()
