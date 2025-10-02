#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GENXAIS Cron-Zyklus-Updater
Aktualisiert automatisch den Fortschritt des GENXAIS-Zyklus für das Dashboard.
"""

import os
import json
import time
import random
import argparse
import datetime
from pathlib import Path
import sys

# Verzeichnisse und Dateien
DATA_DIR = Path("data/dashboard")
PHASES_FILE = DATA_DIR / "phases.json"
PIPELINES_FILE = DATA_DIR / "pipelines.json"
GRAPHITI_DIR = DATA_DIR / "graphiti"
DECISION_MAP_FILE_TEMPLATE = "decision_map_{}.json"

def get_version():
    """Gibt die aktuelle GENXAIS-Version zurück"""
    try:
        with open("config/genxais_version.json", "r", encoding="utf-8") as f:
            version_data = json.load(f)
        return version_data.get("current", "v1.8")
    except Exception:
        return "v1.8"  # Fallback

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

def update_cycle_progress(version, speed_factor=1.0):
    """Aktualisiert den Fortschritt des GENXAIS-Zyklus"""
    
    # Lade aktuelle Daten
    try:
        with open(PHASES_FILE, 'r', encoding='utf-8') as f:
            phases_data = json.load(f)
        
        with open(PIPELINES_FILE, 'r', encoding='utf-8') as f:
            pipelines_data = json.load(f)
        
        decision_map_file = GRAPHITI_DIR / DECISION_MAP_FILE_TEMPLATE.format(version)
        
        with open(decision_map_file, 'r', encoding='utf-8') as f:
            graphiti_data = json.load(f)
    except Exception as e:
        print(f"Fehler beim Laden der Daten: {e}")
        return False
    
    # Finde aktuelle Phase
    current_phase_name = phases_data.get("current_phase", "VAN")
    current_phase = None
    current_phase_index = 0
    
    for i, phase in enumerate(phases_data.get("phases", [])):
        if phase.get("name") == current_phase_name:
            current_phase = phase
            current_phase_index = i
            break
    
    if current_phase is None:
        print("Fehler: Aktuelle Phase nicht gefunden.")
        return False
    
    # Aktualisiere Phase-Fortschritt
    progress_increment = random.uniform(1.0, 3.0) * speed_factor
    old_progress = current_phase["progress"]
    current_phase["progress"] = min(100, current_phase["progress"] + progress_increment)
    
    # Aktualisiere Tasks
    active_tasks = []
    completed_tasks = []
    for task in current_phase.get("tasks", []):
        if task.get("status") == "pending":
            task["status"] = "active"
            task["progress"] = random.uniform(5.0, 15.0) * speed_factor
            active_tasks.append(task["name"])
            break
        elif task.get("status") == "active":
            task_increment = random.uniform(2.0, 5.0) * speed_factor
            old_task_progress = task["progress"]
            task["progress"] = min(100, task["progress"] + task_increment)
            active_tasks.append(f"{task['name']} ({task['progress']:.1f}%)")
            if task["progress"] >= 100:
                task["progress"] = 100
                task["status"] = "completed"
                completed_tasks.append(task["name"])
    
    # Wechsle zur nächsten Phase, wenn aktuelle Phase zu 98% abgeschlossen ist
    phase_changed = False
    if current_phase["progress"] >= 98:
        current_phase["progress"] = 100
        current_phase["status"] = "completed"
        phase_changed = True
        
        # Setze alle Tasks auf completed
        for task in current_phase.get("tasks", []):
            task["status"] = "completed"
            task["progress"] = 100
        
        # Wechsle zur nächsten Phase
        if current_phase_index < len(phases_data["phases"]) - 1:
            next_phase_index = current_phase_index + 1
            next_phase = phases_data["phases"][next_phase_index]
            next_phase["status"] = "active"
            phases_data["current_phase"] = next_phase["name"]
            
            # Markiere erste Task als aktiv
            if next_phase.get("tasks"):
                next_phase["tasks"][0]["status"] = "active"
                next_phase["tasks"][0]["progress"] = random.uniform(5.0, 15.0) * speed_factor
    
    # Aktualisiere Pipelines basierend auf der aktuellen Phase
    phase_to_pipeline_progress = {
        "VAN": (0, 20),
        "PLAN": (20, 40),
        "CREATE": (40, 70),
        "IMPLEMENT": (70, 90),
        "REFLECT": (90, 100)
    }
    
    min_progress, max_progress = phase_to_pipeline_progress.get(current_phase_name, (0, 20))
    
    active_pipelines = []
    completed_pipelines = []
    
    for pipeline in pipelines_data.get("pipelines", []):
        # Bestimme Status basierend auf der aktuellen Phase
        if current_phase_name == "VAN":
            if pipeline.get("status") == "planning":
                continue
            pipeline["status"] = "planning"
        elif current_phase_name == "PLAN":
            if pipeline.get("status") == "planning" or pipeline.get("status") == "setup":
                pipeline["status"] = "setup"
            else:
                continue
        elif current_phase_name == "CREATE":
            if pipeline.get("status") in ["planning", "setup"]:
                pipeline["status"] = "running"
            elif pipeline.get("status") == "running":
                continue
        elif current_phase_name == "IMPLEMENT":
            if pipeline.get("status") in ["planning", "setup", "running"]:
                pipeline["status"] = "finalizing"
            elif pipeline.get("status") == "finalizing":
                continue
        elif current_phase_name == "REFLECT":
            if pipeline.get("status") != "completed":
                pipeline["status"] = "completed"
                pipeline["progress"] = 100
                completed_pipelines.append(pipeline["name"])
            continue
        
        # Aktualisiere Fortschritt basierend auf der aktuellen Phase
        if pipeline.get("status") != "completed":
            current_progress = pipeline.get("progress", 0)
            target_progress = random.uniform(min_progress, max_progress)
            
            if target_progress > current_progress:
                old_pipeline_progress = pipeline["progress"]
                progress_increment = random.uniform(1.0, 3.0) * speed_factor
                pipeline["progress"] = min(target_progress, current_progress + progress_increment)
                active_pipelines.append(f"{pipeline['name']} ({pipeline['progress']:.1f}%)")
        
        # Aktualisiere Ziele
        for goal in pipeline.get("goals", []):
            if goal.get("status") == "pending":
                goal["status"] = "active"
                goal["progress"] = random.uniform(5.0, 15.0) * speed_factor
                break
            elif goal.get("status") == "active":
                goal_increment = random.uniform(2.0, 6.0) * speed_factor
                goal["progress"] = min(100, goal["progress"] + goal_increment)
                if goal["progress"] >= 100:
                    goal["progress"] = 100
                    goal["status"] = "completed"
        
        # Aktualisiere Laufzeit
        runtime = pipeline.get("runtime", "0h 0m")
        hours, minutes = runtime.split("h ")
        minutes = minutes.replace("m", "")
        hours = int(hours)
        minutes = int(minutes)
        minutes += int(random.uniform(5, 15) * speed_factor)
        if minutes >= 60:
            hours += 1
            minutes -= 60
        pipeline["runtime"] = f"{hours}h {minutes}m"
    
    # Aktualisiere Graphiti Decision Map basierend auf der aktuellen Phase
    phase_to_decision_points = {
        "VAN": ["d1", "d2", "d3"],
        "PLAN": ["d4"],
        "CREATE": ["d5"],
        "IMPLEMENT": ["d6", "d7"],
        "REFLECT": ["d8"]
    }
    
    # Setze aktuelle Phase auf aktiv
    for node in graphiti_data.get("nodes", []):
        if node.get("id") == current_phase_name.lower():
            node["status"] = "active"
        elif node.get("type") == "phase" and node.get("id") in [p.get("name", "").lower() for p in phases_data.get("phases", []) if p.get("status") == "completed"]:
            node["status"] = "completed"
        
        # Aktualisiere Entscheidungspunkte
        if node.get("type") == "decision" and node.get("id") in phase_to_decision_points.get(current_phase_name, []):
            if current_phase["progress"] > 50:
                node["status"] = "active"
            if current_phase["progress"] > 90:
                node["status"] = "completed"
    
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
                line = line.replace("fillcolor=lightcyan", "fillcolor=lightgreen")
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
    
    # Erstelle detaillierte Ausgabe
    print(f"Fortschritt aktualisiert:")
    print(f"  Phase: {current_phase_name} ({old_progress:.1f}% → {current_phase['progress']:.1f}%)")
    
    if phase_changed:
        print(f"  Phase abgeschlossen! Wechsel zu: {phases_data['current_phase']}")
    
    if active_tasks:
        print(f"  Aktive Tasks: {', '.join(active_tasks)}")
    
    if completed_tasks:
        print(f"  Abgeschlossene Tasks: {', '.join(completed_tasks)}")
    
    if active_pipelines:
        print(f"  Aktive Pipelines: {', '.join(active_pipelines)}")
    
    if completed_pipelines:
        print(f"  Abgeschlossene Pipelines: {', '.join(completed_pipelines)}")
    
    return True

def main():
    """Hauptfunktion"""
    parser = argparse.ArgumentParser(description="GENXAIS Cron-Zyklus-Updater")
    parser.add_argument("--version", default=get_version(), help="GENXAIS-Version (z.B. v1.8)")
    parser.add_argument("--interval", type=int, default=60, help="Aktualisierungsintervall in Sekunden")
    parser.add_argument("--speed", type=float, default=1.0, help="Geschwindigkeitsfaktor für die Aktualisierung")
    parser.add_argument("--iterations", type=int, default=None, help="Anzahl der Aktualisierungen (None für unendlich)")
    args = parser.parse_args()
    
    print(f"Starte GENXAIS Cron-Zyklus-Updater für Version {args.version}")
    print(f"Intervall: {args.interval} Sekunden, Geschwindigkeit: {args.speed}x")
    
    iteration = 0
    while True:
        success = update_cycle_progress(args.version, args.speed)
        
        if not success:
            print("Fehler bei der Aktualisierung. Beende.")
            break
        
        iteration += 1
        if args.iterations is not None:
            print(f"Iteration {iteration}/{args.iterations} abgeschlossen")
            if iteration >= args.iterations:
                break
        
        time.sleep(args.interval)

if __name__ == "__main__":
    main() 