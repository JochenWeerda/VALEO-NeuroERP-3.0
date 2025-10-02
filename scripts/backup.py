#!/usr/bin/env python3

import asyncio
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import subprocess
from core.config import settings

# Logger konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseBackup:
    """Klasse für Datenbank-Backups."""
    
    def __init__(self):
        """Initialisiert den Backup-Manager."""
        load_dotenv()
        
        self.mongodb_uri = os.getenv("MONGODB_URI")
        self.database_name = os.getenv("MONGODB_DB")
        self.backup_dir = os.getenv("BACKUP_DIR", "/backups")
        self.retention_days = int(os.getenv("BACKUP_RETENTION_DAYS", "7"))
        
        self.client = AsyncIOMotorClient(self.mongodb_uri)
        self.db = self.client[self.database_name]

    async def create_backup(self):
        """Erstellt ein Backup der Datenbank."""
        try:
            # Backup-Verzeichnis erstellen
            backup_path = Path(self.backup_dir)
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Zeitstempel für Backup-Datei
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Collections auflisten
            collections = await self.db.list_collection_names()
            
            for collection in collections:
                # Backup-Datei für Collection
                backup_file = backup_path / f"{collection}_{timestamp}.json"
                
                # Dokumente aus Collection exportieren
                cursor = self.db[collection].find({})
                documents = await cursor.to_list(length=None)
                
                # In JSON-Datei speichern
                with open(backup_file, 'w') as f:
                    for doc in documents:
                        doc['_id'] = str(doc['_id'])  # ObjectId zu String konvertieren
                        f.write(f"{doc}\n")
                
                logger.info(f"Backup erstellt für Collection {collection}: {backup_file}")
            
            # Alte Backups bereinigen
            await self.cleanup_old_backups()
            
            logger.info("Backup erfolgreich abgeschlossen")
            
        except Exception as e:
            logger.error(f"Fehler beim Backup: {e}")
            raise

    async def cleanup_old_backups(self):
        """Entfernt alte Backups basierend auf der Aufbewahrungszeit."""
        try:
            backup_path = Path(self.backup_dir)
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            
            for backup_file in backup_path.glob("*.json"):
                # Zeitstempel aus Dateinamen extrahieren
                try:
                    file_date_str = backup_file.stem.split("_")[-2]
                    file_date = datetime.strptime(file_date_str, "%Y%m%d")
                    
                    if file_date < cutoff_date:
                        backup_file.unlink()
                        logger.info(f"Altes Backup gelöscht: {backup_file}")
                except (ValueError, IndexError):
                    logger.warning(f"Ungültiger Backup-Dateiname: {backup_file}")
                    continue
            
        except Exception as e:
            logger.error(f"Fehler beim Bereinigen alter Backups: {e}")
            raise

    async def verify_backup(self, backup_files: List[Path]) -> bool:
        """
        Überprüft die Integrität der Backup-Dateien.
        
        Args:
            backup_files: Liste der Backup-Dateien
            
        Returns:
            True wenn Verifikation erfolgreich, sonst False
        """
        try:
            for backup_file in backup_files:
                if not backup_file.exists():
                    logger.error(f"Backup-Datei nicht gefunden: {backup_file}")
                    return False
                
                if backup_file.stat().st_size == 0:
                    logger.error(f"Backup-Datei ist leer: {backup_file}")
                    return False
                
                # Stichprobenartige Überprüfung der JSON-Struktur
                with open(backup_file, 'r') as f:
                    first_line = f.readline().strip()
                    if not first_line.startswith("{") or not first_line.endswith("}"):
                        logger.error(f"Ungültiges JSON-Format in: {backup_file}")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Fehler bei der Backup-Verifikation: {e}")
            return False

    async def close(self):
        """Schließt die Datenbankverbindung."""
        self.client.close()

