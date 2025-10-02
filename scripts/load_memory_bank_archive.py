#!/usr/bin/env python
"""
Lädt alle wichtigen Informationen aus der memory-bank und dem Archiv in die MongoDB.
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
        logging.FileHandler("load_memory_bank_archive.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("LoadMemoryBankArchive")

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

def load_archive_documents():
    """
    Lädt alle Dokumente aus dem Archiv-Verzeichnis in die MongoDB.
    
    Returns:
        bool: True, wenn das Laden erfolgreich war, sonst False
    """
    logger.info("Lade Archiv-Dokumente in MongoDB...")
    
    try:
        # MongoDB-Verbindung herstellen
        client = pymongo.MongoClient(MONGODB_CONNECTION_STRING)
        db = client[MONGODB_DATABASE_NAME]
        collection = db["archive_documents"]
        
        # Sammlung leeren
        collection.delete_many({})
        
        # Archiv-Verzeichnis
        archive_dir = Path("memory-bank") / "archive"
        
        if not archive_dir.exists():
            logger.warning(f"Archiv-Verzeichnis {archive_dir} existiert nicht.")
            return False
        
        # Alle Markdown-Dateien im Archiv-Verzeichnis laden
        for archive_file in archive_dir.glob("*.md"):
            try:
                # Binärmodus zum Erkennen von Null-Bytes
                with open(archive_file, 'rb') as f:
                    content_bytes = f.read()
                
                # Prüfen auf Null-Bytes
                if b'\x00' in content_bytes:
                    logger.warning(f"Datei {archive_file} enthält Null-Bytes und wird übersprungen.")
                    continue
                
                # In Text umwandeln
                try:
                    content = content_bytes.decode('utf-8')
                except UnicodeDecodeError:
                    logger.warning(f"Datei {archive_file} konnte nicht als UTF-8 dekodiert werden, versuche latin-1.")
                    content = content_bytes.decode('latin-1')
                
                # Metadaten extrahieren
                metadata = extract_markdown_metadata(content)
                
                # In MongoDB speichern
                collection.insert_one({
                    "filename": archive_file.name,
                    "path": str(archive_file),
                    "content": content,
                    "metadata": metadata,
                    "last_modified": datetime.datetime.fromtimestamp(archive_file.stat().st_mtime),
                    "timestamp": datetime.datetime.now()
                })
                
                logger.info(f"Archiv-Datei {archive_file.name} erfolgreich geladen.")
            except Exception as e:
                logger.warning(f"Fehler beim Lesen der Archiv-Datei {archive_file}: {str(e)}")
        
        logger.info("Archiv-Dokumente erfolgreich in MongoDB geladen.")
        client.close()
        return True
    except Exception as e:
        logger.error(f"Fehler beim Laden der Archiv-Dokumente: {str(e)}")
        return False

def load_creative_documents():
    """
    Lädt alle Dokumente aus dem Creative-Verzeichnis in die MongoDB.
    
    Returns:
        bool: True, wenn das Laden erfolgreich war, sonst False
    """
    logger.info("Lade Creative-Dokumente in MongoDB...")
    
    try:
        # MongoDB-Verbindung herstellen
        client = pymongo.MongoClient(MONGODB_CONNECTION_STRING)
        db = client[MONGODB_DATABASE_NAME]
        collection = db["creative_documents"]
        
        # Sammlung leeren
        collection.delete_many({})
        
        # Creative-Verzeichnis
        creative_dir = Path("memory-bank") / "creative"
        
        if not creative_dir.exists():
            logger.warning(f"Creative-Verzeichnis {creative_dir} existiert nicht.")
            return False
        
        # Alle Markdown-Dateien im Creative-Verzeichnis laden
        for creative_file in creative_dir.glob("*.md"):
            try:
                # Binärmodus zum Erkennen von Null-Bytes
                with open(creative_file, 'rb') as f:
                    content_bytes = f.read()
                
                # Prüfen auf Null-Bytes
                if b'\x00' in content_bytes:
                    logger.warning(f"Datei {creative_file} enthält Null-Bytes und wird übersprungen.")
                    continue
                
                # In Text umwandeln
                try:
                    content = content_bytes.decode('utf-8')
                except UnicodeDecodeError:
                    logger.warning(f"Datei {creative_file} konnte nicht als UTF-8 dekodiert werden, versuche latin-1.")
                    content = content_bytes.decode('latin-1')
                
                # Metadaten extrahieren
                metadata = extract_markdown_metadata(content)
                
                # In MongoDB speichern
                collection.insert_one({
                    "filename": creative_file.name,
                    "path": str(creative_file),
                    "content": content,
                    "metadata": metadata,
                    "last_modified": datetime.datetime.fromtimestamp(creative_file.stat().st_mtime),
                    "timestamp": datetime.datetime.now()
                })
                
                logger.info(f"Creative-Datei {creative_file.name} erfolgreich geladen.")
            except Exception as e:
                logger.warning(f"Fehler beim Lesen der Creative-Datei {creative_file}: {str(e)}")
        
        logger.info("Creative-Dokumente erfolgreich in MongoDB geladen.")
        client.close()
        return True
    except Exception as e:
        logger.error(f"Fehler beim Laden der Creative-Dokumente: {str(e)}")
        return False

def load_reflection_documents():
    """
    Lädt alle Dokumente aus dem Reflection-Verzeichnis in die MongoDB.
    
    Returns:
        bool: True, wenn das Laden erfolgreich war, sonst False
    """
    logger.info("Lade Reflection-Dokumente in MongoDB...")
    
    try:
        # MongoDB-Verbindung herstellen
        client = pymongo.MongoClient(MONGODB_CONNECTION_STRING)
        db = client[MONGODB_DATABASE_NAME]
        collection = db["reflection_documents"]
        
        # Sammlung leeren
        collection.delete_many({})
        
        # Reflection-Verzeichnis
        reflection_dir = Path("memory-bank") / "reflection"
        
        if not reflection_dir.exists():
            logger.warning(f"Reflection-Verzeichnis {reflection_dir} existiert nicht.")
            return False
        
        # Alle Markdown-Dateien im Reflection-Verzeichnis laden
        for reflection_file in reflection_dir.glob("*.md"):
            try:
                # Binärmodus zum Erkennen von Null-Bytes
                with open(reflection_file, 'rb') as f:
                    content_bytes = f.read()
                
                # Prüfen auf Null-Bytes
                if b'\x00' in content_bytes:
                    logger.warning(f"Datei {reflection_file} enthält Null-Bytes und wird übersprungen.")
                    continue
                
                # In Text umwandeln
                try:
                    content = content_bytes.decode('utf-8')
                except UnicodeDecodeError:
                    logger.warning(f"Datei {reflection_file} konnte nicht als UTF-8 dekodiert werden, versuche latin-1.")
                    content = content_bytes.decode('latin-1')
                
                # Metadaten extrahieren
                metadata = extract_markdown_metadata(content)
                
                # In MongoDB speichern
                collection.insert_one({
                    "filename": reflection_file.name,
                    "path": str(reflection_file),
                    "content": content,
                    "metadata": metadata,
                    "last_modified": datetime.datetime.fromtimestamp(reflection_file.stat().st_mtime),
                    "timestamp": datetime.datetime.now()
                })
                
                logger.info(f"Reflection-Datei {reflection_file.name} erfolgreich geladen.")
            except Exception as e:
                logger.warning(f"Fehler beim Lesen der Reflection-Datei {reflection_file}: {str(e)}")
        
        logger.info("Reflection-Dokumente erfolgreich in MongoDB geladen.")
        client.close()
        return True
    except Exception as e:
        logger.error(f"Fehler beim Laden der Reflection-Dokumente: {str(e)}")
        return False

def load_memory_bank_root_documents():
    """
    Lädt alle Markdown-Dokumente aus dem Wurzelverzeichnis der memory-bank in die MongoDB.
    
    Returns:
        bool: True, wenn das Laden erfolgreich war, sonst False
    """
    logger.info("Lade Dokumente aus dem memory-bank-Wurzelverzeichnis in MongoDB...")
    
    try:
        # MongoDB-Verbindung herstellen
        client = pymongo.MongoClient(MONGODB_CONNECTION_STRING)
        db = client[MONGODB_DATABASE_NAME]
        collection = db["memory_bank_documents"]
        
        # Sammlung leeren
        collection.delete_many({})
        
        # memory-bank-Verzeichnis
        memory_bank_dir = Path("memory-bank")
        
        if not memory_bank_dir.exists():
            logger.warning(f"memory-bank-Verzeichnis {memory_bank_dir} existiert nicht.")
            return False
        
        # Alle Markdown-Dateien im memory-bank-Verzeichnis laden
        for md_file in memory_bank_dir.glob("*.md"):
            try:
                # Binärmodus zum Erkennen von Null-Bytes
                with open(md_file, 'rb') as f:
                    content_bytes = f.read()
                
                # Prüfen auf Null-Bytes
                if b'\x00' in content_bytes:
                    logger.warning(f"Datei {md_file} enthält Null-Bytes und wird übersprungen.")
                    continue
                
                # In Text umwandeln
                try:
                    content = content_bytes.decode('utf-8')
                except UnicodeDecodeError:
                    logger.warning(f"Datei {md_file} konnte nicht als UTF-8 dekodiert werden, versuche latin-1.")
                    content = content_bytes.decode('latin-1')
                
                # Metadaten extrahieren
                metadata = extract_markdown_metadata(content)
                
                # In MongoDB speichern
                collection.insert_one({
                    "filename": md_file.name,
                    "path": str(md_file),
                    "content": content,
                    "metadata": metadata,
                    "last_modified": datetime.datetime.fromtimestamp(md_file.stat().st_mtime),
                    "timestamp": datetime.datetime.now()
                })
                
                logger.info(f"Datei {md_file.name} aus memory-bank-Wurzelverzeichnis erfolgreich geladen.")
            except Exception as e:
                logger.warning(f"Fehler beim Lesen der Datei {md_file}: {str(e)}")
        
        logger.info("Dokumente aus dem memory-bank-Wurzelverzeichnis erfolgreich in MongoDB geladen.")
        client.close()
        return True
    except Exception as e:
        logger.error(f"Fehler beim Laden der Dokumente aus dem memory-bank-Wurzelverzeichnis: {str(e)}")
        return False

def load_json_data():
    """
    Lädt alle JSON-Dateien aus der memory-bank in die MongoDB.
    
    Returns:
        bool: True, wenn das Laden erfolgreich war, sonst False
    """
    logger.info("Lade JSON-Dateien aus der memory-bank in MongoDB...")
    
    try:
        # MongoDB-Verbindung herstellen
        client = pymongo.MongoClient(MONGODB_CONNECTION_STRING)
        db = client[MONGODB_DATABASE_NAME]
        collection = db["json_data"]
        
        # Sammlung leeren
        collection.delete_many({})
        
        # memory-bank-Verzeichnis
        memory_bank_dir = Path("memory-bank")
        
        if not memory_bank_dir.exists():
            logger.warning(f"memory-bank-Verzeichnis {memory_bank_dir} existiert nicht.")
            return False
        
        # Alle JSON-Dateien in der memory-bank laden
        for json_file in memory_bank_dir.glob("**/*.json"):
            try:
                # Datei lesen
                with open(json_file, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        logger.warning(f"Datei {json_file} ist kein gültiges JSON und wird übersprungen.")
                        continue
                
                # In MongoDB speichern
                collection.insert_one({
                    "filename": json_file.name,
                    "path": str(json_file),
                    "data": data,
                    "last_modified": datetime.datetime.fromtimestamp(json_file.stat().st_mtime),
                    "timestamp": datetime.datetime.now()
                })
                
                logger.info(f"JSON-Datei {json_file.name} erfolgreich geladen.")
            except Exception as e:
                logger.warning(f"Fehler beim Lesen der JSON-Datei {json_file}: {str(e)}")
        
        logger.info("JSON-Dateien aus der memory-bank erfolgreich in MongoDB geladen.")
        client.close()
        return True
    except Exception as e:
        logger.error(f"Fehler beim Laden der JSON-Dateien aus der memory-bank: {str(e)}")
        return False

def extract_markdown_metadata(content):
    """
    Extrahiert Metadaten aus einem Markdown-Dokument.
    
    Args:
        content: Inhalt des Markdown-Dokuments
        
    Returns:
        dict: Extrahierte Metadaten
    """
    metadata = {
        "title": None,
        "date": None,
        "tags": [],
        "categories": [],
        "summary": None
    }
    
    # Titel extrahieren (erste Überschrift)
    lines = content.split('\n')
    for line in lines:
        if line.startswith('# '):
            metadata["title"] = line.strip('# ').strip()
            break
    
    # Datum extrahieren (falls vorhanden)
    for line in lines:
        if line.lower().startswith('datum:') or line.lower().startswith('date:'):
            parts = line.split(':', 1)
            if len(parts) > 1:
                date_str = parts[1].strip()
                try:
                    # Versuche, das Datum zu parsen
                    date_obj = datetime.datetime.strptime(date_str, "%d.%m.%Y")
                    metadata["date"] = date_obj
                except ValueError:
                    try:
                        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                        metadata["date"] = date_obj
                    except ValueError:
                        metadata["date"] = date_str
            break
    
    # Tags extrahieren (falls vorhanden)
    for line in lines:
        if line.lower().startswith('tags:'):
            parts = line.split(':', 1)
            if len(parts) > 1:
                tags_str = parts[1].strip()
                metadata["tags"] = [tag.strip() for tag in tags_str.split(',')]
            break
    
    # Kategorien extrahieren (falls vorhanden)
    for line in lines:
        if line.lower().startswith('kategorien:') or line.lower().startswith('categories:'):
            parts = line.split(':', 1)
            if len(parts) > 1:
                categories_str = parts[1].strip()
                metadata["categories"] = [cat.strip() for cat in categories_str.split(',')]
            break
    
    # Zusammenfassung extrahieren (erster Absatz nach dem Titel)
    summary = ""
    in_summary = False
    for line in lines:
        if line.startswith('# '):
            in_summary = True
            continue
        if in_summary and line.strip():
            summary += line + " "
        if in_summary and not line.strip() and summary:
            break
    
    if summary:
        metadata["summary"] = summary.strip()
    
    return metadata

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
        
        # Indizes für archive_documents
        db.archive_documents.create_index("filename")
        db.archive_documents.create_index("metadata.title")
        db.archive_documents.create_index("metadata.tags")
        db.archive_documents.create_index([("content", pymongo.TEXT)])
        
        # Indizes für creative_documents
        db.creative_documents.create_index("filename")
        db.creative_documents.create_index("metadata.title")
        db.creative_documents.create_index("metadata.tags")
        db.creative_documents.create_index([("content", pymongo.TEXT)])
        
        # Indizes für reflection_documents
        db.reflection_documents.create_index("filename")
        db.reflection_documents.create_index("metadata.title")
        db.reflection_documents.create_index("metadata.tags")
        db.reflection_documents.create_index([("content", pymongo.TEXT)])
        
        # Indizes für memory_bank_documents
        db.memory_bank_documents.create_index("filename")
        db.memory_bank_documents.create_index("metadata.title")
        db.memory_bank_documents.create_index("metadata.tags")
        db.memory_bank_documents.create_index([("content", pymongo.TEXT)])
        
        # Indizes für json_data
        db.json_data.create_index("filename")
        
        logger.info("Indizes erfolgreich erstellt.")
        client.close()
        return True
    except Exception as e:
        logger.error(f"Fehler beim Erstellen der Indizes: {str(e)}")
        return False

def main():
    """
    Hauptfunktion für das Laden aller wichtigen Informationen aus der memory-bank und dem Archiv in die MongoDB.
    """
    # MongoDB-Verbindung prüfen
    if not check_mongodb_connection():
        logger.error("Konnte keine Verbindung zur MongoDB herstellen.")
        return 1
    
    # Daten laden
    success = True
    
    if not load_archive_documents():
        logger.error("Konnte Archiv-Dokumente nicht laden.")
        success = False
    
    if not load_creative_documents():
        logger.error("Konnte Creative-Dokumente nicht laden.")
        success = False
    
    if not load_reflection_documents():
        logger.error("Konnte Reflection-Dokumente nicht laden.")
        success = False
    
    if not load_memory_bank_root_documents():
        logger.error("Konnte Dokumente aus dem memory-bank-Wurzelverzeichnis nicht laden.")
        success = False
    
    if not load_json_data():
        logger.error("Konnte JSON-Dateien nicht laden.")
        success = False
    
    # Indizes erstellen
    if not create_indexes():
        logger.error("Konnte Indizes nicht erstellen.")
        success = False
    
    if success:
        logger.info("Alle Daten erfolgreich in die MongoDB geladen.")
        return 0
    else:
        logger.error("Es sind Fehler aufgetreten. Siehe Log für Details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())