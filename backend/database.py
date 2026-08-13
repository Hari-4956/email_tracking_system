from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from backend.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_recycle=settings.DB_POOL_RECYCLE,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db():
    """Yield a DB session and always close it afterward."""
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all database tables if they do not already exist."""
    # Import models here so SQLAlchemy registers all tables
    from backend.models import Campaign, Recipient, EmailEvent

    Base.metadata.create_all(bind=engine)