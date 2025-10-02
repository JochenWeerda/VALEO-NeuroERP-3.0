"""
Langgraph-Pipeline für parallele Ausführung von Verbesserungen
"""

import os
import yaml
import asyncio
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
from agents.parallel_improvement_agent import ParallelImprovementAgent

async def run_task(task: Dict[str, Any], agent_name: str) -> Dict[str, Any]:
    """Führt eine einzelne Task aus"""
    agent = ParallelImprovementAgent(
        name=agent_name,
        task=task,
        artifacts=task["artifacts"]
    )
    return await agent.execute()

async def run_parallel_tasks(config: Dict[str, Any], num_agents: int) -> List[Dict[str, Any]]:
    """Führt Tasks parallel aus"""
    
    all_tasks = []
    for category in config["parallel_tasks"].values():
        all_tasks.extend(category["tasks"])
    
    # Erstelle Task-Gruppen für parallele Ausführung
    task_groups = []
    for i in range(0, len(all_tasks), num_agents):
        group = all_tasks[i:i + num_agents]
        task_groups.append(group)
    
    results = []
    
    # Führe Task-Gruppen nacheinander aus
    for group_idx, task_group in enumerate(task_groups):
        print(f"\nVerarbeite Task-Gruppe {group_idx + 1}/{len(task_groups)}...")
        
        # Führe Tasks in der Gruppe parallel aus
        tasks = []
        for task_idx, task in enumerate(task_group):
            agent_name = f"agent_{group_idx}_{task_idx}"
            tasks.append(run_task(task, agent_name))
        
        # Warte auf Abschluss aller Tasks in der Gruppe
        group_results = await asyncio.gather(*tasks)
        results.extend(group_results)
        
        print(f"Task-Gruppe {group_idx + 1} abgeschlossen.")
    
    return results

def main():
    """Hauptfunktion"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Führt parallele Verbesserungen aus")
    parser.add_argument("--config", required=True, help="Pfad zur Konfigurationsdatei")
    parser.add_argument("--agents", type=int, default=4, help="Anzahl paralleler Agenten")
    parser.add_argument("--mode", choices=["create", "implement"], default="create",
                      help="Ausführungsmodus (create oder implement)")
    args = parser.parse_args()
    
    # Lade Konfiguration
    with open(args.config, "r") as f:
        config = yaml.safe_load(f)
    
    print(f"\nStarte parallele Ausführung mit {args.agents} Agenten im {args.mode.upper()}-Modus...")
    
    # Führe Tasks aus
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(run_parallel_tasks(config, args.agents))
    
    # Zeige Ergebnisse
    print("\nAusführung abgeschlossen!")
    print("\nErgebnisse:")
    for result in results:
        status = "✅" if result["status"] == "success" else "❌"
        print(f"{status} {result['task']}: {result['message']}")
        if "files_created" in result:
            print("  Erstellte Dateien:")
            for file in result["files_created"]:
                print(f"  - {file}")
    
if __name__ == "__main__":
    main() 