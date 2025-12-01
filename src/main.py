import os
import logging
import traceback
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.routers import users
from .config import settings
from . import database
from .database import init_db
from src.routers import (
    prayer_routes,
    allah_names,
    calendar,
    qibla,
    zakat,
    hadith,
    duas,
    articles,
    contact,
    users,
    admin,
    conversation,
    messages,
    files,
    ratings,
    quran,
    websocket_routes,
)
from src.services.prayer_service import get_prayer_times, DEFAULT_LAT, DEFAULT_LON
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
app = FastAPI(
    title="Focus Flow API",
    description="Authentication + Prayer Times API (No Weather)",
    version="1.2.1",
    debug=(settings.ENVIRONMENT == "development"),
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://nibrasudeen.vercel.app",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.middleware("http")
async def log_exceptions(request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        logging.error("UNCAUGHT EXCEPTION", exc_info=e)
        traceback.print_exc()
        raise e
BASE_DIR = os.path.dirname(__file__)
STATIC_DIR = os.path.join(BASE_DIR, "static")
UPLOAD_DIR = os.path.join(STATIC_DIR, "uploads")
AUDIO_DIR = os.path.join(STATIC_DIR, "audio")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.include_router(users.router)
app.include_router(prayer_routes.router)
app.include_router(allah_names.router)
app.include_router(zakat.router)
app.include_router(qibla.router)
app.include_router(calendar.router)
app.include_router(hadith.router)
app.include_router(duas.router)
app.include_router(articles.router)
app.include_router(contact.router)
app.include_router(admin.router)
app.include_router(conversation.router)
app.include_router(messages.router)
app.include_router(files.router)
app.include_router(ratings.router)
app.include_router(quran.router)
app.include_router(websocket_routes.router)

@app.get("/")
async def read_root():
    return {"message": "Welcome to Focus Flow API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.on_event("startup")
async def on_startup():
    logging.info("Starting Focus Flow API...")
    logging.info(f"Environment: {settings.ENVIRONMENT}")
    logging.info(f"Database URL: {settings.DATABASE_URL}")
    try:
        await database.connect_to_mongo()
        await database.init_db()
        data = await get_prayer_times(DEFAULT_LAT, DEFAULT_LON)
        logging.info(f"Preloaded next prayer: {data['next_prayer']['name']} at {data['next_prayer']['time']}")
    except Exception as e:
        logging.exception(f"Startup error: {e}")
    logging.info("API Startup complete.")

@app.on_event("shutdown")
async def on_shutdown():
    logging.info("Shutting down Focus Flow API...")
    await database.disconnect_from_mongo()

def silence_asyncio_connection_reset(loop, context):
    """Prevents noisy ConnectionResetError logs on Windows."""
    if "exception" in context and isinstance(context["exception"], ConnectionResetError):
        return
    loop.default_exception_handler(context)
try:
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(silence_asyncio_connection_reset)
except Exception as e:
    logging.warning(f"Failed to set asyncio exception handler: {e}")
