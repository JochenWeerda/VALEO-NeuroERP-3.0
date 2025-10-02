#!/usr/bin/env python
"""
Lädt die Daten aus dem custom_finance-Verzeichnis in die MongoDB.
"""

import os
import sys
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
        logging.FileHandler("load_custom_finance_to_mongodb.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("LoadCustomFinanceToMongoDB")

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

def load_custom_finance_files():
    """
    Lädt alle Dateien aus dem custom_finance-Verzeichnis in die MongoDB.
    
    Returns:
        bool: True, wenn das Laden erfolgreich war, sonst False
    """
    logger.info("Lade Custom Finance-Dateien in MongoDB...")
    
    try:
        # MongoDB-Verbindung herstellen
        client = pymongo.MongoClient(MONGODB_CONNECTION_STRING)
        db = client[MONGODB_DATABASE_NAME]
        collection = db["custom_finance"]
        
        # Sammlung leeren
        collection.delete_many({})
        
        # custom_finance-Verzeichnis
        custom_finance_dir = Path("custom_finance")
        
        if not custom_finance_dir.exists():
            logger.warning(f"custom_finance-Verzeichnis {custom_finance_dir} existiert nicht.")
            return False
        
        # Alle Python-Dateien im custom_finance-Verzeichnis und seinen Unterverzeichnissen laden
        for file_path in custom_finance_dir.glob("**/*.py"):
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
                
                # Kategorie bestimmen
                category = determine_category(file_path)
                
                # In MongoDB speichern
                collection.insert_one({
                    "filename": file_path.name,
                    "path": str(file_path),
                    "content": content,
                    "file_type": "python",
                    "category": category,
                    "size": file_path.stat().st_size,
                    "last_modified": datetime.datetime.fromtimestamp(file_path.stat().st_mtime),
                    "timestamp": datetime.datetime.now()
                })
                
                logger.info(f"Custom Finance-Datei {file_path.name} erfolgreich geladen.")
            except Exception as e:
                logger.warning(f"Fehler beim Lesen der Custom Finance-Datei {file_path}: {str(e)}")
        
        logger.info("Custom Finance-Dateien erfolgreich in MongoDB geladen.")
        client.close()
        return True
    except Exception as e:
        logger.error(f"Fehler beim Laden der Custom Finance-Dateien: {str(e)}")
        return False

def load_custom_finance_xml():
    """
    Lädt alle XML-Dateien aus dem custom_finance-Verzeichnis in die MongoDB.
    
    Returns:
        bool: True, wenn das Laden erfolgreich war, sonst False
    """
    logger.info("Lade Custom Finance XML-Dateien in MongoDB...")
    
    try:
        # MongoDB-Verbindung herstellen
        client = pymongo.MongoClient(MONGODB_CONNECTION_STRING)
        db = client[MONGODB_DATABASE_NAME]
        collection = db["custom_finance_xml"]
        
        # Sammlung leeren
        collection.delete_many({})
        
        # custom_finance-Verzeichnis
        custom_finance_dir = Path("custom_finance")
        
        if not custom_finance_dir.exists():
            logger.warning(f"custom_finance-Verzeichnis {custom_finance_dir} existiert nicht.")
            return False
        
        # Alle XML-Dateien im custom_finance-Verzeichnis und seinen Unterverzeichnissen laden
        for file_path in custom_finance_dir.glob("**/*.xml"):
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
                
                # Kategorie bestimmen
                category = determine_category(file_path)
                
                # In MongoDB speichern
                collection.insert_one({
                    "filename": file_path.name,
                    "path": str(file_path),
                    "content": content,
                    "file_type": "xml",
                    "category": category,
                    "size": file_path.stat().st_size,
                    "last_modified": datetime.datetime.fromtimestamp(file_path.stat().st_mtime),
                    "timestamp": datetime.datetime.now()
                })
                
                logger.info(f"Custom Finance XML-Datei {file_path.name} erfolgreich geladen.")
            except Exception as e:
                logger.warning(f"Fehler beim Lesen der Custom Finance XML-Datei {file_path}: {str(e)}")
        
        logger.info("Custom Finance XML-Dateien erfolgreich in MongoDB geladen.")
        client.close()
        return True
    except Exception as e:
        logger.error(f"Fehler beim Laden der Custom Finance XML-Dateien: {str(e)}")
        return False

def load_backup_cursor_files():
    """
    Lädt alle Dateien aus dem backup-cursor-Verzeichnis in die MongoDB.
    
    Returns:
        bool: True, wenn das Laden erfolgreich war, sonst False
    """
    logger.info("Lade Backup Cursor-Dateien in MongoDB...")
    
    try:
        # MongoDB-Verbindung herstellen
        client = pymongo.MongoClient(MONGODB_CONNECTION_STRING)
        db = client[MONGODB_DATABASE_NAME]
        collection = db["backup_cursor"]
        
        # Sammlung leeren
        collection.delete_many({})
        
        # backup-cursor-Verzeichnis
        backup_cursor_dir = Path("backup-cursor")
        
        if not backup_cursor_dir.exists():
            logger.warning(f"backup-cursor-Verzeichnis {backup_cursor_dir} existiert nicht.")
            return False
        
        # Alle Dateien im backup-cursor-Verzeichnis laden
        for file_path in backup_cursor_dir.glob("*.*"):
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
                
                # Dateityp bestimmen
                file_type = determine_file_type(file_path)
                
                # In MongoDB speichern
                collection.insert_one({
                    "filename": file_path.name,
                    "path": str(file_path),
                    "content": content,
                    "file_type": file_type,
                    "category": "backup_cursor",
                    "size": file_path.stat().st_size,
                    "last_modified": datetime.datetime.fromtimestamp(file_path.stat().st_mtime),
                    "timestamp": datetime.datetime.now()
                })
                
                logger.info(f"Backup Cursor-Datei {file_path.name} erfolgreich geladen.")
            except Exception as e:
                logger.warning(f"Fehler beim Lesen der Backup Cursor-Datei {file_path}: {str(e)}")
        
        logger.info("Backup Cursor-Dateien erfolgreich in MongoDB geladen.")
        client.close()
        return True
    except Exception as e:
        logger.error(f"Fehler beim Laden der Backup Cursor-Dateien: {str(e)}")
        return False

def determine_category(file_path):
    """
    Bestimmt die Kategorie einer Datei anhand ihres Pfads.
    
    Args:
        file_path: Pfad zur Datei
        
    Returns:
        str: Kategorie der Datei
    """
    path_str = str(file_path).lower()
    
    if "models" in path_str:
        return "models"
    elif "views" in path_str:
        return "views"
    elif "security" in path_str:
        return "security"
    elif "data" in path_str:
        return "data"
    elif "__manifest__" in path_str:
        return "manifest"
    elif "__init__" in path_str:
        return "init"
    else:
        return "other"

def determine_file_type(file_path):
    """
    Bestimmt den Dateityp anhand der Dateiendung.
    
    Args:
        file_path: Pfad zur Datei
        
    Returns:
        str: Dateityp
    """
    extension = file_path.suffix.lower()
    
    if extension == ".py":
        return "python"
    elif extension == ".xml":
        return "xml"
    elif extension == ".csv":
        return "csv"
    elif extension == ".md":
        return "markdown"
    elif extension == ".js":
        return "javascript"
    elif extension == ".html":
        return "html"
    elif extension == ".css":
        return "css"
    else:
        return "other"

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
        
        # Indizes für custom_finance
        db.custom_finance.create_index("filename")
        db.custom_finance.create_index("category")
        db.custom_finance.create_index([("content", pymongo.TEXT)])
        
        # Indizes für custom_finance_xml
        db.custom_finance_xml.create_index("filename")
        db.custom_finance_xml.create_index("category")
        db.custom_finance_xml.create_index([("content", pymongo.TEXT)])
        
        # Indizes für backup_cursor
        db.backup_cursor.create_index("filename")
        db.backup_cursor.create_index("file_type")
        db.backup_cursor.create_index([("content", pymongo.TEXT)])
        
        logger.info("Indizes erfolgreich erstellt.")
        client.close()
        return True
    except Exception as e:
        logger.error(f"Fehler beim Erstellen der Indizes: {str(e)}")
        return False

def main():
    """
    Hauptfunktion für das Laden der Daten aus dem custom_finance-Verzeichnis in die MongoDB.
    """
    # MongoDB-Verbindung prüfen
    if not check_mongodb_connection():
        logger.error("Konnte keine Verbindung zur MongoDB herstellen.")
        return 1
    
    # Custom Finance-Dateien laden
    if not load_custom_finance_files():
        logger.error("Konnte Custom Finance-Dateien nicht laden.")
        return 1
    
    # Custom Finance XML-Dateien laden
    if not load_custom_finance_xml():
        logger.error("Konnte Custom Finance XML-Dateien nicht laden.")
        return 1
    
    # Backup Cursor-Dateien laden
    if not load_backup_cursor_files():
        logger.error("Konnte Backup Cursor-Dateien nicht laden.")
        return 1
    
    # Indizes erstellen
    if not create_indexes():
        logger.error("Konnte Indizes nicht erstellen.")
        return 1
    
    logger.info("Alle Custom Finance-Daten erfolgreich in die MongoDB geladen.")
    return 0


if __name__ == "__main__":
    sys.exit(main())