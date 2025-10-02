#!/usr/bin/env python3
"""
Zeigt die mit OpenAI erstellte Zusammenfassung des Handover-Dokuments an.
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime
from bson import ObjectId

# Pfad zum Projektverzeichnis hinzufügen
sys.path.append(str(Path(__file__).resolve().parent.parent))

from backend.apm_framework.mongodb_connector import APMMongoDBConnector

# Logger konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Hauptfunktion zum Anzeigen der OpenAI-Zusammenfassung des Handover-Dokuments."""
    try:
        # MongoDB-Verbindung herstellen
        mongodb_connector = APMMongoDBConnector("mongodb://localhost:27017/", "valeo_neuroerp")
        
        # Neuestes Handover-Dokument abrufen
        handovers = mongodb_connector.find_many("handovers", {}, sort=[("timestamp", -1)], limit=1)
        
        if not handovers:
            logger.info("Keine Handover-Dokumente gefunden")
            return
        
        handover = handovers[0]
        
        # Metadaten ausgeben
        print("\n" + "="*50)
        print(f"Handover-Dokument (ID: {handover['_id']})")
        print(f"Zeitstempel: {handover['timestamp']}")
        print(f"Status: {handover.get('status', 'Unbekannt')}")
        print(f"Quelle: {handover.get('source_file', 'Unbekannt')}")
        print(f"Projekt-ID: {handover.get('project_id', 'Nicht zugeordnet')}")
        print("="*50 + "\n")
        
        # Zusammenfassung ausgeben
        print("OPENAI-ZUSAMMENFASSUNG:")
        print("-"*50)
        summary = handover.get('summary', 'Keine Zusammenfassung verfügbar')
        print(summary)
        print("-"*50 + "\n")
        
        # Verbindung schließen
        mongodb_connector.close()
        print("MongoDB-Verbindung geschlossen")
        
    except Exception as e:
        logger.error(f"Fehler beim Anzeigen der Zusammenfassung: {str(e)}")
        raise

if __name__ == "__main__":
    main() 