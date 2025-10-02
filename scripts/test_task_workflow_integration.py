#!/usr/bin/env python3
"""
Test-Skript für die Task-Workflow-Integration mit MongoDB.
"""

import os
import sys
import json
import asyncio
import logging
from pathlib import Path
from datetime import datetime, timedelta

# Pfad zum Projektverzeichnis hinzufügen
sys.path.append(str(Path(__file__).resolve().parent.parent))

from scripts.task_workflow_integration import TaskWorkflowIntegration
from backend.apm_framework.mongodb_connector import APMMongoDBConnector
from linkup_mcp.langgraph_integration import AgentType

# Logger konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TaskWorkflowTester:
    """Test-Klasse für die Task-Workflow-Integration."""
    
    def __init__(self):
        """Initialisiert den Task-Workflow-Tester."""
        self.mongodb_uri = "mongodb://localhost:27017/"
        self.db_name = "valeo_neuroerp_test"
        self.integration = TaskWorkflowIntegration(
            mongodb_uri=self.mongodb_uri,
            db_name=self.db_name
        )
        self.connector = APMMongoDBConnector(self.mongodb_uri, self.db_name)
    
    async def setup_test_db(self):
        """Richtet die Test-Datenbank ein."""
        try:
            # Verbindung herstellen
            await self.connector.connect()
            
            # Collections erstellen
            collections = ["workflow_states", "task_history", "agent_results"]
            for collection in collections:
                await self.connector.create_collection(collection)
            
            logger.info("Test-Datenbank erfolgreich eingerichtet")
            return True
        except Exception as e:
            logger.error(f"Fehler beim Einrichten der Test-Datenbank: {str(e)}")
            return False
    
    async def cleanup_test_db(self):
        """Räumt die Test-Datenbank auf."""
        try:
            # Collections löschen
            collections = ["workflow_states", "task_history", "agent_results"]
            for collection in collections:
                await self.connector.drop_collection(collection)
            
            # Verbindung trennen
            await self.connector.disconnect()
            
            logger.info("Test-Datenbank erfolgreich aufgeräumt")
            return True
        except Exception as e:
            logger.error(f"Fehler beim Aufräumen der Test-Datenbank: {str(e)}")
            return False
    
    async def test_workflow_state_updates(self):
        """Testet die Workflow-Status-Aktualisierungen."""
        try:
            # Initialen Status speichern
            initial_state = await self.integration.update_workflow_state()
            logger.info("Initialer Workflow-Status gespeichert")
            
            # Status abrufen und vergleichen
            stored_state = await self.connector.find_one(
                "workflow_states",
                {"current_phase": initial_state["current_phase"]}
            )
            
            if not stored_state:
                raise ValueError("Gespeicherter Status nicht gefunden")
            
            logger.info("Workflow-Status erfolgreich getestet")
            return True
        except Exception as e:
            logger.error(f"Fehler beim Testen der Workflow-Status-Updates: {str(e)}")
            return False
    
    async def test_agent_workflow(self, agent_type: AgentType):
        """Testet den Workflow eines spezifischen Agenten."""
        try:
            # Workflow ausführen
            result = await self.integration.run_agent_workflow(agent_type)
            
            if result:
                # Ergebnis in MongoDB speichern
                await self.connector.insert_one(
                    "agent_results",
                    {
                        "agent_type": agent_type.value,
                        "result": result,
                        "timestamp": datetime.now()
                    }
                )
                
                logger.info(f"Agent-Workflow für {agent_type.value} erfolgreich getestet")
                return True
            else:
                logger.warning(f"Keine Ergebnisse für Agent {agent_type.value}")
                return False
        except Exception as e:
            logger.error(f"Fehler beim Testen des Agent-Workflows: {str(e)}")
            return False
    
    async def test_task_history(self):
        """Testet die Task-Historie-Funktionalität."""
        try:
            # Beispiel-Task-Historie erstellen
            task_history = {
                "task_id": "test_task_001",
                "title": "Performance-Analyse durchführen",
                "agent_type": AgentType.VAN.value,
                "status": "completed",
                "start_time": datetime.now() - timedelta(hours=1),
                "end_time": datetime.now(),
                "result": "Performance-Analyse erfolgreich durchgeführt"
            }
            
            # In MongoDB speichern
            await self.connector.insert_one("task_history", task_history)
            
            # Abrufen und vergleichen
            stored_task = await self.connector.find_one(
                "task_history",
                {"task_id": task_history["task_id"]}
            )
            
            if not stored_task:
                raise ValueError("Gespeicherte Task-Historie nicht gefunden")
            
            logger.info("Task-Historie erfolgreich getestet")
            return True
        except Exception as e:
            logger.error(f"Fehler beim Testen der Task-Historie: {str(e)}")
            return False

async def main():
    """Hauptfunktion zum Ausführen der Tests."""
    try:
        tester = TaskWorkflowTester()
        
        # Test-Datenbank einrichten
        if not await tester.setup_test_db():
            return
        
        # Tests ausführen
        tests = [
            ("Workflow-Status-Updates", tester.test_workflow_state_updates()),
            ("VAN-Agent-Workflow", tester.test_agent_workflow(AgentType.VAN)),
            ("Task-Historie", tester.test_task_history())
        ]
        
        for test_name, test_coro in tests:
            logger.info(f"\nStarte Test: {test_name}")
            if await test_coro:
                logger.info(f"✓ {test_name} erfolgreich")
            else:
                logger.error(f"✗ {test_name} fehlgeschlagen")
        
        # Aufräumen
        await tester.cleanup_test_db()
        
    except Exception as e:
        logger.error(f"Fehler bei der Test-Ausführung: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())