from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from src.config import settings

DATABASE_URL = settings.effective_database_url

if "ssl=require" not in DATABASE_URL:
    if "?" in DATABASE_URL:
        DATABASE_URL += "&ssl=require"
    else:
        DATABASE_URL += "?ssl=require"

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=5,
    pool_timeout=30,
    connect_args={
        "server_settings": {
            "client_encoding": "utf8"
        }
    },
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
