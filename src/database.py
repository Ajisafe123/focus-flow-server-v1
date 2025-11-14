from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from src.config import settings
import ssl

DATABASE_URL = settings.effective_database_url.strip()

if "sslmode" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.split("?")[0]

connect_args = {"server_settings": {"client_encoding": "utf8"}}
if "render.com" in DATABASE_URL:
    ssl_context = ssl.create_default_context()
    connect_args["ssl"] = ssl_context

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=10,
    max_overflow=5,
    pool_timeout=30,
    connect_args=connect_args,
)

async_session_maker = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()

async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        yield session

async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)