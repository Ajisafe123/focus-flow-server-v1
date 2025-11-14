import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection

# Import all your models here
from src.database import Base
from src.config import settings

# Models
from src.models.allah_names import AllahName
from src.models.hadith import Hadith
from src.models.dua import Dua, DuaView, DuaFavorite, DuaCategory
from src.models.users import User, PasswordResetCode, ChatUser

# Alembic Config
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# This tells Alembic what to use for autogeneration
target_metadata = Base.metadata

def get_url():
    return settings.DATABASE_URL

# Offline migrations
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

# Synchronous migration runner
def do_run_migrations(connection: Connection) -> None:
    """Run migrations synchronously within a connection."""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

# Async migration runner
async def run_async_migrations() -> None:
    """Run migrations in async mode."""
    from sqlalchemy.ext.asyncio import create_async_engine

    connectable = create_async_engine(get_url(), poolclass=pool.NullPool)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

# Online migrations
def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())

# Entrypoint
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
