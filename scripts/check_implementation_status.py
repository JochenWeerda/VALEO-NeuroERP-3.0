#!/usr/bin/env python3
"""
Überprüft den Implementierungsstatus in der MongoDB.
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
import json

# Pfad zum Projekt-Root hinzufügen
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.apm_framework.mongodb_connector import APMMongoDBConnector

# Logger konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MongoJSONEncoder(json.JSONEncoder):
    """JSON-Encoder für MongoDB-Objekte."""
    
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(MongoJSONEncoder, self).default(obj)


async def check_implementation_status():
    """
    Überprüft den Implementierungsstatus in der MongoDB.
    """
    try:
        # MongoDB-Verbindung herstellen
        mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        mongodb_db = os.getenv("MONGODB_DB", "valeo_neuroerp")
        
        logger.info(f"Stelle Verbindung zu MongoDB her: {mongodb_uri}, DB: {mongodb_db}")
        mongodb = APMMongoDBConnector(mongodb_uri, mongodb_db)
        await mongodb.connect()
        
        # Status abrufen
        status = await mongodb.find_one("project_status", {"phase": "IMPLEMENTATION"})
        
        if status:
            print(f"\nImplementierungsstatus:")
            print(f"Phase: {status.get('phase')}")
            print(f"Status: {status.get('status')}")
            print(f"Abschlussdatum: {status.get('completion_date')}")
            print(f"Erstellt am: {status.get('created_at')}")
            print(f"\nVollständiger Status: {json.dumps(status, indent=2, cls=MongoJSONEncoder)}")
        else:
            print("\nKein Implementierungsstatus gefunden.")
    
    except Exception as e:
        logger.error(f"Fehler bei der Überprüfung des Implementierungsstatus: {str(e)}")
        print(f"\nFehler: {str(e)}")
    
    finally:
        # MongoDB-Verbindung trennen
        if 'mongodb' in locals():
            await mongodb.disconnect()


if __name__ == "__main__":
    # Asynchrone Funktion ausführen
    asyncio.run(check_implementation_status())
