import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

def get_db_url():
    url = settings.database_url
    if not url:
        return None
    # Fix for Heroku/Render/Railway postgres:// vs postgresql://
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg://", 1)
    elif url.startswith("postgresql://") and "psycopg" not in url:
        url = url.replace("postgresql", "postgresql+psycopg", 1)
        
    return url

# Don't create engine immediately to prevent startup failures
engine = None
SessionLocal = None

def init_engine():
    """Initialize the database engine if not already done"""
    global engine, SessionLocal
    
    if engine is not None:
        return engine
    
    db_url = get_db_url()
    if not db_url:
        logger.warning("No database URL provided")
        return None
    
    try:
        # Create sync engine with psycopg settings
        engine = create_engine(
            db_url,
            echo=settings.debug,
            pool_recycle=300,
            connect_args={
                "sslmode": "require",
                "connect_timeout": 60
            }
        )
        SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        )
        logger.info("Database engine initialized successfully with sync psycopg")
        return engine
    except Exception as e:
        logger.error(f"Failed to initialize database engine: {e}")
        engine = None
        SessionLocal = None
        return None


class Base(DeclarativeBase):
    pass


def init_db():
    """Initialize database tables"""
    init_engine()  # Try to initialize engine first
    if engine is None:
        logger.error("Cannot initialize DB: Engine is None")
        return
    
    from models import Source, NewsItem, Favorite, BroadcastLog, User  # noqa
    
    # Retry database connection with exponential backoff
    max_retries = 5
    retry_delay = 2
    
    logger.info("Starting database table creation (if not exists)...")
    for attempt in range(max_retries):
        try:
            # Create tables directly
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables verified/created successfully")
            return
        except Exception as e:
            logger.warning(f"Database connection attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                logger.error("Max retries reached. Database initialization failed.")
                return
            import time
            time.sleep(retry_delay)
            retry_delay *= 2


def get_db():
    """Get database session"""
    init_engine()  # Ensure engine is initialized
    if SessionLocal is None:
        # Database not available, yield None
        yield None
        return
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