def create_backup_dir():
    """Backup-Verzeichnis erstellen"""
    backup_dir = os.path.join("data", "backups", datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
    os.makedirs(backup_dir, exist_ok=True)
    return backup_dir

def backup_mongodb():
    """MongoDB-Backup erstellen"""
    try:
        backup_dir = create_backup_dir()
        output_file = os.path.join(backup_dir, "mongodb_backup.gz")
        
        cmd = [
            "mongodump",
            "--uri", settings.MONGODB_URI,
            "--gzip",
            "--archive=" + output_file
        ]
        
        subprocess.run(cmd, check=True)
        logger.info(f"MongoDB-Backup erstellt: {output_file}")
        
    except Exception as e:
        logger.error(f"Fehler beim MongoDB-Backup: {str(e)}")
        raise

def backup_postgresql():
    """PostgreSQL-Backup erstellen"""
    try:
        backup_dir = create_backup_dir()
        output_file = os.path.join(backup_dir, "postgresql_backup.sql")
        
        env = os.environ.copy()
        env["PGPASSWORD"] = settings.POSTGRES_PASSWORD
        
        cmd = [
            "pg_dump",
            "-h", settings.POSTGRES_HOST,
            "-p", str(settings.POSTGRES_PORT),
            "-U", settings.POSTGRES_USER,
            "-d", settings.POSTGRES_DB,
            "-f", output_file
        ]
        
        subprocess.run(cmd, env=env, check=True)
        logger.info(f"PostgreSQL-Backup erstellt: {output_file}")
        
    except Exception as e:
        logger.error(f"Fehler beim PostgreSQL-Backup: {str(e)}")
        raise

def restore_mongodb(backup_file):
    """MongoDB-Backup wiederherstellen"""
    try:
        cmd = [
            "mongorestore",
            "--uri", settings.MONGODB_URI,
            "--gzip",
            "--archive=" + backup_file
        ]
        
        subprocess.run(cmd, check=True)
        logger.info("MongoDB-Backup wiederhergestellt")
        
    except Exception as e:
        logger.error(f"Fehler bei MongoDB-Wiederherstellung: {str(e)}")
        raise

def restore_postgresql(backup_file):
    """PostgreSQL-Backup wiederherstellen"""
    try:
        env = os.environ.copy()
        env["PGPASSWORD"] = settings.POSTGRES_PASSWORD
        
        cmd = [
            "psql",
            "-h", settings.POSTGRES_HOST,
            "-p", str(settings.POSTGRES_PORT),
            "-U", settings.POSTGRES_USER,
            "-d", settings.POSTGRES_DB,
            "-f", backup_file
        ]
        
        subprocess.run(cmd, env=env, check=True)
        logger.info("PostgreSQL-Backup wiederhergestellt")
        
    except Exception as e:
        logger.error(f"Fehler bei PostgreSQL-Wiederherstellung: {str(e)}")
        raise

def backup_all():
    """Alle Datenbanken sichern"""
    try:
        backup_mongodb()
        backup_postgresql()
        logger.info("Alle Backups erfolgreich erstellt")
        
    except Exception as e:
        logger.error(f"Fehler beim Backup: {str(e)}")
        raise

def restore_all(mongodb_backup, postgresql_backup):
    """Alle Datenbanken wiederherstellen"""
    try:
        restore_mongodb(mongodb_backup)
        restore_postgresql(postgresql_backup)
        logger.info("Alle Backups erfolgreich wiederhergestellt")
        
    except Exception as e:
        logger.error(f"Fehler bei der Wiederherstellung: {str(e)}")
        raise

async def main():
    """Hauptfunktion."""
    backup_manager = None
    try:
        backup_manager = DatabaseBackup()
        await backup_manager.create_backup()
    except Exception as e:
        logger.error(f"Backup fehlgeschlagen: {e}")
        raise
    finally:
        if backup_manager:
            await backup_manager.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", choices=["backup", "restore"], required=True)
    parser.add_argument("--mongodb-backup", help="MongoDB backup file for restore")
    parser.add_argument("--postgresql-backup", help="PostgreSQL backup file for restore")
    
    args = parser.parse_args()
    
    if args.action == "backup":
        backup_all()
    else:
        if not args.mongodb_backup or not args.postgresql_backup:
            parser.error("Backup-Dateien müssen für Restore angegeben werden")
        restore_all(args.mongodb_backup, args.postgresql_backup) 