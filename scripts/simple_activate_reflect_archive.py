#!/usr/bin/env python
"""
Vereinfachte Version des Skripts zum Aktivieren des REFLECT-ARCHIVE-Mode und Befüllen der MongoDB.
"""

import os
import sys
import json
import logging
import datetime
import subprocess
from pathlib import Path
import pymongo
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# Logger konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("simple_activate_reflect_archive.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("SimpleActivateReflectArchive")

# MongoDB-Konfiguration
MONGODB_CONNECTION_STRING = "mongodb://localhost:27017/"
MONGODB_DATABASE_NAME = "valeo_neuroerp"
SOURCE_DIR = "C:/AI_driven_ERP"

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

def activate_reflect_archive_mode():
    """
    Aktiviert den REFLECT-ARCHIVE-Mode, indem die entsprechende Datei in memory-bank/current_mode.txt geschrieben wird.
    
    Returns:
        bool: True, wenn der Mode erfolgreich aktiviert wurde, sonst False
    """
    logger.info("Aktiviere REFLECT-ARCHIVE-Mode...")
    
    try:
        # Pfad zur current_mode.txt
        mode_file_path = Path("memory-bank") / "current_mode.txt"
        
        # Verzeichnis erstellen, falls es nicht existiert
        mode_file_path.parent.mkdir(exist_ok=True)
        
        # Mode in Datei schreiben
        with open(mode_file_path, "w", encoding="utf-8") as f:
            f.write("REFLECT-ARCHIVE")
        
        logger.info("REFLECT-ARCHIVE-Mode erfolgreich aktiviert.")
        return True
    except Exception as e:
        logger.error(f"Fehler beim Aktivieren des REFLECT-ARCHIVE-Mode: {e}")
        return False

