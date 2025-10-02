import subprocess
import logging
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy import create_engine, text
from core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def vacuum_postgresql():
    """PostgreSQL VACUUM durchführen"""
    try:
        # Create database URL
        db_url = (
            f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
            f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
        )
        
        # Create engine
        engine = create_engine(db_url)
        
        # Run VACUUM ANALYZE
        with engine.connect() as conn:
            conn.execute(text("VACUUM ANALYZE"))
            logger.info("PostgreSQL VACUUM ANALYZE erfolgreich durchgeführt")
            
    except Exception as e:
        logger.error(f"Fehler bei PostgreSQL VACUUM: {str(e)}")
        raise

async def cleanup_mongodb():
    """MongoDB-Bereinigung durchführen"""
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(settings.MONGODB_URI)
        db = client[settings.MONGODB_DATABASE]
        
        # Cleanup old logs (older than 30 days)
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        result = await db.logs.delete_many({"timestamp": {"$lt": cutoff_date}})
        logger.info(f"{result.deleted_count} alte Log-Einträge gelöscht")
        
        # Run compact on collections
        collections = await db.list_collection_names()
        for collection in collections:
            await db.command("compact", collection)
        logger.info("MongoDB Compact auf allen Collections durchgeführt")
        
    except Exception as e:
        logger.error(f"Fehler bei MongoDB-Bereinigung: {str(e)}")
        raise

def analyze_postgresql():
    """PostgreSQL-Analyse durchführen"""
    try:
        # Create database URL
        db_url = (
            f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
            f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
        )
        
        # Create engine
        engine = create_engine(db_url)
        
        # Run analysis queries
        with engine.connect() as conn:
            # Check table sizes
            result = conn.execute(text("""
                SELECT schemaname, relname, pg_size_pretty(pg_total_relation_size(relid))
                FROM pg_stat_user_tables
                ORDER BY pg_total_relation_size(relid) DESC;
            """))
            logger.info("Tabellengrößen:")
            for row in result:
                logger.info(f"{row[0]}.{row[1]}: {row[2]}")
            
            # Check index usage
            result = conn.execute(text("""
                SELECT schemaname, relname, 
                    idx_scan as index_scans,
                    seq_scan as sequential_scans,
                    idx_tup_fetch as tuples_fetched_by_index,
                    seq_tup_read as tuples_fetched_by_seqscan
                FROM pg_stat_user_tables
                ORDER BY idx_scan DESC;
            """))
            logger.info("\nIndex-Nutzung:")
            for row in result:
                logger.info(f"{row[0]}.{row[1]}: {row[2]} Index Scans, {row[3]} Sequential Scans")
            
    except Exception as e:
        logger.error(f"Fehler bei PostgreSQL-Analyse: {str(e)}")
        raise

async def analyze_mongodb():
    """MongoDB-Analyse durchführen"""
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(settings.MONGODB_URI)
        db = client[settings.MONGODB_DATABASE]
        
        # Get collection stats
        collections = await db.list_collection_names()
        for collection in collections:
            stats = await db.command("collStats", collection)
            logger.info(f"\nStatistik für Collection {collection}:")
            logger.info(f"Größe: {stats['size']} Bytes")
            logger.info(f"Dokumente: {stats['count']}")
            logger.info(f"Durchschnittliche Objektgröße: {stats['avgObjSize']} Bytes")
            
        # Get database stats
        db_stats = await db.command("dbStats")
        logger.info("\nDatenbank-Statistik:")
        logger.info(f"Gesamtgröße: {db_stats['dataSize']} Bytes")
        logger.info(f"Collections: {db_stats['collections']}")
        logger.info(f"Objekte: {db_stats['objects']}")
        
    except Exception as e:
        logger.error(f"Fehler bei MongoDB-Analyse: {str(e)}")
        raise

async def maintenance_all():
    """Alle Wartungsaufgaben durchführen"""
    try:
        # PostgreSQL maintenance
        vacuum_postgresql()
        analyze_postgresql()
        
        # MongoDB maintenance
        await cleanup_mongodb()
        await analyze_mongodb()
        
        logger.info("Alle Wartungsaufgaben erfolgreich durchgeführt")
        
    except Exception as e:
        logger.error(f"Fehler bei Wartungsaufgaben: {str(e)}")
        raise

if __name__ == "__main__":
    import asyncio
    asyncio.run(maintenance_all()) 