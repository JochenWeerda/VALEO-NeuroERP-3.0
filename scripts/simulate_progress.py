#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GENXAIS Fortschritts-Simulator
Dieses Skript simuliert den Fortschritt eines GENXAIS-Zyklus für Demonstrations- und Testzwecke.
"""

import os
import sys
import json
import argparse
import datetime
from pathlib import Path

# Konstanten
DATA_DIR = Path("data/dashboard")
PHASES_FILE = DATA_DIR / "phases.json"
PIPELINES_FILE = DATA_DIR / "pipelines.json"
GRAPHITI_DIR = DATA_DIR / "graphiti"
DECISION_MAP_FILE_TEMPLATE = "decision_map_{}.json"

def normalize_progress(value):
    """Normalisiert einen Fortschrittswert auf den Bereich 0-100"""
    return max(0, min(100, value))

def update_phase_progress(version, phase_name, progress):
    """Aktualisiert den Fortschritt einer Phase"""
    if not os.path.exists(PHASES_FILE):
        print(f"Fehler: Datei {PHASES_FILE} nicht gefunden.")
        return False
    
    try:
        with open(PHASES_FILE, 'r', encoding='utf-8') as f:
            phases_data = json.load(f)
        
        # Überprüfe, ob die Version übereinstimmt
        if phases_data.get("version") != version:
            print(f"Fehler: Version in {PHASES_FILE} ({phases_data.get('version')}) stimmt nicht mit der angegebenen Version ({version}) überein.")
            return False
        
        # Aktualisiere den Fortschritt der angegebenen Phase
        phase_found = False
        for phase in phases_data.get("phases", []):
            if phase.get("name") == phase_name:
                phase["progress"] = normalize_progress(progress)
                phase_found = True
                
                # Aktualisiere den Status basierend auf dem Fortschritt
                if progress < 5:
                    phase["status"] = "pending"
                elif progress < 100:
                    phase["status"] = "active"
                else:
                    phase["status"] = "completed"
                
                break
        
        if not phase_found:
            print(f"Fehler: Phase {phase_name} nicht gefunden.")
            return False
        
        # Aktualisiere den Zeitstempel
        phases_data["last_updated"] = datetime.datetime.now().isoformat()
        
        # Speichere die aktualisierten Daten
        with open(PHASES_FILE, 'w', encoding='utf-8') as f:
            json.dump(phases_data, f, indent=2, ensure_ascii=False)
        
        print(f"Fortschritt der Phase {phase_name} auf {progress}% aktualisiert.")
        return True
    
    except Exception as e:
        print(f"Fehler beim Aktualisieren des Fortschritts: {e}")
        return False

def update_pipeline_progress(version, pipeline_id, progress):
    """Aktualisiert den Fortschritt einer Pipeline"""
    if not os.path.exists(PIPELINES_FILE):
        print(f"Fehler: Datei {PIPELINES_FILE} nicht gefunden.")
        return False
    
    try:
        with open(PIPELINES_FILE, 'r', encoding='utf-8') as f:
            pipelines_data = json.load(f)
        
        # Überprüfe, ob die Version übereinstimmt
        if pipelines_data.get("version") != version:
            print(f"Fehler: Version in {PIPELINES_FILE} ({pipelines_data.get('version')}) stimmt nicht mit der angegebenen Version ({version}) überein.")
            return False
        
        # Aktualisiere den Fortschritt der angegebenen Pipeline
        pipeline_found = False
        for pipeline in pipelines_data.get("pipelines", []):
            if pipeline.get("id") == pipeline_id:
                pipeline["progress"] = normalize_progress(progress)
                pipeline_found = True
                
                # Aktualisiere den Status basierend auf dem Fortschritt
                if progress < 5:
                    pipeline["status"] = "planning"
                elif progress < 20:
                    pipeline["status"] = "setup"
                elif progress < 80:
                    pipeline["status"] = "running"
                elif progress < 100:
                    pipeline["status"] = "finalizing"
                else:
                    pipeline["status"] = "completed"
                
                break
        
        if not pipeline_found:
            print(f"Fehler: Pipeline {pipeline_id} nicht gefunden.")
            return False
        
        # Aktualisiere den Zeitstempel
        pipelines_data["last_updated"] = datetime.datetime.now().isoformat()
        
        # Speichere die aktualisierten Daten
        with open(PIPELINES_FILE, 'w', encoding='utf-8') as f:
            json.dump(pipelines_data, f, indent=2, ensure_ascii=False)
        
        print(f"Fortschritt der Pipeline {pipeline_id} auf {progress}% aktualisiert.")
        return True
    
    except Exception as e:
        print(f"Fehler beim Aktualisieren des Fortschritts: {e}")
        return False

def update_decision_map(version, node_id, status):
    """Aktualisiert den Status eines Knotens in der Decision Map"""
    decision_map_file = GRAPHITI_DIR / DECISION_MAP_FILE_TEMPLATE.format(version)
    
    if not os.path.exists(decision_map_file):
        print(f"Fehler: Datei {decision_map_file} nicht gefunden.")
        return False
    
    try:
        with open(decision_map_file, 'r', encoding='utf-8') as f:
            decision_map = json.load(f)
        
        # Aktualisiere den Status des angegebenen Knotens
        node_found = False
        for node in decision_map.get("nodes", []):
            if node.get("id") == node_id:
                node["status"] = status
                node_found = True
                break
        
        if not node_found:
            print(f"Fehler: Knoten {node_id} nicht gefunden.")
            return False
        
        # Speichere die aktualisierten Daten
        with open(decision_map_file, 'w', encoding='utf-8') as f:
            json.dump(decision_map, f, indent=2, ensure_ascii=False)
        
        print(f"Status des Knotens {node_id} auf '{status}' aktualisiert.")
        return True
    
    except Exception as e:
        print(f"Fehler beim Aktualisieren des Knotenstatus: {e}")
        return False

def update_task_progress(version, phase_name, task_index, progress):
    """Aktualisiert den Fortschritt einer Aufgabe"""
    if not os.path.exists(PHASES_FILE):
        print(f"Fehler: Datei {PHASES_FILE} nicht gefunden.")
        return False
    
    try:
        with open(PHASES_FILE, 'r', encoding='utf-8') as f:
            phases_data = json.load(f)
        
        # Überprüfe, ob die Version übereinstimmt
        if phases_data.get("version") != version:
            print(f"Fehler: Version in {PHASES_FILE} ({phases_data.get('version')}) stimmt nicht mit der angegebenen Version ({version}) überein.")
            return False
        
        # Aktualisiere den Fortschritt der angegebenen Aufgabe
        phase_found = False
        task_found = False
        for phase in phases_data.get("phases", []):
            if phase.get("name") == phase_name:
                phase_found = True
                tasks = phase.get("tasks", [])
                if 0 <= task_index < len(tasks):
                    tasks[task_index]["progress"] = normalize_progress(progress)
                    task_found = True
                    
                    # Aktualisiere den Status basierend auf dem Fortschritt
                    if progress < 5:
                        tasks[task_index]["status"] = "pending"
                    elif progress < 100:
                        tasks[task_index]["status"] = "in_progress"
                    else:
                        tasks[task_index]["status"] = "completed"
                    
                    # Berechne den Durchschnittsfortschritt der Phase
                    total_progress = sum(task.get("progress", 0) for task in tasks)
                    phase["progress"] = normalize_progress(total_progress / len(tasks))
                    
                    break
        
        if not phase_found:
            print(f"Fehler: Phase {phase_name} nicht gefunden.")
            return False
        
        if not task_found:
            print(f"Fehler: Aufgabe mit Index {task_index} in Phase {phase_name} nicht gefunden.")
            return False
        
        # Aktualisiere den Zeitstempel
        phases_data["last_updated"] = datetime.datetime.now().isoformat()
        
        # Speichere die aktualisierten Daten
        with open(PHASES_FILE, 'w', encoding='utf-8') as f:
            json.dump(phases_data, f, indent=2, ensure_ascii=False)
        
        print(f"Fortschritt der Aufgabe {task_index} in Phase {phase_name} auf {progress}% aktualisiert.")
        return True
    
    except Exception as e:
        print(f"Fehler beim Aktualisieren des Fortschritts: {e}")
        return False

def update_goal_progress(version, pipeline_id, goal_index, progress):
    """Aktualisiert den Fortschritt eines Ziels"""
    if not os.path.exists(PIPELINES_FILE):
        print(f"Fehler: Datei {PIPELINES_FILE} nicht gefunden.")
        return False
    
    try:
        with open(PIPELINES_FILE, 'r', encoding='utf-8') as f:
            pipelines_data = json.load(f)
        
        # Überprüfe, ob die Version übereinstimmt
        if pipelines_data.get("version") != version:
            print(f"Fehler: Version in {PIPELINES_FILE} ({pipelines_data.get('version')}) stimmt nicht mit der angegebenen Version ({version}) überein.")
            return False
        
        # Aktualisiere den Fortschritt des angegebenen Ziels
        pipeline_found = False
        goal_found = False
        for pipeline in pipelines_data.get("pipelines", []):
            if pipeline.get("id") == pipeline_id:
                pipeline_found = True
                goals = pipeline.get("goals", [])
                if 0 <= goal_index < len(goals):
                    goals[goal_index]["progress"] = normalize_progress(progress)
                    goal_found = True
                    
                    # Aktualisiere den Status basierend auf dem Fortschritt
                    if progress < 5:
                        goals[goal_index]["status"] = "pending"
                    elif progress < 100:
                        goals[goal_index]["status"] = "in_progress"
                    else:
                        goals[goal_index]["status"] = "completed"
                    
                    # Berechne den Durchschnittsfortschritt der Pipeline
                    total_progress = sum(goal.get("progress", 0) for goal in goals)
                    pipeline["progress"] = normalize_progress(total_progress / len(goals))
                    
                    break
        
        if not pipeline_found:
            print(f"Fehler: Pipeline {pipeline_id} nicht gefunden.")
            return False
        
        if not goal_found:
            print(f"Fehler: Ziel mit Index {goal_index} in Pipeline {pipeline_id} nicht gefunden.")
            return False
        
        # Aktualisiere den Zeitstempel
        pipelines_data["last_updated"] = datetime.datetime.now().isoformat()
        
        # Speichere die aktualisierten Daten
        with open(PIPELINES_FILE, 'w', encoding='utf-8') as f:
            json.dump(pipelines_data, f, indent=2, ensure_ascii=False)
        
        print(f"Fortschritt des Ziels {goal_index} in Pipeline {pipeline_id} auf {progress}% aktualisiert.")
        return True
    
    except Exception as e:
        print(f"Fehler beim Aktualisieren des Fortschritts: {e}")
        return False

def main():
    """Hauptfunktion"""
    parser = argparse.ArgumentParser(description="GENXAIS Fortschritts-Simulator")
    parser.add_argument("--version", required=True, help="Version des GENXAIS-Zyklus (z.B. v1.7)")
    parser.add_argument("--phase", help="Name der Phase, deren Fortschritt aktualisiert werden soll")
    parser.add_argument("--pipeline", help="ID der Pipeline, deren Fortschritt aktualisiert werden soll")
    parser.add_argument("--node", help="ID des Knotens in der Decision Map, dessen Status aktualisiert werden soll")
    parser.add_argument("--task", type=int, help="Index der Aufgabe, deren Fortschritt aktualisiert werden soll")
    parser.add_argument("--goal", type=int, help="Index des Ziels, dessen Fortschritt aktualisiert werden soll")
    parser.add_argument("--progress", type=int, help="Neuer Fortschrittswert (0-100)")
    parser.add_argument("--status", help="Neuer Status (für Knoten in der Decision Map)")
    
    args = parser.parse_args()
    
    # Überprüfe, ob die erforderlichen Verzeichnisse existieren
    if not os.path.exists(DATA_DIR):
        print(f"Fehler: Verzeichnis {DATA_DIR} nicht gefunden.")
        return 1
    
    if not os.path.exists(GRAPHITI_DIR):
        print(f"Fehler: Verzeichnis {GRAPHITI_DIR} nicht gefunden.")
        return 1
    
    # Führe die entsprechende Aktion basierend auf den Argumenten aus
    if args.phase and args.progress is not None:
        if args.task is not None:
            update_task_progress(args.version, args.phase, args.task, args.progress)
        else:
            update_phase_progress(args.version, args.phase, args.progress)
    
    elif args.pipeline and args.progress is not None:
        if args.goal is not None:
            update_goal_progress(args.version, args.pipeline, args.goal, args.progress)
        else:
            update_pipeline_progress(args.version, args.pipeline, args.progress)
    
    elif args.node and args.status:
        update_decision_map(args.version, args.node, args.status)
    
    else:
        print("Fehler: Unzureichende Argumente. Verwende --help für weitere Informationen.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 