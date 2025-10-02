import subprocess
import logging
from core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_alembic_migrations():
    """Alembic-Migrationen ausführen"""
    try:
        # Run migrations
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        logger.info("Alembic-Migrationen erfolgreich ausgeführt")
        
    except Exception as e:
        logger.error(f"Fehler bei Alembic-Migrationen: {str(e)}")
        raise

def create_new_migration(message):
    """Neue Alembic-Migration erstellen"""
    try:
        # Create new migration
        subprocess.run(["alembic", "revision", "--autogenerate", "-m", message], check=True)
        logger.info(f"Neue Migration erstellt: {message}")
        
    except Exception as e:
        logger.error(f"Fehler beim Erstellen der Migration: {str(e)}")
        raise

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", choices=["upgrade", "create"], required=True)
    parser.add_argument("--message", help="Migration message for create action")
    
    args = parser.parse_args()
    
    if args.action == "upgrade":
        run_alembic_migrations()
    else:
        if not args.message:
            parser.error("Migration message muss für create angegeben werden")
        create_new_migration(args.message) 