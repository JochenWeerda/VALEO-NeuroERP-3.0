#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GENXAIS Zyklus-Starter
Dieses Script startet einen GENXAIS-Zyklus basierend auf der aktuellen Version.
"""

import os
import sys
import json
import time
import yaml
import datetime
import argparse
from pathlib import Path

# Importiere die Versionskonfiguration
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.genxais_version import get_version, get_previous_version, increment_version

# Konstanten
DEFAULT_PROMPT_FILE = "prompts/launch_cycle_valero_{}.yaml"
DATA_DIR = Path("data/dashboard")
PHASES_FILE = DATA_DIR / "phases.json"
PIPELINES_FILE = DATA_DIR / "pipelines.json"
GRAPHITI_DIR = DATA_DIR / "graphiti"
DECISION_MAP_FILE_TEMPLATE = "decision_map_{}.json"

def load_prompt(version=None):
    """Lädt den Initialisierungs-Prompt für den GENXAIS-Zyklus"""
    if version is None:
        version = get_version()
    
    prompt_file = DEFAULT_PROMPT_FILE.format(version)
    
    if not os.path.exists(prompt_file):
        print(f"Fehler: Prompt-Datei {prompt_file} nicht gefunden.")
        return None
    
    try:
        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt_data = yaml.safe_load(f)
        return prompt_data
    except Exception as e:
        print(f"Fehler beim Laden des Prompts: {e}")
        return None

def initialize_dashboard_data(prompt_data, version=None):
    """Initialisiert die Daten für das Dashboard"""
    if version is None:
        version = get_version()
    
    # Stelle sicher, dass die Verzeichnisse existieren
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    GRAPHITI_DIR.mkdir(parents=True, exist_ok=True)
    
    # Initialisiere Phasen-Daten
    phases_data = {
        "version": version,
        "current_phase": "VAN",
        "phases": [],
        "last_updated": datetime.datetime.now().isoformat()
    }
    
    # Füge Phasen hinzu
    default_phases = ["VAN", "PLAN", "CREATE", "IMPLEMENT", "REFLECT"]
    phases_from_prompt = prompt_data.get("phases", [])
    
    # Wenn phases eine Liste von Strings ist, verwende diese direkt
    if phases_from_prompt and isinstance(phases_from_prompt[0], str):
        phase_names = phases_from_prompt
    # Wenn phases eine Liste von Dictionaries ist, extrahiere die Namen
    elif phases_from_prompt and isinstance(phases_from_prompt[0], dict):
        phase_names = [phase.get("name", "") for phase in phases_from_prompt]
    # Fallback zu Standardphasen
    else:
        phase_names = default_phases
    
    for phase_name in phase_names:
        phase_status = "active" if phase_name == "VAN" else "pending"
        phase_progress = 5 if phase_name == "VAN" else 0
        
        phase_data = {
            "name": phase_name,
            "status": phase_status,
            "progress": phase_progress,
            "tasks": []
        }
        
        # Füge Tasks hinzu, falls vorhanden
        if isinstance(phases_from_prompt[0], dict):
            for phase in phases_from_prompt:
                if phase.get("name") == phase_name:
                    for task in phase.get("tasks", []):
                        task_data = {
                            "name": task,
                            "status": "pending",
                            "progress": 0
                        }
                        phase_data["tasks"].append(task_data)
        
        phases_data["phases"].append(phase_data)
    
    # Speichere Phasen-Daten
    with open(PHASES_FILE, 'w', encoding='utf-8') as f:
        json.dump(phases_data, f, indent=2, ensure_ascii=False)
    
    # Initialisiere Pipeline-Daten
    pipelines_data = {
        "version": version,
        "pipelines": [],
        "last_updated": datetime.datetime.now().isoformat()
    }
    
    # Füge Pipelines hinzu
    for pipeline in prompt_data.get("pipelines", []):
        pipeline_id = pipeline.get("id", "")
        pipeline_name = pipeline.get("name", "")
        pipeline_status = "planning"
        pipeline_progress = 0
        
        pipeline_data = {
            "id": pipeline_id,
            "name": pipeline_name,
            "status": pipeline_status,
            "progress": pipeline_progress,
            "agents": pipeline.get("agents", []),
            "goals": [],
            "runtime": "0h 0m"
        }
        
        # Füge Ziele hinzu
        for goal in pipeline.get("goals", []):
            goal_data = {
                "name": goal,
                "status": "pending",
                "progress": 0
            }
            pipeline_data["goals"].append(goal_data)
        
        pipelines_data["pipelines"].append(pipeline_data)
    
    # Speichere Pipeline-Daten
    with open(PIPELINES_FILE, 'w', encoding='utf-8') as f:
        json.dump(pipelines_data, f, indent=2, ensure_ascii=False)
    
    # Initialisiere Graphiti Decision Map
    decision_map_file = GRAPHITI_DIR / DECISION_MAP_FILE_TEMPLATE.format(version)
    
    # Erstelle eine einfache Decision Map
    next_version = get_next_version(version)
    decision_map = {
        "version": version,
        "name": f"GENXAIS Decision Map {version}",
        "dot_source": f"""
        digraph G {{
            rankdir=LR;
            node [shape=box, style="rounded,filled", fillcolor=lightblue];
            
            // Phasen
            van [label="VAN Phase", fillcolor=lightgreen];
            plan [label="PLAN Phase"];
            create [label="CREATE Phase"];
            impl [label="IMPLEMENTATION Phase"];
            refl [label="REFLEKTION Phase"];
            
            // Entscheidungspunkte
            d1 [label="Issues Analyse", shape=diamond];
            d2 [label="Artefakt Validierung", shape=diamond];
            d3 [label="Pipeline Planung", shape=diamond];
            d4 [label="Ressourcen Zuweisung", shape=diamond];
            d5 [label="Codegenerierung", shape=diamond];
            d6 [label="Integration", shape=diamond];
            d7 [label="Deployment", shape=diamond];
            d8 [label="Abschlussbewertung", shape=diamond];
            
            // Kanten
            van -> d1;
            d1 -> d2 [label="Issues analysiert"];
            d2 -> d3 [label="Artefakte validiert"];
            d3 -> plan [label="Pipelines geplant"];
            plan -> d4;
            d4 -> create [label="Ressourcen zugewiesen"];
            create -> d5;
            d5 -> impl [label="Code generiert"];
            impl -> d6;
            d6 -> d7 [label="Integration abgeschlossen"];
            d7 -> refl [label="Deployment erfolgreich"];
            refl -> d8;
            d8 -> "{next_version}" [label="Zyklus abgeschlossen"];
            
            // Aktuelle Position
            van [fillcolor=lightgreen];
            d1 [fillcolor=gold];
        }}
        """,
        "nodes": [
            {"id": "van", "label": "VAN Phase", "type": "phase", "status": "active"},
            {"id": "plan", "label": "PLAN Phase", "type": "phase", "status": "pending"},
            {"id": "create", "label": "CREATE Phase", "type": "phase", "status": "pending"},
            {"id": "impl", "label": "IMPLEMENTATION Phase", "type": "phase", "status": "pending"},
            {"id": "refl", "label": "REFLEKTION Phase", "type": "phase", "status": "pending"},
            {"id": "d1", "label": "Issues Analyse", "type": "decision", "status": "active"},
            {"id": "d2", "label": "Artefakt Validierung", "type": "decision", "status": "pending"},
            {"id": "d3", "label": "Pipeline Planung", "type": "decision", "status": "pending"},
            {"id": "d4", "label": "Ressourcen Zuweisung", "type": "decision", "status": "pending"},
            {"id": "d5", "label": "Codegenerierung", "type": "decision", "status": "pending"},
            {"id": "d6", "label": "Integration", "type": "decision", "status": "pending"},
            {"id": "d7", "label": "Deployment", "type": "decision", "status": "pending"},
            {"id": "d8", "label": "Abschlussbewertung", "type": "decision", "status": "pending"},
            {"id": next_version, "label": next_version, "type": "exit", "status": "pending"}
        ],
        "edges": [
            {"source": "van", "target": "d1", "label": ""},
            {"source": "d1", "target": "d2", "label": "Issues analysiert"},
            {"source": "d2", "target": "d3", "label": "Artefakte validiert"},
            {"source": "d3", "target": "plan", "label": "Pipelines geplant"},
            {"source": "plan", "target": "d4", "label": ""},
            {"source": "d4", "target": "create", "label": "Ressourcen zugewiesen"},
            {"source": "create", "target": "d5", "label": ""},
            {"source": "d5", "target": "impl", "label": "Code generiert"},
            {"source": "impl", "target": "d6", "label": ""},
            {"source": "d6", "target": "d7", "label": "Integration abgeschlossen"},
            {"source": "d7", "target": "refl", "label": "Deployment erfolgreich"},
            {"source": "refl", "target": "d8", "label": ""},
            {"source": "d8", "target": next_version, "label": "Zyklus abgeschlossen"}
        ],
        "last_updated": datetime.datetime.now().isoformat()
    }
    
    # Speichere Decision Map
    with open(decision_map_file, 'w', encoding='utf-8') as f:
        json.dump(decision_map, f, indent=2, ensure_ascii=False)

def get_next_version(version):
    """Berechnet die nächste Version"""
    try:
        version_parts = version.split('.')
        major = version_parts[0]
        minor = int(version_parts[1])
        return f"{major}.{minor+1}"
    except Exception:
        return "v1.6"  # Fallback

def normalize_progress_values(data):
    """Normalisiert Fortschrittswerte auf den Bereich 0-100"""
    if "phases" in data:
        for phase in data.get("phases", []):
            if "progress" in phase:
                phase["progress"] = min(100, max(0, phase.get("progress", 0)))
            for task in phase.get("tasks", []):
                if "progress" in task:
                    task["progress"] = min(100, max(0, task.get("progress", 0)))
    
    if "pipelines" in data:
        for pipeline in data.get("pipelines", []):
            if "progress" in pipeline:
                pipeline["progress"] = min(100, max(0, pipeline.get("progress", 0)))
            for goal in pipeline.get("goals", []):
                if "progress" in goal:
                    goal["progress"] = min(100, max(0, goal.get("progress", 0)))

def simulate_cycle_progress():
    """Simuliert den Fortschritt des GENXAIS-Zyklus"""
    print("Simuliere GENXAIS-Zyklus-Fortschritt...")
    
    # Lade aktuelle Daten
    try:
        with open(PHASES_FILE, 'r', encoding='utf-8') as f:
            phases_data = json.load(f)
        
        with open(PIPELINES_FILE, 'r', encoding='utf-8') as f:
            pipelines_data = json.load(f)
        
        version = phases_data.get("version", get_version())
        decision_map_file = GRAPHITI_DIR / DECISION_MAP_FILE_TEMPLATE.format(version)
        
        with open(decision_map_file, 'r', encoding='utf-8') as f:
            graphiti_data = json.load(f)
    except Exception as e:
        print(f"Fehler beim Laden der Daten: {e}")
        return
    
    # Simuliere Fortschritt für jede Phase
    current_phase_index = 0
    for i, phase in enumerate(phases_data.get("phases", [])):
        if phase.get("status") == "active":
            current_phase_index = i
            break
    
    # Simuliere Phasen-Fortschritt
    for _ in range(5):  # 5 Simulationsschritte
        # Aktualisiere aktuelle Phase
        current_phase = phases_data["phases"][current_phase_index]
        current_phase["progress"] = min(100, current_phase["progress"] + 20)
        
        # Aktualisiere Tasks
        for task in current_phase.get("tasks", []):
            if task.get("status") == "pending":
                task["status"] = "active"
                task["progress"] = 25
                break
            elif task.get("status") == "active":
                task["progress"] = min(100, task["progress"] + 25)
                if task["progress"] >= 100:
                    task["progress"] = 100
                    task["status"] = "completed"
        
        # Prüfe, ob Phase abgeschlossen ist
        all_tasks_completed = all(task.get("status") == "completed" for task in current_phase.get("tasks", []))
        if all_tasks_completed:
            current_phase["status"] = "completed"
            current_phase["progress"] = 100
            
            # Wechsle zur nächsten Phase
            if current_phase_index < len(phases_data["phases"]) - 1:
                current_phase_index += 1
                phases_data["phases"][current_phase_index]["status"] = "active"
                phases_data["current_phase"] = phases_data["phases"][current_phase_index]["name"]
        
        # Aktualisiere Pipelines
        for pipeline in pipelines_data.get("pipelines", []):
            if pipeline.get("status") == "planning":
                pipeline["status"] = "active"
                pipeline["progress"] = 10
            elif pipeline.get("status") == "active":
                pipeline["progress"] = min(100, pipeline["progress"] + 15)
                if pipeline["progress"] >= 100:
                    pipeline["progress"] = 100
                    pipeline["status"] = "completed"
                
                # Aktualisiere Ziele
                for goal in pipeline.get("goals", []):
                    if goal.get("status") == "pending":
                        goal["status"] = "active"
                        goal["progress"] = 20
                        break
                    elif goal.get("status") == "active":
                        goal["progress"] = min(100, goal["progress"] + 20)
                        if goal["progress"] >= 100:
                            goal["progress"] = 100
                            goal["status"] = "completed"
                
                # Aktualisiere Laufzeit
                runtime = pipeline.get("runtime", "0h 0m")
                hours, minutes = runtime.split("h ")
                minutes = minutes.replace("m", "")
                hours = int(hours)
                minutes = int(minutes)
                minutes += 30
                if minutes >= 60:
                    hours += 1
                    minutes -= 60
                pipeline["runtime"] = f"{hours}h {minutes}m"
        
        # Aktualisiere Graphiti
        for node in graphiti_data.get("nodes", []):
            if node.get("id") == phases_data["current_phase"].lower():
                node["status"] = "active"
            elif node.get("type") == "phase" and node.get("id") in [p.get("name", "").lower() for p in phases_data.get("phases", []) if p.get("status") == "completed"]:
                node["status"] = "completed"
            
            if node.get("type") == "decision":
                phase_progress = {p.get("name"): p.get("progress", 0) for p in phases_data.get("phases", [])}
                if node.get("id") == "d1" and phase_progress.get("VAN", 0) > 30:
                    node["status"] = "completed"
                elif node.get("id") == "d2" and phase_progress.get("VAN", 0) > 60:
                    node["status"] = "completed"
                elif node.get("id") == "d3" and phase_progress.get("VAN", 0) > 90:
                    node["status"] = "active"
                elif node.get("id") == "d4" and phase_progress.get("PLAN", 0) > 50:
                    node["status"] = "active"
        
        # Aktualisiere DOT-Source
        dot_source_lines = graphiti_data.get("dot_source", "").split("\n")
        updated_dot_source = []
        for line in dot_source_lines:
            if "fillcolor=" in line:
                node_id = line.split("[")[0].strip()
                node_status = next((n.get("status") for n in graphiti_data.get("nodes", []) if n.get("id") == node_id), None)
                if node_status == "active":
                    line = line.replace("fillcolor=lightblue", "fillcolor=lightgreen")
                    line = line.replace("fillcolor=gold", "fillcolor=lightgreen")
                elif node_status == "completed":
                    line = line.replace("fillcolor=lightblue", "fillcolor=lightcyan")
                    line = line.replace("fillcolor=lightgreen", "fillcolor=lightcyan")
                    line = line.replace("fillcolor=gold", "fillcolor=lightcyan")
            updated_dot_source.append(line)
        graphiti_data["dot_source"] = "\n".join(updated_dot_source)
        
        # Normalisiere Fortschrittswerte
        normalize_progress_values(phases_data)
        normalize_progress_values(pipelines_data)
        
        # Speichere aktualisierte Daten
        phases_data["last_updated"] = datetime.datetime.now().isoformat()
        pipelines_data["last_updated"] = datetime.datetime.now().isoformat()
        graphiti_data["last_updated"] = datetime.datetime.now().isoformat()
        
        with open(PHASES_FILE, 'w', encoding='utf-8') as f:
            json.dump(phases_data, f, indent=2, ensure_ascii=False)
        
        with open(PIPELINES_FILE, 'w', encoding='utf-8') as f:
            json.dump(pipelines_data, f, indent=2, ensure_ascii=False)
        
        with open(decision_map_file, 'w', encoding='utf-8') as f:
            json.dump(graphiti_data, f, indent=2, ensure_ascii=False)
        
        # Warte kurz
        print(f"Fortschritt: Phase {phases_data['current_phase']}, Fortschritt {current_phase['progress']}%")
        time.sleep(2)

def main():
    """Hauptfunktion"""
    parser = argparse.ArgumentParser(description="GENXAIS Zyklus-Starter")
    parser.add_argument("--version", help="GENXAIS-Version (z.B. v1.5)")
    parser.add_argument("--increment", action="store_true", help="Version inkrementieren")
    parser.add_argument("--simulate", action="store_true", help="Zyklus-Fortschritt simulieren")
    args = parser.parse_args()
    
    # Version inkrementieren, falls gewünscht
    if args.increment:
        new_version = increment_version()
        print(f"Version inkrementiert auf {new_version}")
        version = new_version
    else:
        version = args.version or get_version()
    
    print(f"Starte GENXAIS-Zyklus für Version {version}...")
    
    # Lade Prompt
    prompt_data = load_prompt(version)
    if prompt_data is None:
        print(f"Fehler: Konnte Prompt für Version {version} nicht laden.")
        return
    
    # Initialisiere Dashboard-Daten
    initialize_dashboard_data(prompt_data, version)
    
    # Simuliere Zyklus-Fortschritt, falls gewünscht
    if args.simulate:
        simulate_cycle_progress()
    
    print(f"GENXAIS-Zyklus für Version {version} gestartet.")
    print(f"Dashboard-Daten wurden initialisiert.")
    print(f"Starte das Dashboard mit: python -m streamlit run scripts/enhanced_dashboard.py")

if __name__ == "__main__":
    main() 