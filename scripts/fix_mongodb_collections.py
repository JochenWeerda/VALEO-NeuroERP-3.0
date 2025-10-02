#!/usr/bin/env python
"""
Korrigiert die fehlenden Sammlungen in der MongoDB, indem es Aliase für die vorhandenen Sammlungen erstellt.
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
        logging.FileHandler("fix_mongodb_collections.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("FixMongoDBCollections")

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

def create_collection_aliases():
    """
    Erstellt Aliase für die fehlenden Sammlungen in der MongoDB.
    
    Returns:
        bool: True, wenn die Aliase erfolgreich erstellt wurden, sonst False
    """
    logger.info("Erstelle Aliase für fehlende Sammlungen...")
    
    try:
        # MongoDB-Verbindung herstellen
        client = pymongo.MongoClient(MONGODB_CONNECTION_STRING)
        db = client[MONGODB_DATABASE_NAME]
        
        # Aliase für fehlende Sammlungen erstellen
        aliases = [
            {"source": "archive_documents", "target": "archive"},
            {"source": "creative_documents", "target": "creative"},
            {"source": "reflection_documents", "target": "reflection"},
            {"source": "memory_bank_documents", "target": "memory_bank"},
            {"source": "readme_files", "target": "readme"}
        ]
        
        for alias in aliases:
            source = alias["source"]
            target = alias["target"]
            
            # Prüfen, ob die Quellsammlung existiert
            if source not in db.list_collection_names():
                logger.warning(f"Quellsammlung {source} existiert nicht.")
                continue
            
            # Prüfen, ob die Zielsammlung bereits existiert
            if target in db.list_collection_names():
                logger.warning(f"Zielsammlung {target} existiert bereits.")
                continue
            
            # Alle Dokumente aus der Quellsammlung kopieren
            documents = list(db[source].find())
            if documents:
                db[target].insert_many(documents)
                logger.info(f"Alias für {source} -> {target} mit {len(documents)} Dokumenten erstellt.")
            else:
                logger.warning(f"Quellsammlung {source} enthält keine Dokumente.")
        
        # Indizes für die neuen Sammlungen erstellen
        create_indexes_for_aliases(db, aliases)
        
        client.close()
        return True
    except Exception as e:
        logger.error(f"Fehler beim Erstellen der Aliase: {str(e)}")
        return False

def create_indexes_for_aliases(db, aliases):
    """
    Erstellt Indizes für die neuen Sammlungen.
    
    Args:
        db: MongoDB-Datenbankverbindung
        aliases: Liste der Aliase
    """
    logger.info("Erstelle Indizes für neue Sammlungen...")
    
    try:
        for alias in aliases:
            source = alias["source"]
            target = alias["target"]
            
            # Indizes aus der Quellsammlung abrufen
            index_info = db[source].index_information()
            
            # Indizes in der Zielsammlung erstellen (außer _id_)
            for index_name, index_spec in index_info.items():
                if index_name != "_id_":
                    # Schlüssel und Optionen extrahieren
                    keys = [(k, v) for k, v in index_spec["key"].items()]
                    options = {}
                    if "unique" in index_spec:
                        options["unique"] = index_spec["unique"]
                    if "sparse" in index_spec:
                        options["sparse"] = index_spec["sparse"]
                    if "expireAfterSeconds" in index_spec:
                        options["expireAfterSeconds"] = index_spec["expireAfterSeconds"]
                    if "partialFilterExpression" in index_spec:
                        options["partialFilterExpression"] = index_spec["partialFilterExpression"]
                    
                    # Index erstellen
                    db[target].create_index(keys, **options)
                    logger.info(f"Index {index_name} für Sammlung {target} erstellt.")
    except Exception as e:
        logger.error(f"Fehler beim Erstellen der Indizes: {str(e)}")

def check_collections():
    """
    Überprüft die Vollständigkeit der MongoDB-Sammlungen nach der Korrektur.
    
    Returns:
        dict: Informationen über die MongoDB-Sammlungen
    """
    logger.info("Überprüfe MongoDB-Sammlungen nach der Korrektur...")
    
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
        
        # Ergebnis zusammenstellen
        result = {
            "collections": collections,
            "expected_collections": expected_collections,
            "missing_collections": missing_collections,
            "collection_counts": collection_counts
        }
        
        client.close()
        return result
    except Exception as e:
        logger.error(f"Fehler beim Überprüfen der MongoDB-Sammlungen: {str(e)}")
        return None

def print_summary(collections_info):
    """
    Gibt eine Zusammenfassung der MongoDB-Sammlungen nach der Korrektur aus.
    
    Args:
        collections_info: Informationen über die MongoDB-Sammlungen
    """
    print("\n" + "=" * 80)
    print("MongoDB-Sammlungen nach der Korrektur".center(80))
    print("=" * 80)
    
    # Sammlungen ausgeben
    print("\nSammlungen:")
    for collection in sorted(collections_info["collections"]):
        count = collections_info["collection_counts"][collection]
        print(f"  {collection}: {count} Dokumente")
    
    # Fehlende Sammlungen ausgeben
    if collections_info["missing_collections"]:
        print("\nFehlende Sammlungen:")
        for collection in collections_info["missing_collections"]:
            print(f"  {collection}")
    else:
        print("\nAlle erwarteten Sammlungen sind vorhanden.")
    
    print("=" * 80)

def main():
    """
    Hauptfunktion für die Korrektur der fehlenden Sammlungen in der MongoDB.
    """
    # MongoDB-Verbindung prüfen
    if not check_mongodb_connection():
        logger.error("Konnte keine Verbindung zur MongoDB herstellen.")
        return 1
    
    # Aliase für fehlende Sammlungen erstellen
    if not create_collection_aliases():
        logger.error("Konnte Aliase für fehlende Sammlungen nicht erstellen.")
        return 1
    
    # Sammlungen überprüfen
    collections_info = check_collections()
    if collections_info is None:
        logger.error("Konnte MongoDB-Sammlungen nicht überprüfen.")
        return 1
    
    # Zusammenfassung ausgeben
    print_summary(collections_info)
    
    logger.info("Korrektur der fehlenden Sammlungen in der MongoDB erfolgreich abgeschlossen.")
    return 0


if __name__ == "__main__":
    sys.exit(main())