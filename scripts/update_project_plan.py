#!/usr/bin/env python3
"""
Aktualisiert die solution_design_id im Projektplan.
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


async def update_project_plan():
    """
    Aktualisiert die solution_design_id im Projektplan.
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
        
        # Neuestes PLAN-Ergebnis und Lösungsdesign abrufen
        plan_results = await mongodb.find_many("plan_results", {"project_id": project_id}, 
                                              sort_field="timestamp", sort_order=-1, limit=1)
        
        if not plan_results:
            logger.error("Kein PLAN-Ergebnis gefunden")
            print("\nFehler: Kein PLAN-Ergebnis gefunden.")
            return
        
        plan_result = plan_results[0]
        plan_result_id = plan_result.get("_id")
        design_id = plan_result.get("design_id")
        
        logger.info(f"PLAN-Ergebnis gefunden: {plan_result_id}")
        logger.info(f"Design-ID: {design_id}")
        
        # Projektplan abrufen
        project_plans = await mongodb.find_many("project_plans", {"project_id": project_id}, 
                                               sort_field="timestamp", sort_order=-1, limit=1)
        
        if not project_plans:
            logger.error("Kein Projektplan gefunden")
            print("\nFehler: Kein Projektplan gefunden.")
            return
        
        project_plan = project_plans[0]
        project_plan_id = project_plan.get("_id")
        
        logger.info(f"Projektplan gefunden: {project_plan_id}")
        
        # Projektplan aktualisieren
        update_dict = {
            "$set": {
                "solution_design_id": design_id,
                "updated_at": datetime.now()
            }
        }
        
        await mongodb.update_one("project_plans", {"_id": project_plan_id}, update_dict)
        
        logger.info(f"Projektplan mit ID {project_plan_id} aktualisiert")
        logger.info(f"solution_design_id auf {design_id} gesetzt")
        
        print("\n" + "=" * 80)
        print("Projektplan erfolgreich aktualisiert")
        print(f"Projektplan-ID: {project_plan_id}")
        print(f"solution_design_id: {design_id}")
        print("=" * 80 + "\n")
        
        print("Sie können jetzt den CREATE-Modus ausführen mit: python scripts/run_create_mode.py")
    
    except Exception as e:
        logger.error(f"Fehler bei der Aktualisierung des Projektplans: {str(e)}")
        print(f"\nFehler: {str(e)}")
    
    finally:
        # MongoDB-Verbindung trennen
        if 'mongodb' in locals():
            await mongodb.disconnect()


if __name__ == "__main__":
    # Asynchrone Funktion ausführen
    asyncio.run(update_project_plan()) 