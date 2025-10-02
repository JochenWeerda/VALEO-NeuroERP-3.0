#!/usr/bin/env python3
"""
Handover-Generator für das APM-Framework.
Generiert Handover-Dokumente zwischen verschiedenen Phasen des APM-Workflows.
"""

import os
import sys
import logging
import asyncio
import argparse
from pathlib import Path
from datetime import datetime

# Pfad zum Projektverzeichnis hinzufügen
sys.path.append(str(Path(__file__).resolve().parent.parent))

from backend.apm_framework.handover_manager import HandoverManager

# Logger konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def generate_handover(phase: str, content_file: str = None) -> str:
    """
    Generiert ein Handover-Dokument für die angegebene Phase.
    
    Args:
        phase: Phase des APM-Workflows (VAN, PLAN, CREATE, IMPLEMENT, REFLECT)
        content_file: Pfad zu einer JSON-Datei mit Inhalt für das Handover-Dokument
        
    Returns:
        Pfad zum erstellten Handover-Dokument
    """
    try:
        # HandoverManager initialisieren
        manager = HandoverManager()
        
        # Inhalt für das Handover-Dokument
        content = {}
        
        # Wenn eine Inhaltsdatei angegeben wurde, diese laden
        if content_file:
            import json
            with open(content_file, "r", encoding="utf-8") as f:
                content = json.load(f)
        else:
            # Standardinhalt für das Handover-Dokument
            content = {
                "Beschreibung": "Automatisch generiertes Handover-Dokument",
                "Prozent": "0%",
                "Liste": "Keine Probleme",
                "Datei 1": "scripts/handover_generator.py",
                "Datei 2": "backend/apm_framework/handover_manager.py",
                "Details": f"{phase}-Modus mit MongoDB-Verbindung",
                "Text": f"Automatisch generiertes Handover-Dokument für Phase {phase}",
                "Prioritäre Aufgabe 1": "Handover-Dokument überprüfen",
                "Prioritäre Aufgabe 2": "Nächste Schritte planen",
                "Prioritäre Aufgabe 3": "Implementierung fortsetzen",
                "Version": "3.11",
                "Liste": "MongoDB (localhost:27017)",
                "Agent-Name/Rolle": "Handover-Generator",
                "Zusammenfassung der letzten Konversation und wichtige Entscheidungen": f"Automatisch generiertes Handover-Dokument für Phase {phase}"
            }
            
            # Phasenspezifische Inhalte
            if phase == HandoverManager.PHASE_VAN:
                content.update({
                    "Anforderung 1": "Anforderungsanalyse durchführen",
                    "Anforderung 2": "Klärungsfragen sammeln",
                    "Frage 1": "Welche Funktionen haben höchste Priorität?",
                    "Frage 2": "Welche technischen Einschränkungen gibt es?"
                })
            elif phase == HandoverManager.PHASE_PLAN:
                content.update({
                    "Entscheidung 1": "Architekturentscheidung 1",
                    "Entscheidung 2": "Architekturentscheidung 2",
                    "Ressource 1": "Ressource 1",
                    "Ressource 2": "Ressource 2",
                    "Meilenstein 1": "Meilenstein 1",
                    "Meilenstein 2": "Meilenstein 2"
                })
        
        # Handover-Dokument erstellen
        handover_path = manager.create_handover_document(phase, content)
        logger.info(f"Handover-Dokument erstellt: {handover_path}")
        
        # Handover-Dokument in MongoDB speichern
        handover_id = await manager.save_to_mongodb(handover_path)
        logger.info(f"Handover-Dokument in MongoDB gespeichert mit ID: {handover_id}")
        
        # Neuestes Handover-Dokument abrufen und anzeigen
        latest_handover = manager.get_latest_handover()
        
        if latest_handover:
            print(f"\nNeuestes Handover-Dokument (ID: {latest_handover['_id']}):")
            print(f"Zeitstempel: {latest_handover['timestamp']}")
            print(f"Status: {latest_handover.get('status', 'Unbekannt')}")
            print("\nZusammenfassung:")
            print(latest_handover.get('summary', 'Keine Zusammenfassung verfügbar'))
            
            # Handover-Dokument als JSON exportieren
            import json
            output_dir = Path(__file__).resolve().parent.parent / "memory-bank" / "handover"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            output_path = output_dir / "latest_handover.json"
            with open(output_path, "w", encoding="utf-8") as f:
                # ObjectId in String umwandeln
                latest_handover_copy = dict(latest_handover)
                latest_handover_copy["_id"] = str(latest_handover_copy["_id"])
                latest_handover_copy["project_id"] = str(latest_handover_copy["project_id"])
                latest_handover_copy["timestamp"] = latest_handover_copy["timestamp"].isoformat()
                
                json.dump(latest_handover_copy, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Handover-Dokument als JSON exportiert: {output_path}")
        
        # Verbindung schließen
        manager.close()
        
        return handover_path
        
    except Exception as e:
        logger.error(f"Fehler bei der Generierung des Handover-Dokuments: {str(e)}")
        raise

def main():
    """Hauptfunktion für die Kommandozeile."""
    parser = argparse.ArgumentParser(description="Handover-Generator für das APM-Framework")
    parser.add_argument("--phase", "-p", type=str, default=HandoverManager.PHASE_VAN,
                        choices=[HandoverManager.PHASE_VAN, HandoverManager.PHASE_PLAN, 
                                HandoverManager.PHASE_CREATE, HandoverManager.PHASE_IMPLEMENT, 
                                HandoverManager.PHASE_REFLECT],
                        help="Phase des APM-Workflows")
    parser.add_argument("--content", "-c", type=str, 
                        help="Pfad zu einer JSON-Datei mit Inhalt für das Handover-Dokument")
    
    args = parser.parse_args()
    
    # Handover-Dokument generieren
    asyncio.run(generate_handover(args.phase, args.content))

if __name__ == "__main__":
    main() 