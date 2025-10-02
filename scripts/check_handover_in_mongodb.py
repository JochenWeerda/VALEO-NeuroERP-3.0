#!/usr/bin/env python3
"""
Überprüft, ob das Handover-Dokument in MongoDB gespeichert wurde.
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime
from pprint import pprint

# Pfad zum Projektverzeichnis hinzufügen
sys.path.append(str(Path(__file__).resolve().parent.parent))

from backend.apm_framework.mongodb_connector import APMMongoDBConnector

# Logger konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Hauptfunktion zum Überprüfen des Handover-Dokuments in MongoDB."""
    try:
        # MongoDB-Verbindung herstellen
        mongodb_connector = APMMongoDBConnector("mongodb://localhost:27017/", "valeo_neuroerp")
        
        # Alle Projekte anzeigen
        projects = mongodb_connector.find_many("projects", {})
        logger.info(f"Gefundene Projekte: {len(projects)}")
        for project in projects:
            logger.info(f"Projekt: {project['_id']} - {project.get('name', 'Unbenannt')}")
        
        # Alle Handover-Dokumente abrufen, unabhängig vom Projekt
        handovers = mongodb_connector.find_many("handovers", {})
        
        if not handovers:
            logger.info("Keine Handover-Dokumente gefunden")
            return
        
        logger.info(f"{len(handovers)} Handover-Dokumente gefunden")
        
        # Alle Handover-Dokumente anzeigen
        for i, handover in enumerate(handovers, 1):
            logger.info(f"Handover {i} (ID: {handover['_id']}):")
            logger.info(f"  Zeitstempel: {handover['timestamp']}")
            logger.info(f"  Status: {handover.get('status', 'Unbekannt')}")
            logger.info(f"  Quelle: {handover.get('source_file', 'Unbekannt')}")
            logger.info(f"  Projekt-ID: {handover.get('project_id', 'Nicht zugeordnet')}")
            summary = handover.get('summary', 'Keine Zusammenfassung')
            logger.info(f"  Zusammenfassung: {summary[:100]}..." if len(summary) > 100 else summary)
            logger.info("---")
        
        # Verbindung schließen
        mongodb_connector.close()
        logger.info("MongoDB-Verbindung geschlossen")
        
    except Exception as e:
        logger.error(f"Fehler beim Überprüfen des Handover-Dokuments: {str(e)}")
        raise

if __name__ == "__main__":
    main() 