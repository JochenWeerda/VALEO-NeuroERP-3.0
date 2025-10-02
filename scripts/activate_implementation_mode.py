#!/usr/bin/env python3
"""
Aktiviert den IMPLEMENTATION-Modus im APM-Framework des VALEO-NeuroERP-Systems.
Wechselt zum IMPLEMENTATION-Modus und führt die notwendigen Initialisierungen durch.
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
from pymongo import MongoClient
from pathlib import Path
import json

# Pfad zum Projekt-Root hinzufügen
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.apm_framework.mongodb_connector import APMMongoDBConnector
from backend.apm_framework.apm_workflow import APMWorkflow, APMMode
from backend.apm_framework.rag_service import RAGService

# Logger konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ImplementationMode:
    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['valeo_neuroerp']
        self.impl_collection = self.db['implementations']
        
    async def activate(self):
        """Aktiviert den IMPLEMENTATION-Modus und dokumentiert die Implementierung"""
        try:
            # Implementierte Komponenten dokumentieren
            impl_doc = {
                "type": "implementation",
                "date": datetime.now(),
                "status": "active",
                "components": {
                    "circuit_breaker": {
                        "files": [
                            "backend/services/circuit_breaker.py",
                            "backend/services/transaction_service.py"
                        ],
                        "features": [
                            "Zustandsverwaltung (OPEN/HALF-OPEN/CLOSED)",
                            "Redis-basierte Verteilung",
                            "Prometheus Metriken",
                            "Automatische Wiederherstellung",
                            "Konfigurierbare Schwellenwerte"
                        ],
                        "status": "implemented"
                    }
                },
                "metadata": {
                    "sprint": 1,
                    "implementation_date": "2025-07-08",
                    "tested": False,
                    "deployed": False
                }
            }
            
            result = self.impl_collection.insert_one(impl_doc)
            logger.info(f"Implementierung in MongoDB gespeichert. Document ID: {result.inserted_id}")
            
            # Status aktualisieren
            self.impl_collection.update_many(
                {"_id": {"$ne": result.inserted_id}},
                {"$set": {"status": "archived"}}
            )
            
            logger.info("IMPLEMENTATION-Modus erfolgreich aktiviert")
            return result.inserted_id
            
        except Exception as e:
            logger.error(f"Fehler beim Aktivieren des IMPLEMENTATION-Modus: {str(e)}")
            raise

async def check_rag_service(mongodb, project_id):
    """
    Überprüft, ob der RAG-Service läuft und korrekt konfiguriert ist.
    
    Args:
        mongodb: MongoDB-Connector
        project_id: Projekt-ID
        
    Returns:
        bool: True, wenn der RAG-Service läuft, False sonst
    """
    try:
        # RAG-Service initialisieren
        rag_service = RAGService(mongodb, project_id)
        
        # Testabfrage durchführen
        result = await rag_service.rag_query("Test RAG-Service")
        
        if result and "response" in result:
            logger.info("RAG-Service läuft und antwortet auf Abfragen")
            return True
        else:
            logger.warning("RAG-Service läuft, antwortet aber nicht korrekt auf Abfragen")
            return False
    except Exception as e:
        logger.error(f"Fehler bei der Überprüfung des RAG-Services: {str(e)}")
        return False


async def activate_implementation_mode():
    """
    Aktiviert den IMPLEMENTATION-Modus im APM-Framework.
    """
    try:
        # MongoDB-Verbindung herstellen
        mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        mongodb_db = os.getenv("MONGODB_DB", "valeo_neuroerp")
        
        logger.info(f"Stelle Verbindung zu MongoDB her: {mongodb_uri}, DB: {mongodb_db}")
        mongodb = APMMongoDBConnector(mongodb_uri, mongodb_db)
        await mongodb.connect()
        
        # Projekt-ID festlegen (kann auch aus der Umgebung oder als Parameter übergeben werden)
        project_id = os.getenv("PROJECT_ID", "valeo_neuroerp_project")
        
        # RAG-Service überprüfen
        logger.info("Überprüfe RAG-Service...")
        rag_service_running = await check_rag_service(mongodb, project_id)
        
        if not rag_service_running:
            logger.warning("RAG-Service ist nicht verfügbar oder antwortet nicht korrekt.")
            print("\nWARNUNG: Der RAG-Service ist nicht verfügbar oder antwortet nicht korrekt.")
            print("Der IMPLEMENTATION-Modus benötigt den RAG-Service für die Implementierungsunterstützung.")
            print("Führen Sie 'python scripts/check_rag_service.py' aus, um den RAG-Service zu starten.\n")
            
            # Frage, ob fortgefahren werden soll
            response = input("Möchten Sie trotzdem fortfahren? (j/n): ")
            if response.lower() != "j":
                logger.info("Abbruch durch Benutzer")
                print("\nAktivierung des IMPLEMENTATION-Modus abgebrochen.")
                return
        
        # APM-Workflow initialisieren
        workflow = APMWorkflow(mongodb, project_id)
        
        # RAG-Service initialisieren und setzen
        rag_service = RAGService(mongodb, project_id)
        workflow.set_rag_service(rag_service)
        
        # Aktuellen Modus abrufen
        current_mode = await workflow.get_current_mode()
        logger.info(f"Aktueller Modus: {current_mode.value if current_mode else 'Nicht gesetzt'}")
        
        # Zu IMPLEMENTATION-Modus wechseln
        success = await workflow.switch_mode(APMMode.IMPLEMENTATION)
        
        if success:
            logger.info("IMPLEMENTATION-Modus erfolgreich aktiviert")
            
            # Überprüfen, ob ein CREATE-Ergebnis vorhanden ist
            create_results = await mongodb.find_many("create_results", {"project_id": project_id}, limit=1)
            
            if create_results:
                last_create_result = create_results[0]
                create_id = last_create_result.get("_id")
                logger.info(f"Letztes CREATE-Ergebnis gefunden: {create_id}")
                
                # Aktuelle Modus-Informationen in memory-bank/current_mode.txt speichern
                mode_info = f"""IMPLEMENTATION-Modus aktiviert am {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Projekt-ID: {project_id}
CREATE-Ergebnis-ID: {create_id}
Status: Bereit zur Implementierung

Der IMPLEMENTATION-Modus konzentriert sich auf:
- Implementierung der generierten Code-Artefakte
- Konfiguration und Deployment
- Continuous Integration und Continuous Deployment
- Qualitätssicherung und Tests
"""
                
                with open("memory-bank/current_mode.txt", "w", encoding="utf-8") as f:
                    f.write(mode_info)
                
                logger.info("Modus-Informationen in memory-bank/current_mode.txt gespeichert")
                
                # Handover-Dokument erstellen
                handover_info = f"""# IMPLEMENTATION-Modus Handover

## Aktueller Status
- **Modus**: IMPLEMENTATION
- **Projekt-ID**: {project_id}
- **CREATE-Ergebnis-ID**: {create_id}
- **Datum**: {datetime.now().strftime('%Y-%m-%d')}

## Abgeschlossene Aufgaben
1. **CREATE-Modus abgeschlossen**: Code-Artefakte, Ressourcenanforderungen, Entwurfsmuster und Testfälle wurden generiert.
2. **IMPLEMENTATION-Modus aktiviert**: Bereit für die Implementierung der generierten Code-Artefakte.

## Nächste Schritte
1. **Code-Artefakte implementieren**: Die generierten Code-Artefakte in das Projekt integrieren.
2. **Konfiguration und Deployment**: Die Anwendung konfigurieren und deployen.
3. **CI/CD einrichten**: Continuous Integration und Continuous Deployment einrichten.
4. **Tests ausführen**: Die generierten Testfälle ausführen und die Qualität sicherstellen.

## Technische Details
- Die CREATE-Ergebnisse sind in der MongoDB in der Collection `create_results` gespeichert.
- Die generierten Code-Artefakte sind in der Collection `code_artifacts` gespeichert.
- Die generierten Ressourcenanforderungen sind in der Collection `resource_requirements` gespeichert.
- Die generierten Entwurfsmuster sind in der Collection `design_patterns` gespeichert.
- Die generierten Testfälle sind in der Collection `test_cases` gespeichert.
"""
                
                with open("memory-bank/handover/current-handover.md", "w", encoding="utf-8") as f:
                    f.write(handover_info)
                
                logger.info("Handover-Dokument in memory-bank/handover/current-handover.md gespeichert")
                
                print("\n" + "=" * 80)
                print("IMPLEMENTATION-Modus erfolgreich aktiviert")
                print(f"Projekt-ID: {project_id}")
                print(f"CREATE-Ergebnis-ID: {create_id}")
                print("=" * 80 + "\n")
                
                print("Der IMPLEMENTATION-Modus ist bereit für:")
                print("1. Implementierung der generierten Code-Artefakte")
                print("2. Konfiguration und Deployment")
                print("3. Continuous Integration und Continuous Deployment")
                print("4. Qualitätssicherung und Tests")
                print("\n" + "=" * 80)
            else:
                logger.warning("Kein CREATE-Ergebnis gefunden. Der IMPLEMENTATION-Modus benötigt ein CREATE-Ergebnis.")
                print("\nWARNUNG: Kein CREATE-Ergebnis gefunden.")
                print("Der IMPLEMENTATION-Modus benötigt ein CREATE-Ergebnis als Grundlage.")
                print("Führen Sie zuerst den CREATE-Modus aus: python scripts/activate_create_mode.py")
                
                # Aktuelle Modus-Informationen trotzdem in memory-bank/current_mode.txt speichern
                mode_info = f"""IMPLEMENTATION-Modus aktiviert am {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Projekt-ID: {project_id}
Status: Kein CREATE-Ergebnis gefunden

Der IMPLEMENTATION-Modus konzentriert sich auf:
- Implementierung der generierten Code-Artefakte
- Konfiguration und Deployment
- Continuous Integration und Continuous Deployment
- Qualitätssicherung und Tests

Hinweis: Es wurde kein CREATE-Ergebnis gefunden. Der IMPLEMENTATION-Modus benötigt ein CREATE-Ergebnis als Grundlage.
"""
                
                with open("memory-bank/current_mode.txt", "w", encoding="utf-8") as f:
                    f.write(mode_info)
                
                logger.info("Modus-Informationen in memory-bank/current_mode.txt gespeichert")
        else:
            logger.error("Fehler beim Aktivieren des IMPLEMENTATION-Modus")
            print("\nFehler: IMPLEMENTATION-Modus konnte nicht aktiviert werden.")
    
    except Exception as e:
        logger.error(f"Fehler beim Aktivieren des IMPLEMENTATION-Modus: {str(e)}")
        print(f"\nFehler: {str(e)}")
    
    finally:
        # MongoDB-Verbindung trennen
        if 'mongodb' in locals():
            await mongodb.disconnect()

async def main():
    impl_mode = ImplementationMode()
    await impl_mode.activate()

if __name__ == "__main__":
    asyncio.run(main()) 