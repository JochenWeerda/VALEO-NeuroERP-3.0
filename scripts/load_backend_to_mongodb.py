#!/usr/bin/env python
"""
Lädt die wichtigen Backend-Dateien in die MongoDB.
"""

import os
import sys
import json
import logging
import datetime
from pathlib import Path
import pymongo
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# Logger konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("load_backend_to_mongodb.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("LoadBackendToMongoDB")

# MongoDB-Konfiguration
MONGODB_CONNECTION_STRING = "mongodb://localhost:27017/"
MONGODB_DATABASE_NAME = "valeo_neuroerp"

def check_mongodb_connection():
    """
    Überprüft die Verbindung zur MongoDB.
    
    Returns:
        bool: True, wenn die Verbindung erfolgreich hergestellt wurde, sonst False
    """
    try:
        logger.info("Verbindung zu MongoDB wird hergestellt...")
        client = pymongo.MongoClient(
            MONGODB_CONNECTION_STRING,
            serverSelectionTimeoutMS=5000
        )
        # Verbindung testen
        client.admin.command('ping')
        logger.info("Verbindung zu MongoDB erfolgreich hergestellt.")
        client.close()
        return True
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error(f"Verbindung zu MongoDB fehlgeschlagen: {str(e)}")
        return False

def load_backend_files():
    """
    Lädt die wichtigen Backend-Dateien in die MongoDB.
    
    Returns:
        bool: True, wenn das Laden erfolgreich war, sonst False
    """
    logger.info("Lade Backend-Dateien in MongoDB...")
    
    try:
        # MongoDB-Verbindung herstellen
        client = pymongo.MongoClient(MONGODB_CONNECTION_STRING)
        db = client[MONGODB_DATABASE_NAME]
        collection = db["backend_files"]
        
        # Sammlung leeren
        collection.delete_many({})
        
        # Backend-Verzeichnis
        backend_dir = Path("backend")
        
        if not backend_dir.exists():
            logger.warning(f"Backend-Verzeichnis {backend_dir} existiert nicht.")
            return False
        
        # Wichtige Python-Dateien im Backend-Verzeichnis laden
        important_files = [
            "main.py",
            "mongodb_connector.py",
            "mongodb_restart_manager.py",
            "cache_manager.py",
            "enhanced_cache_manager.py",
            "ip_manager.py",
            "ip_manager_api.py",
            "libreoffice_processor.py",
            "modular_server.py",
            "observer_service.py",
            "performance_benchmark.py",
            "performance_optimizer.py",
            "server.py",
            "start_erp_system.py"
        ]
        
        for filename in important_files:
            file_path = backend_dir / filename
            if file_path.exists():
                try:
                    # Binärmodus zum Erkennen von Null-Bytes
                    with open(file_path, 'rb') as f:
                        content_bytes = f.read()
                    
                    # Prüfen auf Null-Bytes
                    if b'\x00' in content_bytes:
                        logger.warning(f"Datei {file_path} enthält Null-Bytes und wird übersprungen.")
                        continue
                    
                    # In Text umwandeln
                    try:
                        content = content_bytes.decode('utf-8')
                    except UnicodeDecodeError:
                        logger.warning(f"Datei {file_path} konnte nicht als UTF-8 dekodiert werden, versuche latin-1.")
                        content = content_bytes.decode('latin-1')
                    
                    # In MongoDB speichern
                    collection.insert_one({
                        "filename": file_path.name,
                        "path": str(file_path),
                        "content": content,
                        "file_type": "python",
                        "category": "backend_core",
                        "size": file_path.stat().st_size,
                        "last_modified": datetime.datetime.fromtimestamp(file_path.stat().st_mtime),
                        "timestamp": datetime.datetime.now()
                    })
                    
                    logger.info(f"Backend-Datei {file_path.name} erfolgreich geladen.")
                except Exception as e:
                    logger.warning(f"Fehler beim Lesen der Backend-Datei {file_path}: {str(e)}")
        
        logger.info("Backend-Dateien erfolgreich in MongoDB geladen.")
        client.close()
        return True
    except Exception as e:
        logger.error(f"Fehler beim Laden der Backend-Dateien: {str(e)}")
        return False

def load_apm_framework_files():
    """
    Lädt die Dateien des APM-Frameworks in die MongoDB.
    
    Returns:
        bool: True, wenn das Laden erfolgreich war, sonst False
    """
    logger.info("Lade APM-Framework-Dateien in MongoDB...")
    
    try:
        # MongoDB-Verbindung herstellen
        client = pymongo.MongoClient(MONGODB_CONNECTION_STRING)
        db = client[MONGODB_DATABASE_NAME]
        collection = db["apm_framework_files"]
        
        # Sammlung leeren
        collection.delete_many({})
        
        # APM-Framework-Verzeichnis
        apm_dir = Path("backend") / "apm_framework"
        
        if not apm_dir.exists():
            logger.warning(f"APM-Framework-Verzeichnis {apm_dir} existiert nicht.")
            return False
        
        # Alle Python-Dateien im APM-Framework-Verzeichnis laden
        for file_path in apm_dir.glob("*.py"):
            try:
                # Binärmodus zum Erkennen von Null-Bytes
                with open(file_path, 'rb') as f:
                    content_bytes = f.read()
                
                # Prüfen auf Null-Bytes
                if b'\x00' in content_bytes:
                    logger.warning(f"Datei {file_path} enthält Null-Bytes und wird übersprungen.")
                    continue
                
                # In Text umwandeln
                try:
                    content = content_bytes.decode('utf-8')
                except UnicodeDecodeError:
                    logger.warning(f"Datei {file_path} konnte nicht als UTF-8 dekodiert werden, versuche latin-1.")
                    content = content_bytes.decode('latin-1')
                
                # In MongoDB speichern
                collection.insert_one({
                    "filename": file_path.name,
                    "path": str(file_path),
                    "content": content,
                    "file_type": "python",
                    "category": "apm_framework",
                    "size": file_path.stat().st_size,
                    "last_modified": datetime.datetime.fromtimestamp(file_path.stat().st_mtime),
                    "timestamp": datetime.datetime.now()
                })
                
                logger.info(f"APM-Framework-Datei {file_path.name} erfolgreich geladen.")
            except Exception as e:
                logger.warning(f"Fehler beim Lesen der APM-Framework-Datei {file_path}: {str(e)}")
        
        logger.info("APM-Framework-Dateien erfolgreich in MongoDB geladen.")
        client.close()
        return True
    except Exception as e:
        logger.error(f"Fehler beim Laden der APM-Framework-Dateien: {str(e)}")
        return False

