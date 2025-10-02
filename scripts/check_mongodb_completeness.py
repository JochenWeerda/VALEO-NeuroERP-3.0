#!/usr/bin/env python
"""
Überprüft die Vollständigkeit der MongoDB-Datenbank und erstellt eine Zusammenfassung.
"""

import sys
import logging
import datetime
import pymongo
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# Logger konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("check_mongodb_completeness.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("CheckMongoDBCompleteness")

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

def check_collections():
    """
    Überprüft die Vollständigkeit der MongoDB-Sammlungen.
    
    Returns:
        dict: Informationen über die MongoDB-Sammlungen
    """
    logger.info("Überprüfe MongoDB-Sammlungen...")
    
    try:
        # MongoDB-Verbindung herstellen
        client = pymongo.MongoClient(MONGODB_CONNECTION_STRING)
        db = client[MONGODB_DATABASE_NAME]
        
        # Alle Sammlungen abrufen
        collections = db.list_collection_names()
        
        # Erwartete Sammlungen
        expected_collections = [
            "project_structure",
            "tasks",
            "context",
            "readme",
            "archive",
            "creative",
            "reflection",
            "memory_bank",
            "json_data",
            "scripts",
            "script_analysis",
            "backend_files",
            "apm_framework_files",
            "readme_files",
            "documentation",
            "apm_framework_docs",
            "custom_finance",
            "custom_finance_xml",
            "backup_cursor"
        ]
        
        # Überprüfen, ob alle erwarteten Sammlungen vorhanden sind
        missing_collections = [collection for collection in expected_collections if collection not in collections]
        
        # Anzahl der Dokumente in jeder Sammlung zählen
        collection_counts = {}
        for collection in collections:
            count = db[collection].count_documents({})
            collection_counts[collection] = count
        
        # Größe jeder Sammlung berechnen
        collection_sizes = {}
        for collection in collections:
            size = db.command("collStats", collection)["size"]
            collection_sizes[collection] = size
        
        # Ergebnis zusammenstellen
        result = {
            "collections": collections,
            "expected_collections": expected_collections,
            "missing_collections": missing_collections,
            "collection_counts": collection_counts,
            "collection_sizes": collection_sizes,
            "timestamp": datetime.datetime.now()
        }
        
        client.close()
        return result
    except Exception as e:
        logger.error(f"Fehler beim Überprüfen der MongoDB-Sammlungen: {str(e)}")
        return None

def check_indexes():
    """
    Überprüft die Indizes in den MongoDB-Sammlungen.
    
    Returns:
        dict: Informationen über die MongoDB-Indizes
    """
    logger.info("Überprüfe MongoDB-Indizes...")
    
    try:
        # MongoDB-Verbindung herstellen
        client = pymongo.MongoClient(MONGODB_CONNECTION_STRING)
        db = client[MONGODB_DATABASE_NAME]
        
        # Alle Sammlungen abrufen
        collections = db.list_collection_names()
        
        # Indizes für jede Sammlung abrufen
        indexes = {}
        for collection in collections:
            index_info = db[collection].index_information()
            indexes[collection] = list(index_info.keys())
        
        # Ergebnis zusammenstellen
        result = {
            "indexes": indexes,
            "timestamp": datetime.datetime.now()
        }
        
        client.close()
        return result
    except Exception as e:
        logger.error(f"Fehler beim Überprüfen der MongoDB-Indizes: {str(e)}")
        return None

def save_summary(collections_info, indexes_info):
    """
    Speichert eine Zusammenfassung der MongoDB-Datenbank.
    
    Args:
        collections_info: Informationen über die MongoDB-Sammlungen
        indexes_info: Informationen über die MongoDB-Indizes
    
    Returns:
        bool: True, wenn die Zusammenfassung erfolgreich gespeichert wurde, sonst False
    """
    logger.info("Speichere Zusammenfassung der MongoDB-Datenbank...")
    
    try:
        # MongoDB-Verbindung herstellen
        client = pymongo.MongoClient(MONGODB_CONNECTION_STRING)
        db = client[MONGODB_DATABASE_NAME]
        
        # Zusammenfassung erstellen
        summary = {
            "collections_info": collections_info,
            "indexes_info": indexes_info,
            "timestamp": datetime.datetime.now()
        }
        
        # Zusammenfassung speichern
        db.mongodb_summary.delete_many({})
        db.mongodb_summary.insert_one(summary)
        
        logger.info("Zusammenfassung der MongoDB-Datenbank erfolgreich gespeichert.")
        client.close()
        return True
    except Exception as e:
        logger.error(f"Fehler beim Speichern der Zusammenfassung der MongoDB-Datenbank: {str(e)}")
        return False

def print_summary(collections_info, indexes_info):
    """
    Gibt eine Zusammenfassung der MongoDB-Datenbank aus.
    
    Args:
        collections_info: Informationen über die MongoDB-Sammlungen
        indexes_info: Informationen über die MongoDB-Indizes
    """
    print("\n" + "=" * 80)
    print("MongoDB-Datenbank-Zusammenfassung".center(80))
    print("=" * 80)
    
    # Sammlungen ausgeben
    print("\nSammlungen:")
    for collection in sorted(collections_info["collections"]):
        count = collections_info["collection_counts"][collection]
        size = collections_info["collection_sizes"][collection]
        print(f"  {collection}: {count} Dokumente, {size / 1024:.2f} KB")
    
    # Fehlende Sammlungen ausgeben
    if collections_info["missing_collections"]:
        print("\nFehlende Sammlungen:")
        for collection in collections_info["missing_collections"]:
            print(f"  {collection}")
    else:
        print("\nAlle erwarteten Sammlungen sind vorhanden.")
    
    # Indizes ausgeben
    print("\nIndizes:")
    for collection, indexes in sorted(indexes_info["indexes"].items()):
        print(f"  {collection}: {len(indexes)} Indizes")
        for index in indexes:
            print(f"    - {index}")
    
    # Gesamtstatistik ausgeben
    total_documents = sum(collections_info["collection_counts"].values())
    total_size = sum(collections_info["collection_sizes"].values())
    print("\nGesamtstatistik:")
    print(f"  Anzahl der Sammlungen: {len(collections_info['collections'])}")
    print(f"  Anzahl der Dokumente: {total_documents}")
    print(f"  Gesamtgröße: {total_size / 1024:.2f} KB ({total_size / (1024 * 1024):.2f} MB)")
    
    print("=" * 80)

def main():
    """
    Hauptfunktion für die Überprüfung der Vollständigkeit der MongoDB-Datenbank.
    """
    # MongoDB-Verbindung prüfen
    if not check_mongodb_connection():
        logger.error("Konnte keine Verbindung zur MongoDB herstellen.")
        return 1
    
    # Sammlungen überprüfen
    collections_info = check_collections()
    if collections_info is None:
        logger.error("Konnte MongoDB-Sammlungen nicht überprüfen.")
        return 1
    
    # Indizes überprüfen
    indexes_info = check_indexes()
    if indexes_info is None:
        logger.error("Konnte MongoDB-Indizes nicht überprüfen.")
        return 1
    
    # Zusammenfassung speichern
    if not save_summary(collections_info, indexes_info):
        logger.error("Konnte Zusammenfassung der MongoDB-Datenbank nicht speichern.")
        return 1
    
    # Zusammenfassung ausgeben
    print_summary(collections_info, indexes_info)
    
    logger.info("Überprüfung der Vollständigkeit der MongoDB-Datenbank erfolgreich abgeschlossen.")
    return 0


if __name__ == "__main__":
    sys.exit(main()) 