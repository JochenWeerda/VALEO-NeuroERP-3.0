#!/usr/bin/env python3
"""
Aktiviert den CREATE-Modus im APM-Framework des VALEO-NeuroERP-Systems.
Wechselt zum CREATE-Modus und führt die notwendigen Initialisierungen durch.
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

class CreateMode:
    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['valeo_neuroerp']
        self.create_collection = self.db['creative']
        
    async def activate(self):
        """Aktiviert den CREATE-Modus und speichert die Implementierungsstrategie"""
        try:
            # Aktuelle Implementierungsstrategie laden
            impl_path = Path('memory-bank/creative/implementation_sprint1.md')
            if not impl_path.exists():
                raise FileNotFoundError(f"Implementierungsstrategie nicht gefunden: {impl_path}")
            
            with open(impl_path, 'r', encoding='utf-8') as f:
                impl_content = f.read()
            
            # Implementierungsstrategie in MongoDB speichern
            impl_doc = {
                "type": "implementation_strategy",
                "date": datetime.now(),
                "content": impl_content,
                "status": "active",
                "metadata": {
                    "sprint": 1,
                    "start_date": "2025-07-08",
                    "end_date": "2025-07-12",
                    "components": [
                        "Circuit Breaker",
                        "Monitoring System",
                        "Redis Cluster",
                        "Performance Optimization"
                    ]
                }
            }
            
            result = self.create_collection.insert_one(impl_doc)
            logger.info(f"Implementierungsstrategie in MongoDB gespeichert. Document ID: {result.inserted_id}")
            
            # Status aktualisieren
            self.create_collection.update_many(
                {"_id": {"$ne": result.inserted_id}},
                {"$set": {"status": "archived"}}
            )
            
            logger.info("CREATE-Modus erfolgreich aktiviert")
            return result.inserted_id
            
        except Exception as e:
            logger.error(f"Fehler beim Aktivieren des CREATE-Modus: {str(e)}")
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


async def activate_create_mode():
    """
    Aktiviert den CREATE-Modus im APM-Framework.
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
            print("Der CREATE-Modus benötigt den RAG-Service für die Codegenerierung und Testfallerstellung.")
            print("Führen Sie 'python scripts/check_rag_service.py' aus, um den RAG-Service zu starten.\n")
            
            # Frage, ob fortgefahren werden soll
            response = input("Möchten Sie trotzdem fortfahren? (j/n): ")
            if response.lower() != "j":
                logger.info("Abbruch durch Benutzer")
                print("\nAktivierung des CREATE-Modus abgebrochen.")
                return
        
        # APM-Workflow initialisieren
        workflow = APMWorkflow(mongodb, project_id)
        
        # RAG-Service initialisieren und setzen
        rag_service = RAGService(mongodb, project_id)
        workflow.set_rag_service(rag_service)
        
        # Aktuellen Modus abrufen
        current_mode = await workflow.get_current_mode()
        logger.info(f"Aktueller Modus: {current_mode.value if current_mode else 'Nicht gesetzt'}")
        
        # Zu CREATE-Modus wechseln
        success = await workflow.switch_mode(APMMode.CREATE)
        
        if success:
            logger.info("CREATE-Modus erfolgreich aktiviert")
            
            # Überprüfen, ob ein PLAN-Ergebnis vorhanden ist
            plan_results = await mongodb.find_many("project_plans", {"project_id": project_id}, limit=1)
            
            if plan_results:
                last_plan_result = plan_results[0]
                plan_id = last_plan_result.get("_id")
                logger.info(f"Letztes PLAN-Ergebnis gefunden: {plan_id}")
                
                # Aktuelle Modus-Informationen in memory-bank/current_mode.txt speichern
                mode_info = f"""CREATE-Modus aktiviert am {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Projekt-ID: {project_id}
PLAN-Ergebnis-ID: {plan_id}
Status: Bereit zur Codegenerierung

Der CREATE-Modus konzentriert sich auf:
- Codegenerierung basierend auf dem Lösungsdesign
- Ressourcenbereitstellung für die Implementierung
- Anwendung von Entwurfsmustern
- Implementierung von Testfällen
"""
                
                with open("memory-bank/current_mode.txt", "w", encoding="utf-8") as f:
                    f.write(mode_info)
                
                logger.info("Modus-Informationen in memory-bank/current_mode.txt gespeichert")
                
                print("\n" + "=" * 80)
                print("CREATE-Modus erfolgreich aktiviert")
                print(f"Projekt-ID: {project_id}")
                print(f"PLAN-Ergebnis-ID: {plan_id}")
                print("=" * 80 + "\n")
                
                print("Der CREATE-Modus ist bereit für:")
                print("1. Codegenerierung basierend auf dem Lösungsdesign")
                print("2. Ressourcenbereitstellung für die Implementierung")
                print("3. Anwendung von Entwurfsmustern")
                print("4. Implementierung von Testfällen")
                print("\n" + "=" * 80)
            else:
                logger.warning("Kein PLAN-Ergebnis gefunden. Der CREATE-Modus benötigt ein PLAN-Ergebnis.")
                print("\nWARNUNG: Kein PLAN-Ergebnis gefunden.")
                print("Der CREATE-Modus benötigt ein PLAN-Ergebnis als Grundlage.")
                print("Führen Sie zuerst den PLAN-Modus aus: python scripts/activate_plan_mode.py")
                
                # Aktuelle Modus-Informationen trotzdem in memory-bank/current_mode.txt speichern
                mode_info = f"""CREATE-Modus aktiviert am {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Projekt-ID: {project_id}
Status: Kein PLAN-Ergebnis gefunden

Der CREATE-Modus konzentriert sich auf:
- Codegenerierung basierend auf dem Lösungsdesign
- Ressourcenbereitstellung für die Implementierung
- Anwendung von Entwurfsmustern
- Implementierung von Testfällen

Hinweis: Es wurde kein PLAN-Ergebnis gefunden. Der CREATE-Modus benötigt ein PLAN-Ergebnis als Grundlage.
"""
                
                with open("memory-bank/current_mode.txt", "w", encoding="utf-8") as f:
                    f.write(mode_info)
                
                logger.info("Modus-Informationen in memory-bank/current_mode.txt gespeichert")
        else:
            logger.error("Fehler beim Aktivieren des CREATE-Modus")
            print("\nFehler: CREATE-Modus konnte nicht aktiviert werden.")
    
    except Exception as e:
        logger.error(f"Fehler beim Aktivieren des CREATE-Modus: {str(e)}")
        print(f"\nFehler: {str(e)}")
    
    finally:
        # MongoDB-Verbindung trennen
        if 'mongodb' in locals():
            await mongodb.disconnect()

async def main():
    create_mode = CreateMode()
    await create_mode.activate()

if __name__ == "__main__":
    asyncio.run(main()) 