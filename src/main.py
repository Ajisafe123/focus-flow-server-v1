import os
import logging
import traceback
import asyncio
import json
from json import JSONEncoder
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from bson import ObjectId

from .config import settings
from . import database
from .database import init_db


class CustomJSONEncoder(JSONEncoder):
    """Custom JSON encoder that handles ObjectId serialization"""
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super().default(o)


class CustomJSONResponse(JSONResponse):
    """Custom JSON response that uses our ObjectId-aware encoder"""
    def render(self, content):
        return json.dumps(content, cls=CustomJSONEncoder, ensure_ascii=False).encode("utf-8")
from src.routers import (
    prayer_routes,
    allah_names,
    calendar,
    qibla,
    hadith,
    duas,
    articles,
    teaching,
    contact,
    users,
    admin,
    conversation,
    messages,
    files,
    ratings,
    quran,
    websocket_routes,
    notifications,
    notification_ws,
    notification_ws,
    media,
    shop,
    donations,
)
from src.services.prayer_service import get_prayer_times, DEFAULT_LAT, DEFAULT_LON
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI(
    title="Focus Flow API",
    description="Authentication + Prayer Times API (No Weather)",
    version="1.2.1",
    debug=(settings.ENVIRONMENT == "development"),
    default_response_class=CustomJSONResponse,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
app.include_router(users.router)
app.include_router(prayer_routes.router)
app.include_router(allah_names.router)
app.include_router(qibla.router)
app.include_router(calendar.router)
app.include_router(hadith.router)
app.include_router(duas.router)
app.include_router(articles.router)
app.include_router(teaching.router)
app.include_router(contact.router)
app.include_router(admin.router)
app.include_router(conversation.router)
app.include_router(messages.router)
app.include_router(files.router)
app.include_router(ratings.router)
app.include_router(quran.router)
app.include_router(websocket_routes.router)
app.include_router(notifications.router)
app.include_router(notification_ws.router)
app.include_router(media.router)
app.include_router(shop.router)
app.include_router(donations.router)

@app.get("/")
async def read_root():
    return {"message": "Welcome to Focus Flow API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Legacy alias for frontend expecting /api/day
@app.get("/api/day")
async def alias_day():
    return await calendar.get_today()

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
