#!/usr/bin/env python3
"""
Integration zwischen Tasks und langgraph-Workflow.
Verbindet die Task-Verwaltung mit dem APM-Framework.
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Pfad zum Projektverzeichnis hinzufügen
sys.path.append(str(Path(__file__).resolve().parent.parent))

from backend.apm_framework.apm_workflow import APMWorkflow
from backend.apm_framework.mongodb_connector import APMMongoDBConnector
from linkup_mcp.langgraph_integration import LangGraphIntegration, AgentType

# Logger konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TaskWorkflowIntegration:
    """Integriert Tasks mit dem langgraph-Workflow."""
    
    def __init__(self, mongodb_uri: str = "mongodb://localhost:27017/", 
                 db_name: str = "valeo_neuroerp"):
        """Initialisiert die Task-Workflow-Integration."""
        self.mongodb_uri = mongodb_uri
        self.db_name = db_name
        self.workflow = APMWorkflow(mongodb_uri=mongodb_uri, db_name=db_name)
        self.langgraph = LangGraphIntegration()
        self.tasks_file = Path(__file__).resolve().parent.parent / "memory-bank" / "tasks.md"
    
    def _parse_tasks(self) -> Dict[str, List[Dict[str, Any]]]:
        """Liest und parsed die Tasks aus der tasks.md Datei."""
        with open(self.tasks_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        tasks_by_agent = {
            "VAN": {"high": [], "normal": []},
            "PLAN": {"high": [], "normal": []},
            "CREATE": {"high": [], "normal": []},
            "IMPLEMENT": {"high": [], "normal": []},
            "REVIEW": {"high": [], "normal": []}
        }
        
        current_agent = None
        current_priority = None
        current_task = None
        
        for line in content.split("\n"):
            line = line.strip()
            
            # Agent-Sektion erkennen
            if line.startswith("## "):
                agent = line[3:].split(" ")[0]
                if agent in tasks_by_agent:
                    current_agent = agent
                    current_priority = None
                    current_task = None
                continue
            
            # Priorität erkennen
            if line.startswith("### "):
                if "hoch" in line.lower():
                    current_priority = "high"
                else:
                    current_priority = "normal"
                continue
            
            # Task erkennen
            if line.startswith("- [ ]") and current_agent and current_priority:
                task_title = line[5:].strip()
                current_task = {
                    "title": task_title,
                    "context": "",
                    "source": "",
                    "subtasks": []
                }
                tasks_by_agent[current_agent][current_priority].append(current_task)
                continue
            
            # Task-Details erkennen
            if current_task and line.startswith("  - "):
                detail = line[4:].strip()
                if "Kontext:" in detail:
                    current_task["context"] = detail.split("Kontext:")[1].strip()
                elif "Quelle:" in detail:
                    current_task["source"] = detail.split("Quelle:")[1].strip()
                elif "Unteraufgaben:" in detail:
                    continue
                else:
                    current_task["subtasks"].append(detail)
        
        return tasks_by_agent
    
    async def update_workflow_state(self):
        """Aktualisiert den Workflow-Status basierend auf den Tasks."""
        tasks = self._parse_tasks()
        
        # Aktuelle Phase bestimmen
        current_phase = None
        max_tasks = 0
        
        for agent, priorities in tasks.items():
            total_tasks = len(priorities["high"]) + len(priorities["normal"])
            if total_tasks > max_tasks:
                max_tasks = total_tasks
                current_phase = agent
        
        # Workflow-Status aktualisieren
        workflow_state = {
            "current_phase": current_phase,
            "last_update": datetime.now().isoformat(),
            "tasks_by_phase": {
                agent: {
                    "high_priority": len(priorities["high"]),
                    "normal_priority": len(priorities["normal"]),
                    "total": len(priorities["high"]) + len(priorities["normal"])
                }
                for agent, priorities in tasks.items()
            }
        }
        
        # Status in MongoDB speichern
        connector = APMMongoDBConnector(self.mongodb_uri, self.db_name)
        await connector.connect()
        await connector.insert_one("workflow_states", workflow_state)
        
        logger.info(f"Workflow-Status aktualisiert: Aktuelle Phase ist {current_phase}")
        return workflow_state
    
    async def get_next_tasks(self, agent_type: AgentType) -> List[Dict[str, Any]]:
        """Holt die nächsten Tasks für einen bestimmten Agenten."""
        tasks = self._parse_tasks()
        agent = agent_type.value.upper()
        
        if agent not in tasks:
            return []
        
        # Zuerst Hochprioritäts-Tasks
        next_tasks = tasks[agent]["high"]
        
        # Wenn keine Hochprioritäts-Tasks, dann normale Priorität
        if not next_tasks:
            next_tasks = tasks[agent]["normal"]
        
        return next_tasks
    
    async def run_agent_workflow(self, agent_type: AgentType):
        """Führt den Workflow für einen bestimmten Agenten aus."""
        tasks = await self.get_next_tasks(agent_type)
        
        if not tasks:
            logger.info(f"Keine Tasks für Agent {agent_type.value}")
            return
        
        # Workflow-Kontext erstellen
        context = {
            "agent_type": agent_type.value,
            "tasks": tasks,
            "timestamp": datetime.now().isoformat()
        }
        
        # Workflow ausführen
        try:
            result = await self.langgraph.run_workflow(
                workflow_id=f"{agent_type.value}_workflow",
                input_data=context,
                start_agent=agent_type
            )
            
            # Ergebnis in MongoDB speichern
            connector = APMMongoDBConnector(self.mongodb_uri, self.db_name)
            await connector.connect()
            await connector.insert_one(
                "agent_results",
                {
                    "agent_type": agent_type.value,
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            logger.info(f"Workflow für {agent_type.value} erfolgreich ausgeführt")
            return result
            
        except Exception as e:
            logger.error(f"Fehler beim Ausführen des Workflows für {agent_type.value}: {str(e)}")
            raise

async def main():
    """Hauptfunktion zum Testen der Task-Workflow-Integration."""
    try:
        integration = TaskWorkflowIntegration()
        
        # MongoDB-Verbindung testen
        connector = APMMongoDBConnector(integration.mongodb_uri, integration.db_name)
        if not await connector.connect():
            logger.error("Keine Verbindung zu MongoDB möglich")
            return
        
        # Collections erstellen
        collections = ["workflow_states", "task_history", "agent_results"]
        for collection in collections:
            await connector.create_collection(collection)
        
        # Workflow-Status aktualisieren
        state = await integration.update_workflow_state()
        logger.info(f"Aktueller Workflow-Status: {json.dumps(state, indent=2)}")
        
        # Test mit VAN-Agent
        van_result = await integration.run_agent_workflow(AgentType.VAN)
        if van_result:
            logger.info(f"VAN-Workflow Ergebnis: {json.dumps(van_result, indent=2)}")
        
    except Exception as e:
        logger.error(f"Fehler bei der Task-Workflow-Integration: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())