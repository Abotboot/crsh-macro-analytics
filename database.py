"""
Database models and setup for analytics
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Database setup
DATABASE_URL = "sqlite:///./analytics.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    """User model - tracks unique users"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True)  # Discord ID or anonymous ID
    username = Column(String, nullable=True)  # Discord username
    avatar_hash = Column(String, nullable=True)  # Discord avatar hash
    discriminator = Column(String, nullable=True)  # Discord discriminator (legacy)
    country = Column(String, nullable=True)  # Country code (US, UK, etc.)
    city = Column(String, nullable=True)  # City name
    latitude = Column(Float, nullable=True)  # Latitude
    longitude = Column(Float, nullable=True)  # Longitude
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    total_sessions = Column(Integer, default=0, nullable=False)  # Number of times exe launched
    total_hours = Column(Float, default=0.0, nullable=False)
    total_macros_created = Column(Integer, default=0, nullable=False)  # Total macros created
    total_macros_played = Column(Integer, default=0, nullable=False)  # Total macros played
    app_version = Column(String, nullable=True)

class Session(Base):
    """Session model - tracks individual app sessions"""
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    session_id = Column(String, unique=True, index=True)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    duration_minutes = Column(Float, default=0.0)
    app_version = Column(String, nullable=True)
    
class Event(Base):
    """Event model - tracks specific actions/events"""
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    session_id = Column(String, index=True)
    event_type = Column(String, index=True)  # e.g., "macro_recorded", "macro_played", "app_opened"
    event_data = Column(String, nullable=True)  # JSON string for additional data
    timestamp = Column(DateTime, default=datetime.utcnow)

class DailyStat(Base):
    """Daily statistics - aggregated daily data for faster queries"""
    __tablename__ = "daily_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, unique=True, index=True)
    unique_users = Column(Integer, default=0)
    total_sessions = Column(Integer, default=0)
    total_hours = Column(Float, default=0.0)
    new_users = Column(Integer, default=0)

# Create all tables
def init_db():
    """Initialize database"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
