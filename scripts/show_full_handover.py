#!/usr/bin/env python3
"""
Zeigt das vollständige Handover-Dokument aus MongoDB an.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from bson import ObjectId, json_util

# Pfad zum Projektverzeichnis hinzufügen
sys.path.append(str(Path(__file__).resolve().parent.parent))

from backend.apm_framework.mongodb_connector import APMMongoDBConnector

def parse_json(data):
    """Konvertiert MongoDB-Dokumente in JSON-Strings."""
    return json.loads(json_util.dumps(data))

def main():
    """Hauptfunktion zum Anzeigen des vollständigen Handover-Dokuments."""
    try:
        # MongoDB-Verbindung herstellen
        mongodb_connector = APMMongoDBConnector("mongodb://localhost:27017/", "valeo_neuroerp")
        
        # Neuestes Handover-Dokument abrufen
        handovers = mongodb_connector.find_many("handovers", {}, sort=[("timestamp", -1)], limit=1)
        
        if not handovers:
            print("Keine Handover-Dokumente gefunden")
            return
        
        handover = handovers[0]
        
        # Vollständiges Dokument ausgeben
        print("\n" + "="*50)
        print("VOLLSTÄNDIGES HANDOVER-DOKUMENT")
        print("="*50 + "\n")
        
        # Inhalt ausgeben
        print("INHALT:")
        print("-"*50)
        print(handover.get('content', 'Kein Inhalt verfügbar'))
        print("-"*50 + "\n")
        
        # Zusammenfassung ausgeben
        print("ZUSAMMENFASSUNG:")
        print("-"*50)
        print(handover.get('summary', 'Keine Zusammenfassung verfügbar'))
        print("-"*50 + "\n")
        
        # Vollständiges Dokument als JSON speichern
        output_file = Path(__file__).resolve().parent.parent / "handover_document.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(parse_json(handover), f, indent=2, ensure_ascii=False)
        
        print(f"Vollständiges Dokument als JSON gespeichert in: {output_file}")
        
        # Verbindung schließen
        mongodb_connector.close()
        print("MongoDB-Verbindung geschlossen")
        
    except Exception as e:
        print(f"Fehler beim Anzeigen des Handover-Dokuments: {str(e)}")
        raise

if __name__ == "__main__":
    main() 