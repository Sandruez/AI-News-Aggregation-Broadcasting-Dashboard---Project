import os
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

def get_db_url():
    url = settings.database_url
    if not url:
        return None
    # Fix for Heroku/Render/Railway postgres:// vs postgresql://
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    # Ensure asyncpg driver is used
    if "postgresql" in url and "asyncpg" not in url:
        url = url.replace("postgresql", "postgresql+asyncpg", 1)
        
    return url

# Don't create engine immediately to prevent startup failures
engine = None
AsyncSessionLocal = None

def init_engine():
    global engine, AsyncSessionLocal
    if engine is None:
        db_url = get_db_url()
        if not db_url:
            return
        try:
            connect_args = {}
            if "postgresql" in db_url:
                # SSL is often required for hosted databases
                connect_args["ssl"] = "require"

            engine = create_async_engine(
                db_url,
                echo=False,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20,
                connect_args=connect_args if "ssl" in connect_args else {}
            )
            AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
        except Exception:
            pass  # Engine creation failed, will retry later


class Base(DeclarativeBase):
    pass


async def init_db():
    init_engine()  # Try to initialize engine first
    if engine is None:
        logger.error("Cannot initialize DB: Engine is None")
        return
    
    import asyncio
    from models import Source, NewsItem, Favorite, BroadcastLog, User  # noqa
    
    # Retry database connection with exponential backoff
    max_retries = 5
    retry_delay = 2
    
    logger.info("Starting database table creation (if not exists)...")
    for attempt in range(max_retries):
        try:
            # Use sync connection for table creation
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables verified/created successfully")
            return
        except Exception as e:
            logger.warning(f"Database connection attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                logger.error("Max retries reached. Database initialization failed.")
                return
            await asyncio.sleep(retry_delay)
            retry_delay *= 2


async def get_db():
    init_engine()  # Ensure engine is initialized
    if AsyncSessionLocal is None:
        # Database not available, return None
        yield None
        return
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
            # Don't auto-commit here, let the endpoints handle it
            # or use session.commit() explicitly in the endpoint
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
