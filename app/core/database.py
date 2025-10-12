"""
VALEO-NeuroERP Database Connection and Setup
PostgreSQL database connection with SQLAlchemy
"""

import logging
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

from app.core.config import settings

logger = logging.getLogger(__name__)

# SQLAlchemy setup for PostgreSQL
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,  # Better for PostgreSQL
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=3600,
    echo=settings.DEBUG,  # SQL query logging in debug mode
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db() -> Session:
    """
    Dependency to get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """
    Create all database tables
    """
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise

def reset_database():
    """
    Drop all tables and recreate them (for development/testing)
    """
    try:
        logger.warning("Resetting database - dropping all tables...")
        Base.metadata.drop_all(bind=engine)
        logger.info("All tables dropped successfully")
        create_tables()
    except Exception as e:
        logger.error(f"Failed to reset database: {e}")
        raise

def init_db():
    """
    Initialize database with sample data
    """
    try:
        logger.info("Initializing database with sample data...")

        # Use SQLAlchemy session for data seeding
        db = SessionLocal()

        # Sample data will be inserted via Alembic migrations
        # This function can be used for additional runtime initialization if needed

        db.close()
        logger.info("Database initialization completed")

    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
