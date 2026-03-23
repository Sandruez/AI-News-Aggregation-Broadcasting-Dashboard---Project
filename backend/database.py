import os
import logging
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from config import get_settings

# Set event loop policy for asyncpg compatibility
if os.name != 'nt':  # Not Windows
    try:
        asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
    except Exception:
        pass

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
    """Initialize the database engine if not already done"""
    global engine, AsyncSessionLocal
    
    if engine is not None:
        return engine
    
    db_url = get_db_url()
    if not db_url:
        logger.warning("No database URL provided")
        return None
    
    try:
        # Create engine with proper asyncpg settings
        engine = create_async_engine(
            db_url,
            echo=settings.debug,
            pool_pre_ping=True,
            pool_recycle=300,
            connect_args={
                "command_timeout": 60,
                "server_settings": {
                    "application_name": "ai_news_dashboard",
                    "timezone": "UTC"
                }
            }
        )
        AsyncSessionLocal = async_sessionmaker(
            engine, 
            class_=AsyncSession, 
            expire_on_commit=False
        )
        logger.info("Database engine initialized successfully")
        return engine
    except Exception as e:
        logger.error(f"Failed to initialize database engine: {e}")
        engine = None
        AsyncSessionLocal = None
        return None


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
