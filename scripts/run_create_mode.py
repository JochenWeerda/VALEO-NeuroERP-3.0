#!/usr/bin/env python3
"""
Führt den CREATE-Modus autonom aus und erstellt Ergebnisse für den IMPLEMENTATION-Modus.
"""

import os
import sys
import asyncio
import logging
from datetime import datetime

# Pfad zum Projekt-Root hinzufügen
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.apm_framework.mongodb_connector import APMMongoDBConnector
from backend.apm_framework.apm_workflow import APMWorkflow, APMMode
from backend.apm_framework.rag_service import RAGService

# Logger konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


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


async def run_create_mode():
    """
    Führt den CREATE-Modus autonom aus.
    """
    try:
        # MongoDB-Verbindung herstellen
        mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        mongodb_db = os.getenv("MONGODB_DB", "valeo_neuroerp")
        
        logger.info(f"Stelle Verbindung zu MongoDB her: {mongodb_uri}, DB: {mongodb_db}")
        mongodb = APMMongoDBConnector(mongodb_uri, mongodb_db)
        await mongodb.connect()
        
        # Projekt-ID festlegen
        project_id = os.getenv("PROJECT_ID", "valeo_neuroerp_project")
        
        # RAG-Service überprüfen
        logger.info("Überprüfe RAG-Service...")
        rag_service_running = await check_rag_service(mongodb, project_id)
        
        if not rag_service_running:
            logger.warning("RAG-Service ist nicht verfügbar oder antwortet nicht korrekt.")
            print("\nWARNUNG: Der RAG-Service ist nicht verfügbar oder antwortet nicht korrekt.")
            print("Der CREATE-Modus benötigt den RAG-Service für die Codegenerierung und Testfallerstellung.")
            print("Führen Sie 'python -m backend.apm_framework.rag_service_server' aus, um den RAG-Service zu starten.\n")
            
            # Frage, ob fortgefahren werden soll
            response = input("Möchten Sie trotzdem fortfahren? (j/n): ")
            if response.lower() != "j":
                logger.info("Abbruch durch Benutzer")
                print("\nAusführung des CREATE-Modus abgebrochen.")
                return
        
        # APM-Workflow initialisieren
        workflow = APMWorkflow(mongodb, project_id)
        
        # RAG-Service initialisieren und setzen
        rag_service = RAGService(mongodb, project_id)
        workflow.set_rag_service(rag_service)
        
        # Aktuellen Modus abrufen
        current_mode = await workflow.get_current_mode()
        logger.info(f"Aktueller Modus: {current_mode.value if current_mode else 'Nicht gesetzt'}")
        
        # Zu CREATE-Modus wechseln, falls noch nicht aktiv
        if current_mode != APMMode.CREATE:
            success = await workflow.switch_mode(APMMode.CREATE)
            if success:
                logger.info("CREATE-Modus erfolgreich aktiviert")
            else:
                logger.error("Fehler beim Aktivieren des CREATE-Modus")
                print("\nFehler: CREATE-Modus konnte nicht aktiviert werden.")
                return
        
        # Neuesten Projektplan mit Lösungsdesign-ID abrufen
        project_plans = await mongodb.find_many("project_plans", 
                                              {"project_id": project_id, "solution_design_id": {"$ne": None}}, 
                                              sort_field="updated_at", sort_order=-1, limit=1)
        
        if project_plans:
            plan = project_plans[0]
            plan_id = plan.get("_id")
            logger.info(f"Projektplan gefunden: {plan_id}")
            logger.info(f"Lösungsdesign-ID: {plan.get('solution_design_id')}")
            
            print("\n" + "=" * 80)
            print(f"Führe CREATE-Modus mit PLAN-ID {plan_id} aus...")
            print("=" * 80 + "\n")
            
            # CREATE-Modus ausführen
            try:
                start_time = datetime.now()
                result = await workflow.create_mode.run(plan_id)
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                result_id = result.get("id")
                logger.info(f"CREATE-Modus erfolgreich ausgeführt. Ergebnis-ID: {result_id}")
                
                # Aktuelle Modus-Informationen in memory-bank/current_mode.txt speichern
                mode_info = f"""CREATE-Modus ausgeführt am {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Projekt-ID: {project_id}
PLAN-Ergebnis-ID: {plan_id}
CREATE-Ergebnis-ID: {result_id}
Ausführungsdauer: {duration:.2f} Sekunden
Status: Abgeschlossen

Der CREATE-Modus hat folgende Artefakte erstellt:
- Code-Artefakte: {len(result.get("code_artifacts", []))}
- Ressourcenanforderungen: {len(result.get("resource_requirements", []))}
- Entwurfsmuster: {len(result.get("design_patterns", []))}
- Testfälle: {len(result.get("test_cases", []))}
"""
                
                with open("memory-bank/current_mode.txt", "w", encoding="utf-8") as f:
                    f.write(mode_info)
                
                logger.info("Modus-Informationen in memory-bank/current_mode.txt gespeichert")
                
                # Handover-Dokument erstellen
                handover_info = f"""# CREATE-Modus Handover

## Aktueller Status
- **Modus**: CREATE
- **Projekt-ID**: {project_id}
- **PLAN-Ergebnis-ID**: {plan_id}
- **CREATE-Ergebnis-ID**: {result_id}
- **Datum**: {datetime.now().strftime('%Y-%m-%d')}
- **Ausführungsdauer**: {duration:.2f} Sekunden

## Erstellte Artefakte
1. **Code-Artefakte**: {len(result.get("code_artifacts", []))} erstellt
   - Sprachen: {", ".join(set([artifact.get("language", "Unbekannt") for artifact in result.get("code_artifacts", [])]))}
   - Typen: {", ".join(set([artifact.get("type", "Unbekannt") for artifact in result.get("code_artifacts", [])]))}

2. **Ressourcenanforderungen**: {len(result.get("resource_requirements", []))} erstellt
   - Typen: {", ".join(set([req.get("type", "Unbekannt") for req in result.get("resource_requirements", [])]))}

3. **Entwurfsmuster**: {len(result.get("design_patterns", []))} angewendet
   - Kategorien: {", ".join(set([pattern.get("category", "Unbekannt") for pattern in result.get("design_patterns", [])]))}

4. **Testfälle**: {len(result.get("test_cases", []))} erstellt
   - Typen: {", ".join(set([test.get("type", "Unbekannt") for test in result.get("test_cases", [])]))}

## Nächste Schritte
1. **Zum IMPLEMENTATION-Modus wechseln**: Mit dem Befehl `python scripts/activate_implementation_mode.py` zum IMPLEMENTATION-Modus wechseln.
2. **Code-Artefakte implementieren**: Die generierten Code-Artefakte in das Projekt integrieren.
3. **Ressourcen bereitstellen**: Die identifizierten Ressourcen für die Implementierung bereitstellen.
4. **Tests ausführen**: Die generierten Testfälle ausführen und die Qualität sicherstellen.

## Technische Details
- Die Ergebnisse des CREATE-Modus sind in der MongoDB in der Collection `create_results` gespeichert.
- Die generierten Code-Artefakte sind in der Collection `code_artifacts` gespeichert.
- Die generierten Ressourcenanforderungen sind in der Collection `resource_requirements` gespeichert.
- Die angewendeten Entwurfsmuster sind in der Collection `design_patterns` gespeichert.
- Die generierten Testfälle sind in der Collection `test_cases` gespeichert.

## Hinweise
- Der CREATE-Modus hat erfolgreich alle Artefakte für den IMPLEMENTATION-Modus erstellt.
- Die generierten Code-Artefakte sollten überprüft und bei Bedarf angepasst werden.
- Der RAG-Service sollte weiterhin laufen, um den IMPLEMENTATION-Modus zu unterstützen.
"""
                
                with open("memory-bank/handover/current-handover.md", "w", encoding="utf-8") as f:
                    f.write(handover_info)
                
                logger.info("Handover-Dokument in memory-bank/handover/current-handover.md gespeichert")
                
                print("\n" + "=" * 80)
                print("CREATE-Modus erfolgreich abgeschlossen")
                print(f"Projekt-ID: {project_id}")
                print(f"PLAN-Ergebnis-ID: {plan_id}")
                print(f"CREATE-Ergebnis-ID: {result_id}")
                print(f"Ausführungsdauer: {duration:.2f} Sekunden")
                print("=" * 80 + "\n")
                
                print("Der CREATE-Modus hat folgende Artefakte erstellt:")
                print(f"1. Code-Artefakte: {len(result.get('code_artifacts', []))}")
                print(f"2. Ressourcenanforderungen: {len(result.get('resource_requirements', []))}")
                print(f"3. Entwurfsmuster: {len(result.get('design_patterns', []))}")
                print(f"4. Testfälle: {len(result.get('test_cases', []))}")
                print("\n" + "=" * 80)
                print("\nSie können jetzt zum IMPLEMENTATION-Modus wechseln mit: python scripts/activate_implementation_mode.py")
                
            except Exception as e:
                logger.error(f"Fehler bei der Ausführung des CREATE-Modus: {str(e)}")
                print(f"\nFehler bei der Ausführung des CREATE-Modus: {str(e)}")
        else:
            logger.error("Kein Projektplan mit Lösungsdesign-ID gefunden")
            print("\nFehler: Kein Projektplan mit Lösungsdesign-ID gefunden.")
            print("Führen Sie zuerst 'python scripts/update_project_plan.py' aus, um die Lösungsdesign-ID zu setzen.")
    
    except Exception as e:
        logger.error(f"Fehler bei der Ausführung des CREATE-Modus: {str(e)}")
        print(f"\nFehler: {str(e)}")
    
    finally:
        # MongoDB-Verbindung trennen
        if 'mongodb' in locals():
            await mongodb.disconnect()


if __name__ == "__main__":
    # Asynchrone Funktion ausführen
    asyncio.run(run_create_mode()) 