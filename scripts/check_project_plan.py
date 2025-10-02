#!/usr/bin/env python3
"""
Überprüft den Projektplan in der MongoDB.
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
from bson import ObjectId

# Pfad zum Projekt-Root hinzufügen
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.apm_framework.mongodb_connector import APMMongoDBConnector

# Logger konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def check_project_plan():
    """
    Überprüft den Projektplan in der MongoDB.
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
        
        # Projektpläne abrufen
        project_plans = await mongodb.find_many("project_plans", {"project_id": project_id})
        
        if project_plans:
            print(f"\nGefundene Projektpläne: {len(project_plans)}")
            
            for i, plan in enumerate(project_plans):
                print(f"\n{'-' * 40}")
                print(f"Projektplan {i+1}:")
                print(f"ID: {plan.get('_id')}")
                print(f"Name: {plan.get('name')}")
                print(f"Beschreibung: {plan.get('description')}")
                print(f"VAN-Analyse-ID: {plan.get('van_analysis_id')}")
                print(f"Solution-Design-ID: {plan.get('solution_design_id')}")
                print(f"Timestamp: {plan.get('timestamp')}")
                print(f"Updated At: {plan.get('updated_at')}")
                
                # Meilensteine anzeigen
                milestones = plan.get("milestones", [])
                if milestones:
                    print(f"\nMeilensteine: {len(milestones)}")
                    for j, milestone in enumerate(milestones):
                        print(f"  {j+1}. {milestone.get('name')}: {milestone.get('description')[:50]}...")
                else:
                    print("\nKeine Meilensteine im Projektplan!")
                
                # Lösungsdesign abrufen, falls vorhanden
                solution_design_id = plan.get("solution_design_id")
                if solution_design_id:
                    solution_design = await mongodb.find_one("solution_designs", {"_id": solution_design_id})
                    if solution_design:
                        print(f"\nLösungsdesign gefunden:")
                        print(f"Name: {solution_design.get('name')}")
                        print(f"Beschreibung: {solution_design.get('description')}")
                        
                        # Komponenten anzeigen
                        components = solution_design.get("components", [])
                        if components:
                            print(f"\nKomponenten: {len(components)}")
                            for j, component in enumerate(components):
                                print(f"  {j+1}. {component.get('name')}: {component.get('type')}")
                        else:
                            print("\nKeine Komponenten im Lösungsdesign!")
                    else:
                        print(f"\nLösungsdesign mit ID {solution_design_id} nicht gefunden!")
                else:
                    print("\nKeine Solution-Design-ID im Projektplan!")
        else:
            print("\nKeine Projektpläne gefunden.")
        
        # Aktuelle Workflow-Informationen abrufen
        workflow_info = await mongodb.find_one("apm_workflow", {"project_id": project_id})
        if workflow_info:
            print(f"\n{'-' * 40}")
            print(f"APM-Workflow-Informationen:")
            print(f"Aktueller Modus: {workflow_info.get('current_mode')}")
            print(f"Letzter Modus: {workflow_info.get('last_mode')}")
            print(f"Aktualisiert am: {workflow_info.get('updated_at')}")
        else:
            print("\nKeine APM-Workflow-Informationen gefunden.")
    
    except Exception as e:
        logger.error(f"Fehler bei der Überprüfung des Projektplans: {str(e)}")
        print(f"\nFehler: {str(e)}")
    
    finally:
        # MongoDB-Verbindung trennen
        if 'mongodb' in locals():
            await mongodb.disconnect()


if __name__ == "__main__":
    # Asynchrone Funktion ausführen
    asyncio.run(check_project_plan()) 