"""
Skript zum Synchronisieren von Dateien mit dem RAG-System
"""
import os
from datetime import datetime, timedelta
import hashlib
from typing import Dict, List
from pymongo import MongoClient
import json
import logging
from pathlib import Path

# Logging-Konfiguration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RAGSyncManager:
    def __init__(self):
        # MongoDB Verbindung
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['valeo_neuroerp']
        self.rag_collection = self.db['rag_documents']
        self.file_status_collection = self.db['file_status']
        
        # Verzeichnisse die überwacht werden sollen
        self.watched_directories = [
            'backend',
            'modules',
            'docs',
            'memory-bank',
            'config',
            'scripts'
        ]
        
        # Dateitypen die synchronisiert werden sollen
        self.watched_extensions = {
            '.py', '.js', '.ts', '.md', '.sql', '.yaml', '.yml', 
            '.json', '.txt', '.ini', '.conf'
        }

    def calculate_file_hash(self, filepath: str) -> str:
        """Berechnet den SHA-256 Hash einer Datei."""
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def get_file_metadata(self, filepath: str) -> Dict:
        """Erstellt Metadaten für eine Datei."""
        stat = os.stat(filepath)
        return {
            'filepath': filepath,
            'last_modified': datetime.fromtimestamp(stat.st_mtime),
            'size': stat.st_size,
            'hash': self.calculate_file_hash(filepath)
        }

    def should_process_file(self, filepath: str) -> bool:
        """Prüft ob eine Datei verarbeitet werden soll."""
        # Prüfe Dateiendung
        if not any(filepath.endswith(ext) for ext in self.watched_extensions):
            return False
            
        # Ignoriere bestimmte Verzeichnisse
        ignore_dirs = {'.git', '__pycache__', 'node_modules', 'venv'}
        if any(ignore_dir in filepath for ignore_dir in ignore_dirs):
            return False
            
        return True

    def get_file_content(self, filepath: str) -> str:
        """Liest den Inhalt einer Datei."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Fehler beim Lesen von {filepath}: {e}")
            return ""

    def process_file(self, filepath: str) -> None:
        """Verarbeitet eine einzelne Datei."""
        try:
            metadata = self.get_file_metadata(filepath)
            
            # Prüfe ob die Datei bereits im System ist
            existing_doc = self.file_status_collection.find_one({'filepath': filepath})
            
            if existing_doc and existing_doc['hash'] == metadata['hash']:
                logger.debug(f"Datei {filepath} unverändert, überspringe...")
                return
                
            # Lese Dateiinhalt
            content = self.get_file_content(filepath)
            
            # Erstelle RAG-Dokument
            rag_doc = {
                'filepath': filepath,
                'content': content,
                'metadata': {
                    'file_type': Path(filepath).suffix,
                    'last_modified': metadata['last_modified'],
                    'size': metadata['size']
                },
                'embedding_status': 'pending',
                'created_at': datetime.now()
            }
            
            # Speichere in MongoDB
            self.rag_collection.insert_one(rag_doc)
            
            # Update File-Status
            self.file_status_collection.update_one(
                {'filepath': filepath},
                {'$set': metadata},
                upsert=True
            )
            
            logger.info(f"Datei {filepath} erfolgreich synchronisiert")
            
        except Exception as e:
            logger.error(f"Fehler bei der Verarbeitung von {filepath}: {e}")

    def sync_directory(self, directory: str) -> None:
        """Synchronisiert ein Verzeichnis mit dem RAG-System."""
        logger.info(f"Starte Synchronisation von {directory}")
        
        for root, _, files in os.walk(directory):
            for file in files:
                filepath = os.path.join(root, file)
                if self.should_process_file(filepath):
                    self.process_file(filepath)

    def sync_all(self) -> None:
        """Synchronisiert alle überwachten Verzeichnisse."""
        logger.info("Starte vollständige RAG-Synchronisation")
        
        for directory in self.watched_directories:
            if os.path.exists(directory):
                self.sync_directory(directory)
            else:
                logger.warning(f"Verzeichnis {directory} existiert nicht")

    def cleanup_old_documents(self, days: int = 30) -> None:
        """Löscht alte RAG-Dokumente."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        result = self.rag_collection.delete_many({
            'metadata.last_modified': {'$lt': cutoff_date}
        })
        
        logger.info(f"{result.deleted_count} alte Dokumente gelöscht")

def main():
    """Hauptfunktion"""
    try:
        rag_sync = RAGSyncManager()
        
        # Führe Synchronisation durch
        rag_sync.sync_all()
        
        # Cleanup alte Dokumente
        rag_sync.cleanup_old_documents()
        
        logger.info("RAG-Synchronisation erfolgreich abgeschlossen")
        
    except Exception as e:
        logger.error(f"Fehler während der RAG-Synchronisation: {e}")
        raise

if __name__ == "__main__":
    main() 