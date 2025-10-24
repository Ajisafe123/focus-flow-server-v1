import os
import logging
import traceback
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .database import init_db
from src.routers import auth_routes, prayer_routes, allah_names, calendar, qibla, zakat, hadith, duas
from src.services.prayer_service import get_prayer_times, DEFAULT_LAT, DEFAULT_LON

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI(
    title="Focus Flow API",
    description="Authentication + Prayer Times API (No Weather)",
    version="1.2.1",
    debug=(settings.ENVIRONMENT == "development"),
)

@app.middleware("http")
async def log_exceptions(request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        logging.error("UNCAUGHT EXCEPTION", exc_info=e)
        traceback.print_exc()
        raise e

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(__file__)
STATIC_DIR = os.path.join(BASE_DIR, "static")
UPLOAD_DIR = os.path.join(STATIC_DIR, "uploads")
AUDIO_DIR = os.path.join(STATIC_DIR, "audio")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.include_router(auth_routes.router)
app.include_router(prayer_routes.router)
app.include_router(allah_names.router)
app.include_router(zakat.router)
app.include_router(qibla.router)
app.include_router(calendar.router)
app.include_router(hadith.router)
app.include_router(duas.router)

@app.get("/")
async def read_root():
    return {"message": "Welcome to Focus Flow API (Prayer + Auth)"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.on_event("startup")
async def on_startup():
    logging.info("Starting Focus Flow API...")
    try:
        await init_db()
        data = await get_prayer_times(DEFAULT_LAT, DEFAULT_LON)
        logging.info(f"Preloaded next prayer: {data['next_prayer']['name']} at {data['next_prayer']['time']}")
    except Exception as e:
        logging.exception(f"Startup error: {e}")
    logging.info("API Startup complete.")

@app.on_event("shutdown")
async def on_shutdown():
    logging.info("Shutting down Focus Flow API...")
