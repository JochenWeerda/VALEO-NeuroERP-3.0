#!/usr/bin/env python3
"""
Aktiviert den PLAN-Modus im APM-Framework des VALEO-NeuroERP-Systems.
Wechselt zum PLAN-Modus und führt die notwendigen Initialisierungen durch.
"""

import os
import sys
import asyncio
import logging
import uuid
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

class PlanMode:
    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['valeo_neuroerp']
        self.plan_collection = self.db['planning']
        
    async def activate(self):
        """Aktiviert den PLAN-Modus und speichert die Planung"""
        try:
            # Aktuelle Planung laden
            plan_path = Path('memory-bank/planning/sprint_plan_2025-07.md')
            if not plan_path.exists():
                raise FileNotFoundError(f"Planungsdatei nicht gefunden: {plan_path}")
            
            with open(plan_path, 'r', encoding='utf-8') as f:
                plan_content = f.read()
            
            # Planung in MongoDB speichern
            plan_doc = {
                "type": "sprint_plan",
                "date": datetime.now(),
                "content": plan_content,
                "status": "active",
                "metadata": {
                    "sprints": 3,
                    "start_date": "2025-07-08",
                    "end_date": "2025-07-26",
                    "teams": ["Backend", "DevOps", "Database"],
                    "total_developers": 8
                }
            }
            
            result = self.plan_collection.insert_one(plan_doc)
            logger.info(f"Planung in MongoDB gespeichert. Document ID: {result.inserted_id}")
            
            # Status aktualisieren
            self.plan_collection.update_many(
                {"_id": {"$ne": result.inserted_id}},
                {"$set": {"status": "archived"}}
            )
            
            logger.info("PLAN-Modus erfolgreich aktiviert")
            return result.inserted_id
            
        except Exception as e:
            logger.error(f"Fehler beim Aktivieren des PLAN-Modus: {str(e)}")
            raise

async def main():
    plan_mode = PlanMode()
    await plan_mode.activate()

if __name__ == "__main__":
    asyncio.run(main()) 