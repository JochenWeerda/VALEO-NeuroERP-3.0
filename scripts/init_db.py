import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy import create_engine
from core.config import settings
from core.models.transaction import TransactionDB
from core.db.postgresql import Base
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_mongodb():
    """MongoDB initialisieren"""
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(settings.MONGODB_URI)
        db = client[settings.MONGODB_DATABASE]
        
        # Create indexes
        await db.users.create_index("email", unique=True)
        await db.documents.create_index("user_id")
        await db.workflows.create_index("user_id")
        
        logger.info("MongoDB erfolgreich initialisiert")
        
    except Exception as e:
        logger.error(f"Fehler bei MongoDB-Initialisierung: {str(e)}")
        raise

def init_postgresql():
    """PostgreSQL initialisieren"""
    try:
        # Create database URL
        db_url = (
            f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
            f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
        )
        
        # Create engine
        engine = create_engine(db_url)
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        
        logger.info("PostgreSQL erfolgreich initialisiert")
        
    except Exception as e:
        logger.error(f"Fehler bei PostgreSQL-Initialisierung: {str(e)}")
        raise

async def init_all():
    """Alle Datenbanken initialisieren"""
    try:
        # Initialize MongoDB
        await init_mongodb()
        
        # Initialize PostgreSQL
        init_postgresql()
        
        logger.info("Alle Datenbanken erfolgreich initialisiert")
        
    except Exception as e:
        logger.error(f"Fehler bei Datenbank-Initialisierung: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(init_all()) 