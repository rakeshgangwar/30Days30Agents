from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Create SQLAlchemy engine with optimized connection pool settings
engine = create_engine(
    str(settings.DATABASE_URL),
    pool_size=20,  # Increased from default of 5
    max_overflow=20,  # Increased from default of 10
    pool_timeout=60,  # Increased from default of 30
    pool_recycle=3600  # Recycle connections after 1 hour
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

def get_db():
    """Get a database session.

    This function creates a new database session for each request and ensures
    that the session is properly closed when the request is complete, even if
    an exception occurs.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create tables in the database."""
    Base.metadata.create_all(bind=engine)