def load_readme_files():
    """
    Lädt die README-Dateien des Backends in die MongoDB.
    
    Returns:
        bool: True, wenn das Laden erfolgreich war, sonst False
    """
    logger.info("Lade README-Dateien in MongoDB...")
    
    try:
        # MongoDB-Verbindung herstellen
        client = pymongo.MongoClient(MONGODB_CONNECTION_STRING)
        db = client[MONGODB_DATABASE_NAME]
        collection = db["readme_files"]
        
        # Sammlung leeren
        collection.delete_many({})
        
        # Backend-Verzeichnis
        backend_dir = Path("backend")
        
        if not backend_dir.exists():
            logger.warning(f"Backend-Verzeichnis {backend_dir} existiert nicht.")
            return False
        
        # Alle README-Dateien im Backend-Verzeichnis laden
        for file_path in backend_dir.glob("README*.md"):
            try:
                # Binärmodus zum Erkennen von Null-Bytes
                with open(file_path, 'rb') as f:
                    content_bytes = f.read()
                
                # Prüfen auf Null-Bytes
                if b'\x00' in content_bytes:
                    logger.warning(f"Datei {file_path} enthält Null-Bytes und wird übersprungen.")
                    continue
                
                # In Text umwandeln
                try:
                    content = content_bytes.decode('utf-8')
                except UnicodeDecodeError:
                    logger.warning(f"Datei {file_path} konnte nicht als UTF-8 dekodiert werden, versuche latin-1.")
                    content = content_bytes.decode('latin-1')
                
                # In MongoDB speichern
                collection.insert_one({
                    "filename": file_path.name,
                    "path": str(file_path),
                    "content": content,
                    "file_type": "markdown",
                    "category": "documentation",
                    "size": file_path.stat().st_size,
                    "last_modified": datetime.datetime.fromtimestamp(file_path.stat().st_mtime),
                    "timestamp": datetime.datetime.now()
                })
                
                logger.info(f"README-Datei {file_path.name} erfolgreich geladen.")
            except Exception as e:
                logger.warning(f"Fehler beim Lesen der README-Datei {file_path}: {str(e)}")
        
        logger.info("README-Dateien erfolgreich in MongoDB geladen.")
        client.close()
        return True
    except Exception as e:
        logger.error(f"Fehler beim Laden der README-Dateien: {str(e)}")
        return False

def create_indexes():
    """
    Erstellt Indizes in den MongoDB-Sammlungen für eine bessere Suchleistung.
    
    Returns:
        bool: True, wenn die Indizes erfolgreich erstellt wurden, sonst False
    """
    logger.info("Erstelle Indizes in MongoDB-Sammlungen...")
    
    try:
        # MongoDB-Verbindung herstellen
        client = pymongo.MongoClient(MONGODB_CONNECTION_STRING)
        db = client[MONGODB_DATABASE_NAME]
        
        # Indizes für backend_files
        db.backend_files.create_index("filename")
        db.backend_files.create_index("category")
        db.backend_files.create_index([("content", pymongo.TEXT)])
        
        # Indizes für apm_framework_files
        db.apm_framework_files.create_index("filename")
        db.apm_framework_files.create_index([("content", pymongo.TEXT)])
        
        # Indizes für readme_files
        db.readme_files.create_index("filename")
        db.readme_files.create_index([("content", pymongo.TEXT)])
        
        logger.info("Indizes erfolgreich erstellt.")
        client.close()
        return True
    except Exception as e:
        logger.error(f"Fehler beim Erstellen der Indizes: {str(e)}")
        return False

def main():
    """
    Hauptfunktion für das Laden der wichtigen Backend-Dateien in die MongoDB.
    """
    # MongoDB-Verbindung prüfen
    if not check_mongodb_connection():
        logger.error("Konnte keine Verbindung zur MongoDB herstellen.")
        return 1
    
    # Backend-Dateien laden
    if not load_backend_files():
        logger.error("Konnte Backend-Dateien nicht laden.")
        return 1
    
    # APM-Framework-Dateien laden
    if not load_apm_framework_files():
        logger.error("Konnte APM-Framework-Dateien nicht laden.")
        return 1
    
    # README-Dateien laden
    if not load_readme_files():
        logger.error("Konnte README-Dateien nicht laden.")
        return 1
    
    # Indizes erstellen
    if not create_indexes():
        logger.error("Konnte Indizes nicht erstellen.")
        return 1
    
    logger.info("Alle Backend-Dateien erfolgreich in die MongoDB geladen.")
    return 0


if __name__ == "__main__":
    sys.exit(main())