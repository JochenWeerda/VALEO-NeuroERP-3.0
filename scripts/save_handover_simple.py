#!/usr/bin/env python3
"""
Speichert das aktuelle Handover-Dokument in MongoDB (vereinfachte Version ohne MCP).
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# Pfad zum Projektverzeichnis hinzufügen
sys.path.append(str(Path(__file__).resolve().parent.parent))

from backend.apm_framework.mongodb_connector import APMMongoDBConnector

# Logger konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleHandoverProcessor:
    def __init__(self, mongodb_uri="mongodb://localhost:27017/", db_name="valeo_neuroerp"):
        """Initialisiert den HandoverProcessor mit MongoDB-Verbindung."""
        self.mongodb_connector = APMMongoDBConnector(mongodb_uri, db_name)
        
        # Projekt-ID abrufen oder erstellen
        project = self.mongodb_connector.find_one("projects", {"name": "VALEO-NeuroERP"})
        if not project:
            project_id = self.mongodb_connector.insert_one("projects", {
                "name": "VALEO-NeuroERP",
                "description": "Neuromorphes ERP-System mit KI-Integration",
                "created_at": datetime.now()
            })
            self.project_id = project_id
        else:
            self.project_id = project["_id"]
        
    def process_handover(self, handover_file_path):
        """Verarbeitet das Handover-Dokument und speichert es in MongoDB."""
        try:
            # Handover-Dokument einlesen
            handover_path = Path(handover_file_path)
            if not handover_path.exists():
                raise FileNotFoundError(f"Handover-Datei nicht gefunden: {handover_file_path}")
            
            with open(handover_path, "r", encoding="utf-8") as f:
                handover_content = f.read()
            
            logger.info(f"Handover-Dokument aus {handover_file_path} eingelesen")
            
            # Einfache Zusammenfassung extrahieren (erste 200 Zeichen)
            summary = handover_content[:200] + "..." if len(handover_content) > 200 else handover_content
            
            # Handover-Metadaten erstellen
            handover_data = {
                "content": handover_content,
                "summary": summary,
                "timestamp": datetime.now(),
                "source_file": str(handover_path),
                "status": "active",
                "project_id": self.project_id
            }
            
            # In MongoDB speichern
            handover_id = self.mongodb_connector.db["handovers"].insert_one(handover_data)
            logger.info(f"Handover in MongoDB gespeichert mit ID: {handover_id.inserted_id}")
            
            # Referenz im Projekt-Dokument aktualisieren
            self.mongodb_connector.db["projects"].update_one(
                {"_id": self.project_id},
                {"$set": {"current_handover_id": handover_id.inserted_id}}
            )
            
            return handover_id.inserted_id
            
        except Exception as e:
            logger.error(f"Fehler bei der Verarbeitung des Handover-Dokuments: {str(e)}")
            raise
    
    def close(self):
        """Schließt die MongoDB-Verbindung."""
        self.mongodb_connector.close()
        logger.info("MongoDB-Verbindung geschlossen")

def main():
    """Hauptfunktion zum Speichern des Handover-Dokuments in MongoDB."""
    try:
        # HandoverProcessor initialisieren
        processor = SimpleHandoverProcessor()
        
        # Pfad zum aktuellen Handover-Dokument
        handover_path = Path(__file__).resolve().parent.parent / "memory-bank" / "handover" / "current-handover.md"
        
        # Handover verarbeiten und in MongoDB speichern
        handover_id = processor.process_handover(handover_path)
        logger.info(f"Handover erfolgreich verarbeitet und in MongoDB gespeichert (ID: {handover_id})")
        
        # Verbindung schließen
        processor.close()
        
    except Exception as e:
        logger.error(f"Fehler beim Speichern des Handover-Dokuments: {str(e)}")
        raise

if __name__ == "__main__":
    main() 