***REMOVED***!/usr/bin/env python
"""
Lädt alle Skripte aus dem scripts-Verzeichnis in die MongoDB.
"""

import os
import sys
import logging
import datetime
from pathlib import Path
import pymongo
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

***REMOVED*** Logger konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("load_scripts_to_mongodb.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("LoadScriptsToMongoDB")

***REMOVED*** MongoDB-Konfiguration
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
        ***REMOVED*** Verbindung testen
        client.admin.command('ping')
        logger.info("Verbindung zu MongoDB erfolgreich hergestellt.")
        client.close()
        return True
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error(f"Verbindung zu MongoDB fehlgeschlagen: {str(e)}")
        return False

def load_scripts():
    """
    Lädt alle Skripte aus dem scripts-Verzeichnis in die MongoDB.
    
    Returns:
        bool: True, wenn das Laden erfolgreich war, sonst False
    """
    logger.info("Lade Skripte in MongoDB...")
    
    try:
        ***REMOVED*** MongoDB-Verbindung herstellen
        client = pymongo.MongoClient(MONGODB_CONNECTION_STRING)
        db = client[MONGODB_DATABASE_NAME]
        collection = db["scripts"]
        
        ***REMOVED*** Sammlung leeren
        collection.delete_many({})
        
        ***REMOVED*** scripts-Verzeichnis
        scripts_dir = Path("scripts")
        
        if not scripts_dir.exists():
            logger.warning(f"scripts-Verzeichnis {scripts_dir} existiert nicht.")
            return False
        
        ***REMOVED*** Alle Dateien im scripts-Verzeichnis laden
        for script_file in scripts_dir.glob("*.*"):
            ***REMOVED*** Überspringe das aktuelle Skript
            if script_file.name == "load_scripts_to_mongodb.py":
                continue
                
            try:
                ***REMOVED*** Binärmodus zum Erkennen von Null-Bytes
                with open(script_file, 'rb') as f:
                    content_bytes = f.read()
                
                ***REMOVED*** Prüfen auf Null-Bytes
                if b'\x00' in content_bytes:
                    logger.warning(f"Datei {script_file} enthält Null-Bytes und wird übersprungen.")
                    continue
                
                ***REMOVED*** In Text umwandeln
                try:
                    content = content_bytes.decode('utf-8')
                except UnicodeDecodeError:
                    logger.warning(f"Datei {script_file} konnte nicht als UTF-8 dekodiert werden, versuche latin-1.")
                    content = content_bytes.decode('latin-1')
                
                ***REMOVED*** Skript-Typ bestimmen
                script_type = determine_script_type(script_file)
                
                ***REMOVED*** In MongoDB speichern
                collection.insert_one({
                    "filename": script_file.name,
                    "path": str(script_file),
                    "content": content,
                    "script_type": script_type,
                    "extension": script_file.suffix,
                    "size": script_file.stat().st_size,
                    "last_modified": datetime.datetime.fromtimestamp(script_file.stat().st_mtime),
                    "timestamp": datetime.datetime.now()
                })
                
                logger.info(f"Skript {script_file.name} erfolgreich geladen.")
            except Exception as e:
                logger.warning(f"Fehler beim Lesen des Skripts {script_file}: {str(e)}")
        
        logger.info("Skripte erfolgreich in MongoDB geladen.")
        client.close()
        return True
    except Exception as e:
        logger.error(f"Fehler beim Laden der Skripte: {str(e)}")
        return False

def determine_script_type(script_file):
    """
    Bestimmt den Typ eines Skripts anhand seiner Dateiendung und des Inhalts.
    
    Args:
        script_file: Pfad zur Skriptdatei
        
    Returns:
        str: Skript-Typ
    """
    extension = script_file.suffix.lower()
    
    if extension == ".py":
        return "python"
    elif extension == ".ps1":
        return "powershell"
    elif extension == ".sh":
        return "shell"
    elif extension == ".md":
        return "markdown"
    elif extension == ".js":
        return "javascript"
    elif extension == ".ts":
        return "typescript"
    else:
        return "other"

def create_indexes():
    """
    Erstellt Indizes in der MongoDB-Sammlung für eine bessere Suchleistung.
    
    Returns:
        bool: True, wenn die Indizes erfolgreich erstellt wurden, sonst False
    """
    logger.info("Erstelle Indizes in MongoDB-Sammlungen...")
    
    try:
        ***REMOVED*** MongoDB-Verbindung herstellen
        client = pymongo.MongoClient(MONGODB_CONNECTION_STRING)
        db = client[MONGODB_DATABASE_NAME]
        
        ***REMOVED*** Indizes für scripts
        db.scripts.create_index("filename")
        db.scripts.create_index("script_type")
        db.scripts.create_index([("content", pymongo.TEXT)])
        
        logger.info("Indizes erfolgreich erstellt.")
        client.close()
        return True
    except Exception as e:
        logger.error(f"Fehler beim Erstellen der Indizes: {str(e)}")
        return False

def analyze_scripts():
    """
    Analysiert die geladenen Skripte und erstellt eine Zusammenfassung.
    
    Returns:
        bool: True, wenn die Analyse erfolgreich war, sonst False
    """
    logger.info("Analysiere Skripte...")
    
    try:
        ***REMOVED*** MongoDB-Verbindung herstellen
        client = pymongo.MongoClient(MONGODB_CONNECTION_STRING)
        db = client[MONGODB_DATABASE_NAME]
        collection = db["scripts"]
        
        ***REMOVED*** Anzahl der Skripte nach Typ
        script_types = collection.aggregate([
            {"$group": {"_id": "$script_type", "count": {"$sum": 1}}}
        ])
        
        script_type_counts = {}
        for script_type in script_types:
            script_type_counts[script_type["_id"]] = script_type["count"]
        
        ***REMOVED*** Gesamtanzahl der Skripte
        total_scripts = collection.count_documents({})
        
        ***REMOVED*** Gesamtgröße der Skripte
        total_size = collection.aggregate([
            {"$group": {"_id": None, "total_size": {"$sum": "$size"}}}
        ]).next()["total_size"]
        
        ***REMOVED*** Durchschnittliche Größe der Skripte
        avg_size = total_size / total_scripts if total_scripts > 0 else 0
        
        ***REMOVED*** Größtes Skript
        largest_script = collection.find_one(sort=[("size", pymongo.DESCENDING)])
        
        ***REMOVED*** Kleinstes Skript
        smallest_script = collection.find_one(sort=[("size", pymongo.ASCENDING)])
        
        ***REMOVED*** Neuestes Skript
        newest_script = collection.find_one(sort=[("last_modified", pymongo.DESCENDING)])
        
        ***REMOVED*** Ältestes Skript
        oldest_script = collection.find_one(sort=[("last_modified", pymongo.ASCENDING)])
        
        ***REMOVED*** Zusammenfassung erstellen
        summary = {
            "total_scripts": total_scripts,
            "script_type_counts": script_type_counts,
            "total_size": total_size,
            "avg_size": avg_size,
            "largest_script": {
                "filename": largest_script["filename"],
                "size": largest_script["size"]
            } if largest_script else None,
            "smallest_script": {
                "filename": smallest_script["filename"],
                "size": smallest_script["size"]
            } if smallest_script else None,
            "newest_script": {
                "filename": newest_script["filename"],
                "last_modified": newest_script["last_modified"]
            } if newest_script else None,
            "oldest_script": {
                "filename": oldest_script["filename"],
                "last_modified": oldest_script["last_modified"]
            } if oldest_script else None,
            "timestamp": datetime.datetime.now()
        }
        
        ***REMOVED*** Zusammenfassung in MongoDB speichern
        db.script_analysis.delete_many({})
        db.script_analysis.insert_one(summary)
        
        logger.info("Skript-Analyse erfolgreich erstellt.")
        
        ***REMOVED*** Zusammenfassung ausgeben
        print("\n" + "=" * 80)
        print("Skript-Analyse".center(80))
        print("=" * 80)
        print(f"Gesamtanzahl der Skripte: {total_scripts}")
        print("\nAnzahl der Skripte nach Typ:")
        for script_type, count in script_type_counts.items():
            print(f"  {script_type}: {count}")
        print(f"\nGesamtgröße der Skripte: {total_size} Bytes ({total_size / 1024:.2f} KB)")
        print(f"Durchschnittliche Größe der Skripte: {avg_size:.2f} Bytes ({avg_size / 1024:.2f} KB)")
        if largest_script:
            print(f"\nGrößtes Skript: {largest_script['filename']} ({largest_script['size']} Bytes)")
        if smallest_script:
            print(f"Kleinstes Skript: {smallest_script['filename']} ({smallest_script['size']} Bytes)")
        if newest_script:
            print(f"\nNeuestes Skript: {newest_script['filename']} ({newest_script['last_modified'].strftime('%d.%m.%Y %H:%M:%S')})")
        if oldest_script:
            print(f"Ältestes Skript: {oldest_script['filename']} ({oldest_script['last_modified'].strftime('%d.%m.%Y %H:%M:%S')})")
        print("=" * 80 + "\n")
        
        client.close()
        return True
    except Exception as e:
        logger.error(f"Fehler bei der Analyse der Skripte: {str(e)}")
        return False

def main():
    """
    Hauptfunktion für das Laden aller Skripte aus dem scripts-Verzeichnis in die MongoDB.
    """
    ***REMOVED*** MongoDB-Verbindung prüfen
    if not check_mongodb_connection():
        logger.error("Konnte keine Verbindung zur MongoDB herstellen.")
        return 1
    
    ***REMOVED*** Skripte laden
    if not load_scripts():
        logger.error("Konnte Skripte nicht laden.")
        return 1
    
    ***REMOVED*** Indizes erstellen
    if not create_indexes():
        logger.error("Konnte Indizes nicht erstellen.")
        return 1
    
    ***REMOVED*** Skripte analysieren
    if not analyze_scripts():
        logger.error("Konnte Skripte nicht analysieren.")
        return 1
    
    logger.info("Alle Skripte erfolgreich in die MongoDB geladen und analysiert.")
    return 0


if __name__ == "__main__":
    sys.exit(main())