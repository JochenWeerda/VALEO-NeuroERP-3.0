#!/usr/bin/env python3
"""
Überprüft das PLAN-Ergebnis in der MongoDB.
"""

import os
import sys
import asyncio
import logging
import json
from datetime import datetime
from bson import ObjectId

# Pfad zum Projekt-Root hinzufügen
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.apm_framework.mongodb_connector import APMMongoDBConnector

# Logger konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MongoJSONEncoder(json.JSONEncoder):
    """JSON-Encoder für MongoDB-Objekte."""
    
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(MongoJSONEncoder, self).default(obj)


async def check_plan_result():
    """
    Überprüft das PLAN-Ergebnis in der MongoDB.
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
        
        # Alle PLAN-Ergebnisse abrufen
        plan_results = await mongodb.find_many("plan_results", {"project_id": project_id})
        
        if plan_results:
            print(f"\nGefundene PLAN-Ergebnisse: {len(plan_results)}")
            
            for i, plan_result in enumerate(plan_results):
                print(f"\n{'-' * 40}")
                print(f"PLAN-Ergebnis {i+1}:")
                print(f"ID: {plan_result.get('_id')}")
                print(f"Projekt-ID: {plan_result.get('project_id')}")
                print(f"VAN-Analyse-ID: {plan_result.get('van_analysis_id')}")
                print(f"Plan-ID: {plan_result.get('plan_id')}")
                print(f"Design-ID: {plan_result.get('design_id')}")
                print(f"Task-IDs: {plan_result.get('task_ids')}")
                print(f"Nächste Schritte: {plan_result.get('next_steps')}")
                print(f"Timestamp: {plan_result.get('timestamp')}")
                
                # Lösungsdesign abrufen
                design_id = plan_result.get("design_id")
                if design_id:
                    design = await mongodb.find_one("solution_designs", {"_id": design_id})
                    if design:
                        print(f"\nLösungsdesign gefunden:")
                        print(f"Name: {design.get('name')}")
                        print(f"Beschreibung: {design.get('description')}")
                    else:
                        print(f"\nLösungsdesign mit ID {design_id} nicht gefunden!")
                else:
                    print("\nKeine Design-ID im PLAN-Ergebnis!")
        else:
            print("\nKeine PLAN-Ergebnisse gefunden.")
        
        # Alle Projektpläne abrufen
        project_plans = await mongodb.find_many("project_plans", {"project_id": project_id})
        
        if project_plans:
            print(f"\n{'-' * 40}")
            print(f"\nGefundene Projektpläne: {len(project_plans)}")
            
            for i, plan in enumerate(project_plans):
                print(f"\n{'-' * 40}")
                print(f"Projektplan {i+1}:")
                print(f"ID: {plan.get('_id')}")
                print(f"Name: {plan.get('name')}")
                print(f"Beschreibung: {plan.get('description')}")
                print(f"VAN-Analyse-ID: {plan.get('van_analysis_id')}")
                print(f"Timestamp: {plan.get('timestamp')}")
                
                # Meilensteine anzeigen
                milestones = plan.get("milestones", [])
                if milestones:
                    print(f"\nMeilensteine: {len(milestones)}")
                    for j, milestone in enumerate(milestones):
                        print(f"  {j+1}. {milestone.get('name')}: {milestone.get('description')[:50]}...")
                else:
                    print("\nKeine Meilensteine im Projektplan!")
        else:
            print("\nKeine Projektpläne gefunden.")
        
        # Alle Lösungsdesigns abrufen
        solution_designs = await mongodb.find_many("solution_designs", {"project_id": project_id})
        
        if solution_designs:
            print(f"\n{'-' * 40}")
            print(f"\nGefundene Lösungsdesigns: {len(solution_designs)}")
            
            for i, design in enumerate(solution_designs):
                print(f"\n{'-' * 40}")
                print(f"Lösungsdesign {i+1}:")
                print(f"ID: {design.get('_id')}")
                print(f"Name: {design.get('name')}")
                print(f"Beschreibung: {design.get('description')}")
                print(f"Requirement-ID: {design.get('requirement_id')}")
                print(f"Timestamp: {design.get('timestamp')}")
                
                # Komponenten anzeigen
                components = design.get("components", [])
                if components:
                    print(f"\nKomponenten: {len(components)}")
                    for j, component in enumerate(components):
                        print(f"  {j+1}. {component.get('name')}: {component.get('description')[:50]}...")
                else:
                    print("\nKeine Komponenten im Lösungsdesign!")
        else:
            print("\nKeine Lösungsdesigns gefunden.")
        
    except Exception as e:
        logger.error(f"Fehler bei der Überprüfung des PLAN-Ergebnisses: {str(e)}")
        print(f"\nFehler: {str(e)}")
    
    finally:
        # MongoDB-Verbindung trennen
        if 'mongodb' in locals():
            await mongodb.disconnect()


if __name__ == "__main__":
    # Asynchrone Funktion ausführen
    asyncio.run(check_plan_result()) 