def create_reflection_document():
    """
    Erstellt ein Reflexionsdokument für den REFLECT-ARCHIVE-Mode.
    
    Returns:
        bool: True, wenn das Dokument erfolgreich erstellt wurde, sonst False
    """
    logger.info("Erstelle Reflexionsdokument...")
    
    try:
        # Pfad zum Reflexionsdokument
        reflection_file_path = Path("memory-bank") / "reflection" / f"reflection_ai_driven_erp.md"
        
        # Verzeichnis erstellen, falls es nicht existiert
        reflection_file_path.parent.mkdir(exist_ok=True)
        
        # Inhalt des Reflexionsdokuments
        content = """# Reflexion: AI_driven_ERP-Projekt

## Projektübersicht
Das AI_driven_ERP-Projekt ist ein KI-gestütztes ERP-System mit Fokus auf Stammdatenpflege. Es orientiert sich am Design und der Funktionalität von ORB-FMS, einem gemeinnützigen Farm-Management-System.

## Hauptkomponenten
- Backend: FastAPI-basiertes Backend mit Mikroservice-Architektur
- Frontend: React-basiertes Frontend im ORB-FMS-Design
- Datenmodelle: Optimierte Modelle für Partner, Artikel, Lager und Finanzen

## Erkenntnisse
- Die Projektstruktur folgt einer klaren Trennung von Backend und Frontend
- Das Backend nutzt FastAPI für eine performante API-Entwicklung
- Das Frontend basiert auf React und implementiert verschiedene Themes
- Es gibt eine umfangreiche Aufgabenliste mit verschiedenen Komplexitätsstufen

## Nächste Schritte
1. Vervollständigung der Dashboard-Implementierung für VALERO Enterprise Suite
2. Entwicklung der Modelle für die Geschäftslogik
3. Integration der Module mit bestehenden Odoo-Funktionen
4. Testen der Module unter realen Bedingungen

## Archivierte Artefakte
- Projektstruktur
- Code-Dateien
- Dokumentation
- Aufgaben
- Kontext

Datum: {datetime}
"""
        
        # Datum einfügen
        content = content.replace("{datetime}", datetime.datetime.now().strftime("%d.%m.%Y %H:%M"))
        
        # Dokument schreiben
        with open(reflection_file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        logger.info(f"Reflexionsdokument erfolgreich erstellt: {reflection_file_path}")
        return True
    except Exception as e:
        logger.error(f"Fehler beim Erstellen des Reflexionsdokuments: {e}")
        return False

def load_project_structure():
    """
    Lädt die Projektstruktur in die MongoDB.
    
    Returns:
        bool: True, wenn das Laden erfolgreich war, sonst False
    """
    logger.info("Lade Projektstruktur in MongoDB...")
    
    try:
        # MongoDB-Verbindung herstellen
        client = pymongo.MongoClient(MONGODB_CONNECTION_STRING)
        db = client[MONGODB_DATABASE_NAME]
        collection = db["project_structure"]
        
        # Sammlung leeren
        collection.delete_many({})
        
        # Verzeichnisstruktur scannen
        source_dir = Path(SOURCE_DIR)
        structure = {
            "name": source_dir.name,
            "type": "directory",
            "path": str(source_dir),
            "children": []
        }
        
        # Nur die obersten Verzeichnisse scannen
        for item in source_dir.iterdir():
            if item.is_dir():
                if not item.name.startswith('.') and not item.name == 'node_modules' and not item.name == 'venv':
                    structure["children"].append({
                        "name": item.name,
                        "type": "directory",
                        "path": str(item),
                        "has_children": any(True for _ in item.iterdir())
                    })
            else:
                structure["children"].append({
                    "name": item.name,
                    "type": "file",
                    "path": str(item),
                    "extension": item.suffix,
                    "size": item.stat().st_size
                })
        
        # In MongoDB speichern
        collection.insert_one({
            "timestamp": datetime.datetime.now(),
            "structure": structure
        })
        
        logger.info("Projektstruktur erfolgreich in MongoDB geladen.")
        client.close()
        return True
    except Exception as e:
        logger.error(f"Fehler beim Laden der Projektstruktur: {str(e)}")
        return False

def load_tasks():
    """
    Lädt die Aufgaben aus den tasks.md-Dateien in die MongoDB.
    
    Returns:
        bool: True, wenn das Laden erfolgreich war, sonst False
    """
    logger.info("Lade Aufgaben in MongoDB...")
    
    try:
        # MongoDB-Verbindung herstellen
        client = pymongo.MongoClient(MONGODB_CONNECTION_STRING)
        db = client[MONGODB_DATABASE_NAME]
        collection = db["tasks"]
        
        # Sammlung leeren
        collection.delete_many({})
        
        # Aufgabendateien suchen
        source_dir = Path(SOURCE_DIR)
        tasks_files = [
            source_dir / "memory-bank" / "tasks.md",
            source_dir / "memory-bank" / "tasks-new.md"
        ]
        
        for task_file in tasks_files:
            if task_file.exists():
                try:
                    # Binärmodus zum Erkennen von Null-Bytes
                    with open(task_file, 'rb') as f:
                        content_bytes = f.read()
                    
                    # Prüfen auf Null-Bytes
                    if b'\x00' in content_bytes:
                        logger.warning(f"Datei {task_file} enthält Null-Bytes und wird übersprungen.")
                        continue
                    
                    # In Text umwandeln
                    try:
                        content = content_bytes.decode('utf-8')
                    except UnicodeDecodeError:
                        logger.warning(f"Datei {task_file} konnte nicht als UTF-8 dekodiert werden, versuche latin-1.")
                        content = content_bytes.decode('latin-1')
                    
                    # In MongoDB speichern
                    collection.insert_one({
                        "filename": task_file.name,
                        "path": str(task_file),
                        "content": content,
                        "last_modified": datetime.datetime.fromtimestamp(task_file.stat().st_mtime),
                        "timestamp": datetime.datetime.now()
                    })
                    
                    logger.info(f"Aufgabendatei {task_file.name} erfolgreich geladen.")
                except Exception as e:
                    logger.warning(f"Fehler beim Lesen der Aufgabendatei {task_file}: {str(e)}")
        
        logger.info("Aufgaben erfolgreich in MongoDB geladen.")
        client.close()
        return True
    except Exception as e:
        logger.error(f"Fehler beim Laden der Aufgaben: {str(e)}")
        return False

def load_context():
    """
    Lädt die Kontextdateien in die MongoDB.
    
    Returns:
        bool: True, wenn das Laden erfolgreich war, sonst False
    """
    logger.info("Lade Kontext in MongoDB...")
    
    try:
        # MongoDB-Verbindung herstellen
        client = pymongo.MongoClient(MONGODB_CONNECTION_STRING)
        db = client[MONGODB_DATABASE_NAME]
        collection = db["context"]
        
        # Sammlung leeren
        collection.delete_many({})
        
        # Kontextdateien suchen
        source_dir = Path(SOURCE_DIR)
        context_files = [
            source_dir / "memory-bank" / "activeContext.md",
            source_dir / "memory-bank" / "progress.md"
        ]
        
        for context_file in context_files:
            if context_file.exists():
                try:
                    # Binärmodus zum Erkennen von Null-Bytes
                    with open(context_file, 'rb') as f:
                        content_bytes = f.read()
                    
                    # Prüfen auf Null-Bytes
                    if b'\x00' in content_bytes:
                        logger.warning(f"Datei {context_file} enthält Null-Bytes und wird übersprungen.")
                        continue
                    
                    # In Text umwandeln
                    try:
                        content = content_bytes.decode('utf-8')
                    except UnicodeDecodeError:
                        logger.warning(f"Datei {context_file} konnte nicht als UTF-8 dekodiert werden, versuche latin-1.")
                        content = content_bytes.decode('latin-1')
                    
                    # In MongoDB speichern
                    collection.insert_one({
                        "filename": context_file.name,
                        "path": str(context_file),
                        "content": content,
                        "last_modified": datetime.datetime.fromtimestamp(context_file.stat().st_mtime),
                        "timestamp": datetime.datetime.now()
                    })
                    
                    logger.info(f"Kontextdatei {context_file.name} erfolgreich geladen.")
                except Exception as e:
                    logger.warning(f"Fehler beim Lesen der Kontextdatei {context_file}: {str(e)}")
        
        logger.info("Kontext erfolgreich in MongoDB geladen.")
        client.close()
        return True
    except Exception as e:
        logger.error(f"Fehler beim Laden des Kontexts: {str(e)}")
        return False

def load_readme():
    """
    Lädt die README.md-Datei in die MongoDB.
    
    Returns:
        bool: True, wenn das Laden erfolgreich war, sonst False
    """
    logger.info("Lade README.md in MongoDB...")
    
    try:
        # MongoDB-Verbindung herstellen
        client = pymongo.MongoClient(MONGODB_CONNECTION_STRING)
        db = client[MONGODB_DATABASE_NAME]
        collection = db["documentation"]
        
        # Sammlung leeren
        collection.delete_many({})
        
        # README.md suchen
        source_dir = Path(SOURCE_DIR)
        readme_file = source_dir / "README.md"
        
        if readme_file.exists():
            try:
                # Binärmodus zum Erkennen von Null-Bytes
                with open(readme_file, 'rb') as f:
                    content_bytes = f.read()
                
                # Prüfen auf Null-Bytes
                if b'\x00' in content_bytes:
                    logger.warning(f"Datei {readme_file} enthält Null-Bytes und wird übersprungen.")
                    return False
                
                # In Text umwandeln
                try:
                    content = content_bytes.decode('utf-8')
                except UnicodeDecodeError:
                    logger.warning(f"Datei {readme_file} konnte nicht als UTF-8 dekodiert werden, versuche latin-1.")
                    content = content_bytes.decode('latin-1')
                
                # In MongoDB speichern
                collection.insert_one({
                    "filename": readme_file.name,
                    "path": str(readme_file),
                    "content": content,
                    "last_modified": datetime.datetime.fromtimestamp(readme_file.stat().st_mtime),
                    "timestamp": datetime.datetime.now()
                })
                
                logger.info(f"README.md erfolgreich geladen.")
            except Exception as e:
                logger.warning(f"Fehler beim Lesen der README.md: {str(e)}")
                return False
        else:
            logger.warning(f"README.md nicht gefunden.")
            return False
        
        logger.info("README.md erfolgreich in MongoDB geladen.")
        client.close()
        return True
    except Exception as e:
        logger.error(f"Fehler beim Laden der README.md: {str(e)}")
        return False

def main():
    """
    Hauptfunktion für die Aktivierung des REFLECT-ARCHIVE-Mode und das Befüllen der MongoDB.
    """
    # MongoDB-Verbindung prüfen
    if not check_mongodb_connection():
        logger.error("Konnte keine Verbindung zur MongoDB herstellen.")
        return 1
    
    # REFLECT-ARCHIVE-Mode aktivieren
    if not activate_reflect_archive_mode():
        logger.error("Konnte REFLECT-ARCHIVE-Mode nicht aktivieren.")
        return 1
    
    # Reflexionsdokument erstellen
    if not create_reflection_document():
        logger.error("Konnte Reflexionsdokument nicht erstellen.")
        return 1
    
    # Daten in MongoDB laden
    success = True
    
    if not load_project_structure():
        logger.error("Konnte Projektstruktur nicht laden.")
        success = False
    
    if not load_tasks():
        logger.error("Konnte Aufgaben nicht laden.")
        success = False
    
    if not load_context():
        logger.error("Konnte Kontext nicht laden.")
        success = False
    
    if not load_readme():
        logger.error("Konnte README.md nicht laden.")
        success = False
    
    if success:
        logger.info("REFLECT-ARCHIVE-Mode erfolgreich aktiviert und MongoDB mit Daten befüllt.")
        return 0
    else:
        logger.error("Es sind Fehler aufgetreten. Siehe Log für Details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())