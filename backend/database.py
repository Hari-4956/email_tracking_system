from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from backend.config import get_settings


settings = get_settings()


# =========================================================
# DATABASE ENGINE
# =========================================================

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_recycle=settings.DB_POOL_RECYCLE,
)


# =========================================================
# SESSION
# =========================================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# =========================================================
# BASE
# =========================================================

Base = declarative_base()


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

def init_db():
    """
    Create database tables if they do not already exist.

    This does NOT delete existing tables or data.
    """

    # Import models here so SQLAlchemy registers
    # Campaign, Recipient, and EmailEvent with Base.metadata.
    from backend import models

    Base.metadata.create_all(bind=engine)


# =========================================================
# DATABASE SESSION DEPENDENCY
# =========================================================

def get_db():
    """
    Yield a DB session and always close it afterward.
    """

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()
