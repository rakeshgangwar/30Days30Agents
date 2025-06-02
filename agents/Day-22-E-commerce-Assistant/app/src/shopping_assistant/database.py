"""
Database configuration and ORM models
"""

from sqlalchemy import create_engine, Column, String, Float, DateTime, Boolean, Integer, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

# Database URL - defaults to SQLite for simplicity
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./shopping_assistant.db")

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class UserPreferencesDB(Base):
    """User preferences table"""
    __tablename__ = "user_preferences"
    
    user_id = Column(String, primary_key=True)
    preferred_brands = Column(JSON)
    preferred_categories = Column(JSON)
    price_range = Column(JSON)
    favorite_stores = Column(JSON)
    preferred_features = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PriceTrackerDB(Base):
    """Price tracking table"""
    __tablename__ = "price_trackers"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    product_url = Column(String, nullable=False)
    product_title = Column(String, nullable=False)
    target_price = Column(Float, nullable=False)
    current_price = Column(Float)
    last_checked = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)


class ProductCacheDB(Base):
    """Cached product information"""
    __tablename__ = "product_cache"
    
    id = Column(String, primary_key=True)
    url = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    price = Column(Float)
    currency = Column(String, default="USD")
    image_url = Column(String)
    rating = Column(Float)
    review_count = Column(Integer)
    description = Column(Text)
    features = Column(JSON)
    brand = Column(String)
    category = Column(String)
    availability = Column(String)
    source = Column(String, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SearchHistoryDB(Base):
    """Search history table"""
    __tablename__ = "search_history"
    
    id = Column(String, primary_key=True)
    user_id = Column(String)
    query = Column(String, nullable=False)
    query_type = Column(String, nullable=False)
    filters = Column(JSON)
    results_count = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)


def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_database():
    """Initialize the database"""
    create_tables()
    print("Database initialized successfully!") 