#!/usr/bin/env python
"""
Skript zum Aktivieren des VAN-Modus und Speichern der Ergebnisse.
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime
from pathlib import Path

# Pfade konfigurieren
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

try:
    from backend.apm_framework.van_mode import VANMode
    from backend.apm_framework.mongodb_connector import APMMongoDBConnector
    from backend.apm_framework.rag_service import RAGService
except ImportError:
    print("Fehler beim Importieren der erforderlichen Module.")
    print("Stellen Sie sicher, dass Sie sich im Projektverzeichnis befinden.")
    sys.exit(1)

# Logger konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("activate_van_phase")

async def main():
    """Hauptfunktion zum Aktivieren des VAN-Modus und Speichern der Ergebnisse."""
    
    # Konfiguration laden
    logger.info("VAN-Phase wird aktiviert...")
    
    # MongoDB-Verbindung herstellen
    try:
        mongodb_uri = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/")
        db_name = os.environ.get("MONGODB_DB", "valeo_neuroerp")
        
        logger.info(f"Verbindung zu MongoDB wird hergestellt: {mongodb_uri}")
        mongodb = APMMongoDBConnector(mongodb_uri, db_name)
        
        # Projekt-ID festlegen oder aus der Umgebung laden
        project_id = os.environ.get("PROJECT_ID", "valero_neuroerp_project")
        
        # VAN-Modus initialisieren
        logger.info(f"VAN-Modus wird für Projekt {project_id} initialisiert...")
        van_mode = VANMode(mongodb, project_id)
        
        # RAG-Service initialisieren
        logger.info("RAG-Service wird initialisiert...")
        rag_service = RAGService()
        van_mode.set_rag_service(rag_service)
        
        # Anforderungstext aus Datei laden oder als Parameter übergeben
        requirement_file = os.environ.get("REQUIREMENT_FILE", "memory-bank/tasks/van_phase/requirements.txt")
        
        if os.path.exists(requirement_file):
            with open(requirement_file, "r", encoding="utf-8") as f:
                requirement_text = f.read()
        else:
            requirement_text = """
            VALERO-NeuroERP ist ein vollständiges ERP-System, das ERP, CRM, Kassenprogramm, FIBU und BI integriert.
            Das System soll auf dem GENXAIS-Framework basieren und alle notwendigen Module für ein modernes ERP-System bereitstellen.
            """
            # Anforderungsdatei erstellen
            os.makedirs(os.path.dirname(requirement_file), exist_ok=True)
            with open(requirement_file, "w", encoding="utf-8") as f:
                f.write(requirement_text)
        
        # VAN-Modus ausführen
        logger.info("VAN-Modus wird ausgeführt...")
        result = await van_mode.run(requirement_text)
        
        # Ergebnisse speichern
        results_dir = os.path.join(PROJECT_ROOT, "memory-bank", "tasks", "van_phase", "results")
        os.makedirs(results_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = os.path.join(results_dir, f"van_result_{timestamp}.json")
        
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, default=str)
        
        logger.info(f"VAN-Modus-Ergebnisse wurden in {result_file} gespeichert.")
        
        # Status in current_mode.txt speichern
        mode_file = os.path.join(PROJECT_ROOT, "memory-bank", "current_mode.txt")
        with open(mode_file, "w", encoding="utf-8") as f:
            f.write("VAN")
        
        logger.info("VAN-Phase wurde erfolgreich aktiviert.")
        
        # Verbindung schließen
        mongodb.close()
        
        return 0
        
    except Exception as e:
        logger.error(f"Fehler bei der Ausführung des VAN-Modus: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main())) 