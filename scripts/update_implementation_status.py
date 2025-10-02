#!/usr/bin/env python3
"""
Aktualisiert den Implementierungsstatus in der MongoDB.
"""

import os
import sys
import asyncio
import logging
from datetime import datetime

# Pfad zum Projekt-Root hinzufügen
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.apm_framework.mongodb_connector import APMMongoDBConnector

# Logger konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def update_implementation_status():
    """
    Aktualisiert den Implementierungsstatus in der MongoDB.
    """
    try:
        # MongoDB-Verbindung herstellen
        mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        mongodb_db = os.getenv("MONGODB_DB", "valeo_neuroerp")
        
        logger.info(f"Stelle Verbindung zu MongoDB her: {mongodb_uri}, DB: {mongodb_db}")
        mongodb = APMMongoDBConnector(mongodb_uri, mongodb_db)
        await mongodb.connect()
        
        # Aktuelles Datum im Format YYYY-MM-DD
        completion_date = datetime.now().strftime("%Y-%m-%d")
        
        # Prüfen, ob ein Datensatz existiert
        existing_status = await mongodb.find_one("project_status", {"phase": "IMPLEMENTATION"})
        
        if existing_status:
            # Implementierungsstatus aktualisieren
            await mongodb.update_one(
                "project_status",
                {"phase": "IMPLEMENTATION"},
                {"$set": {"status": "completed", "completion_date": completion_date}}
            )
            logger.info(f"Implementierungsstatus erfolgreich aktualisiert: completed, {completion_date}")
            print(f"\nImplementierungsstatus erfolgreich aktualisiert: completed, {completion_date}")
        else:
            # Neuen Datensatz erstellen, wenn keiner existiert
            await mongodb.insert_one(
                "project_status",
                {
                    "phase": "IMPLEMENTATION",
                    "status": "completed",
                    "completion_date": completion_date,
                    "created_at": datetime.now()
                }
            )
            logger.info(f"Neuer Implementierungsstatus erstellt: completed, {completion_date}")
            print(f"\nNeuer Implementierungsstatus erstellt: completed, {completion_date}")
    
    except Exception as e:
        logger.error(f"Fehler bei der Aktualisierung des Implementierungsstatus: {str(e)}")
        print(f"\nFehler: {str(e)}")
    
    finally:
        # MongoDB-Verbindung trennen
        if 'mongodb' in locals():
            await mongodb.disconnect()


if __name__ == "__main__":
    # Asynchrone Funktion ausführen
    asyncio.run(update_implementation_status())
