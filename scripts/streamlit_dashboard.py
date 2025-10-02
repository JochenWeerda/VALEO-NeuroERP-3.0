#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GENXAIS Streamlit Dashboard
---------------------------
Dieses Skript startet ein Streamlit-Dashboard für die Überwachung des GENXAIS-Zyklus.
"""

import os
import sys
import json
import yaml
import time
import datetime
import streamlit as st
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import pandas as pd
import matplotlib.pyplot as plt
import glob

# Eigene Module importieren
try:
    # Verwende die vorhandenen Funktionen aus dem Dashboard-Modul
    from dashboard_prompt_module import (
        load_version, load_pipeline_status, load_handover as load_handover_module,
        load_tasks as load_tasks_module, load_memory_entries, save_prompt,
        save_prompt_to_file, get_current_prompt, check_rag_server_status
    )
except ImportError:
    # Füge das scripts-Verzeichnis zum Pfad hinzu
    sys.path.append(str(Path(__file__).resolve().parent))
    # Verwende die vorhandenen Funktionen aus dem Dashboard-Modul
    from dashboard_prompt_module import (
        load_version, load_pipeline_status, load_handover as load_handover_module,
        load_tasks as load_tasks_module, load_memory_entries, save_prompt,
        save_prompt_to_file, get_current_prompt, check_rag_server_status
    )

# Pfade konfigurieren
BASE_DIR = Path(__file__).resolve().parent.parent
TASKS_DIR = BASE_DIR / "tasks"
OUTPUT_DIR = BASE_DIR / "output"
MEMORY_BANK_DIR = BASE_DIR / "memory-bank"
CONFIG_PATH = OUTPUT_DIR / "dashboard_config.json"

# Streamlit-Konfiguration
st.set_page_config(
    page_title="GENXAIS v2.0 Dashboard",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Titel und Beschreibung
st.title("🌱 VALEO-NeuroERP v2.0 für Landhandel")
st.markdown("**GENXAIS v2.0 Monitoring Dashboard**")

# Seitenleiste
with st.sidebar:
    st.header("Navigation")
    page = st.radio(
        "Wähle eine Seite:",
        ["Übersicht", "Phasenstatus", "Pipelines", "Aufgaben", "Dokumente"]
    )
    
    st.header("Filter")
    pipeline_filter = st.multiselect(
        "Pipeline",
        ["API", "Frontend", "Backend", "Dokumentation", "Test", "DevOps", "Sicherheit"],
        default=["API", "Frontend", "Backend"]
    )
    
    st.header("Zeitraum")
    start_date = st.date_input("Startdatum", datetime.datetime.now().date())
    end_date = st.date_input("Enddatum", datetime.datetime.now().date())

# Farbschema
COLORS = {
    "completed": "#28a745",  # Grün
    "in_progress": "#ffc107",  # Gelb
    "pending": "#dc3545",  # Rot
    "background": "#f8f9fa",
    "text": "#212529",
    "accent": "#007bff"
}

# Hilfsfunktionen für das Dashboard
def load_config():
    """
    Lädt die Dashboard-Konfiguration.
    
    Returns:
        Dict mit der Konfiguration
    """
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Fehler beim Laden der Konfiguration: {str(e)}")
            return {
                "version": "v1.9",
                "phase": "VAN",
                "load_components": ["handover", "memorybank", "rag", "todos", "artefacts"],
                "start_time": datetime.datetime.now().isoformat()
            }
    
    # Wenn keine Konfiguration existiert, erstelle eine neue
    config = {
        "version": "v1.9",
        "phase": "VAN",
        "load_components": ["handover", "memorybank", "rag", "todos", "artefacts"],
        "start_time": datetime.datetime.now().isoformat()
    }
    save_config(config)
    return config

def save_config(config):
    """
    Speichert die Dashboard-Konfiguration.
    
    Args:
        config: Die zu speichernde Konfiguration
    """
    try:
        OUTPUT_DIR.mkdir(exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, default=str)
    except Exception as e:
        st.error(f"Fehler beim Speichern der Konfiguration: {str(e)}")

def load_tasks():
    """
    Lädt die Aufgaben aus der GENXAIS-Konfigurationsdatei.
    
    Returns:
        Dict mit den Aufgaben
    """
    # Verwende die vorhandene Funktion aus dem Dashboard-Modul
    tasks_data = load_tasks_module()
    
    if not tasks_data:
        # Fallback, wenn keine Aufgaben gefunden wurden
        return {
            "pipelines": [],
            "tasks": [],
            "status": {
                "completed": 0,
                "in_progress": 0,
                "pending": 0,
                "total": 0
            }
        }
    
    # Formatiere die Aufgaben für das Dashboard
    result = {
        "pipelines": [],
        "tasks": [],
        "status": {
            "completed": 0,
            "in_progress": 0,
            "pending": 0,
            "total": 0
        }
    }
    
    # Versuche, die Pipelines zu extrahieren
    pipelines = tasks_data.get("pipelines", [])
    
    for pipeline in pipelines:
        pipeline_name = pipeline.get("name", "Unbekannte Pipeline")
        pipeline_tasks = pipeline.get("tasks", [])
        
        # Zähle die Aufgaben nach Status
        completed = 0
        in_progress = 0
        pending = 0
        
        for task in pipeline_tasks:
            status = task.get("status", "pending")
            if status == "completed":
                completed += 1
            elif status == "in_progress":
                in_progress += 1
            else:
                pending += 1
        
        pipeline_data = {
            "name": pipeline_name,
            "tasks": len(pipeline_tasks),
            "completed": completed,
            "in_progress": in_progress,
            "pending": pending
        }
        
        result["pipelines"].append(pipeline_data)
        
        # Füge alle Aufgaben zur Gesamtliste hinzu
        for task in pipeline_tasks:
            task_data = {
                "pipeline": pipeline_name,
                "name": task.get("name", "Unbekannte Aufgabe"),
                "type": task.get("type", "unknown"),
                "details": task.get("details", ""),
                "status": task.get("status", "pending")
            }
            result["tasks"].append(task_data)
            
            # Aktualisiere Statusstatistiken
            if task.get("status") == "completed":
                result["status"]["completed"] += 1
            elif task.get("status") == "in_progress":
                result["status"]["in_progress"] += 1
            else:
                result["status"]["pending"] += 1
            
            result["status"]["total"] += 1
    
    return result

def load_reflections():
    """
    Lädt die Reflektionen aus dem Memory-Bank-Verzeichnis.
    
    Returns:
        Liste mit Reflektionen
    """
    # Verwende die vorhandene Funktion aus dem Dashboard-Modul
    return load_memory_entries(category="reflection", limit=10)

def load_handover():
    """
    Lädt das letzte Handover-Dokument.
    
    Returns:
        Dict mit Handover-Informationen
    """
    # Verwende die vorhandene Funktion aus dem Dashboard-Modul, aber ohne Parameter
    try:
        # Versuche zuerst, die Funktion ohne Parameter aufzurufen
        handover_content = load_handover_module()
    except TypeError:
        try:
            # Wenn das nicht funktioniert, versuche es mit einem leeren String
            handover_content = load_handover_module("")
        except:
            # Wenn auch das nicht funktioniert, setze handover_content auf None
            handover_content = None
        
    if not handover_content:
        return {}
    
    # Erstelle ein Handover-Objekt
    return {
        "date": datetime.datetime.now().isoformat(),
        "summary": handover_content[:500] + "..." if len(handover_content) > 500 else handover_content,
        "content": handover_content,
        "path": "data/handover/van_handover.md"
    }

def load_artifacts():
    """
    Lädt die Artefakte aus dem Output-Verzeichnis.
    
    Returns:
        Liste mit Artefakten
    """
    artifacts = []
    
    try:
        for file_path in OUTPUT_DIR.glob("*.md"):
            # Überspringe das Handover-Dokument
            if file_path.name == "handover.md":
                continue
            
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Extrahiere Metadaten aus dem Inhalt
                title = file_path.stem
                date = datetime.datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                
                # Extrahiere die ersten 200 Zeichen als Zusammenfassung
                summary = content[:200] + "..." if len(content) > 200 else content
                
                artifacts.append({
                    "title": title,
                    "date": date,
                    "summary": summary,
                    "path": str(file_path)
                })
            except Exception as e:
                st.error(f"Fehler beim Laden des Artefakts {file_path}: {str(e)}")
    except Exception as e:
        st.error(f"Fehler beim Durchsuchen des Output-Verzeichnisses: {str(e)}")
    
    # Sortiere nach Datum (neueste zuerst)
    artifacts.sort(key=lambda x: x["date"], reverse=True)
    
    return artifacts

def generate_dashboard_data():
    """
    Generiert die Daten für das Dashboard.
    
    Returns:
        Dict mit den Dashboard-Daten
    """
    config = load_config()
    tasks = load_tasks()
    reflections = load_reflections()
    handover = load_handover()
    artifacts = load_artifacts()
    
    # Aktualisiere die Konfiguration mit der aktuellen Zeit
    config["last_update"] = datetime.datetime.now().isoformat()
    save_config(config)
    
    return {
        "config": config,
        "tasks": tasks,
        "reflections": reflections,
        "handover": handover,
        "artifacts": artifacts
    }

def update_task_status(pipeline_name, task_name, new_status):
    """
    Aktualisiert den Status einer Aufgabe.
    
    Args:
        pipeline_name: Name der Pipeline
        task_name: Name der Aufgabe
        new_status: Neuer Status (completed, in_progress, pending)
        
    Returns:
        True, wenn erfolgreich, sonst False
    """
    tasks_file = TASKS_DIR / "genxais_cycle_v1.9.yaml"
    if not tasks_file.exists():
        st.error(f"Aufgabendatei nicht gefunden: {tasks_file}")
        return False
    
    try:
        with open(tasks_file, "r", encoding="utf-8") as f:
            tasks_data = yaml.safe_load(f)
        
        # Finde die Pipeline und die Aufgabe
        for pipeline in tasks_data.get("pipelines", []):
            if pipeline.get("name") == pipeline_name:
                for task in pipeline.get("tasks", []):
                    if task.get("name") == task_name:
                        task["status"] = new_status
                        
                        # Speichere die aktualisierte Konfiguration
                        with open(tasks_file, "w", encoding="utf-8") as f:
                            yaml.dump(tasks_data, f, default_flow_style=False, sort_keys=False)
                        
                        return True
        
        st.error(f"Aufgabe '{task_name}' in Pipeline '{pipeline_name}' nicht gefunden")
        return False
    except Exception as e:
        st.error(f"Fehler beim Aktualisieren des Aufgabenstatus: {str(e)}")
        return False

def generate_prompt():
    """
    Generiert einen Prompt für die GENXAIS-Initialisierung.
    
    Returns:
        String mit dem Prompt
    """
    config = load_config()
    tasks = load_tasks()
    handover = load_handover()
    
    # Erstelle den Prompt
    prompt = f"""# 🚀 GENXAIS v{config['version']} – Initialisierungsprompt zur Weiterentwicklung von VALEO – Die NeuroERP
Nutze langgraph-cycle-task, MCP RAG, MongoDB, memory-bank, todo, tasks
## 📁 Projektverzeichnis:
`{BASE_DIR}`  
**Streamlit UI Port:** 8502  
**Modus:** Multi-Pipeline  
**Startphase:** {config['phase']}  
**Letztes Handover:** `output/handover.md`

## 📊 Aufgabenstatus
- Abgeschlossen: {tasks.get('status', {}).get('completed', 0)}
- In Bearbeitung: {tasks.get('status', {}).get('in_progress', 0)}
- Ausstehend: {tasks.get('status', {}).get('pending', 0)}
- Gesamt: {tasks.get('status', {}).get('total', 0)}

## 📝 Letzte Handover-Zusammenfassung
{handover.get('summary', 'Kein Handover-Dokument gefunden.')}

## 🔄 Nächste Schritte
1. Führe die VAN-Phase durch, um den aktuellen Projektstatus zu analysieren
2. Erstelle einen Plan für die Implementierung der ausstehenden Aufgaben
3. Fokussiere auf die Verbesserung der Dokumentation und API-Spezifikation
4. Erhöhe die Testabdeckung auf 85%
5. Implementiere Sicherheitsmaßnahmen nach OWASP Top 10
"""
    
    # Speichere den Prompt
    prompt_path = OUTPUT_DIR / "genxais_prompt_v1.9.md"
    try:
        OUTPUT_DIR.mkdir(exist_ok=True)
        with open(prompt_path, "w", encoding="utf-8") as f:
            f.write(prompt)
    except Exception as e:
        st.error(f"Fehler beim Speichern des Prompts: {str(e)}")
    
    return prompt

def format_timestamp(timestamp: str) -> str:
    """
    Formatiert einen ISO-Zeitstempel in ein lesbares Format.
    
    Args:
        timestamp: ISO-Zeitstempel
        
    Returns:
        Formatierter Zeitstempel
    """
    try:
        dt = datetime.datetime.fromisoformat(timestamp)
        return dt.strftime("%d.%m.%Y %H:%M:%S")
    except:
        return timestamp

def render_header():
    """Rendert den Header des Dashboards."""
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.image("https://via.placeholder.com/150x150.png?text=GENXAIS", width=150)
    
    with col2:
        st.title("GENXAIS v1.9 Dashboard")
        st.subheader("Monitoring und Steuerung des GENXAIS-Zyklus")
        
        config = load_config()
        st.markdown(f"""
        **Version:** {config.get('version', 'v1.9')}  
        **Aktuelle Phase:** {config.get('phase', 'VAN')}  
        **Letzte Aktualisierung:** {format_timestamp(config.get('last_update', datetime.datetime.now().isoformat()))}
        """)

def render_phase_status():
    """Rendert den Status der Phasen."""
    st.header("📊 Phasenstatus")
    
    phases = ["VAN", "PLAN", "CREATE", "IMPLEMENTATION", "REFLEKTION"]
    config = load_config()
    current_phase = config.get('phase', 'VAN')
    
    # Bestimme den Status jeder Phase
    phase_status = {}
    for phase in phases:
        if phase == current_phase:
            phase_status[phase] = "in_progress"
        elif phases.index(phase) < phases.index(current_phase):
            phase_status[phase] = "completed"
        else:
            phase_status[phase] = "pending"
    
    # Zeige die Phasen als Fortschrittsbalken an
    cols = st.columns(len(phases))
    for i, (phase, col) in enumerate(zip(phases, cols)):
        status = phase_status[phase]
        color = COLORS[status]
        
        with col:
            st.markdown(f"<h4 style='text-align: center;'>{phase}</h4>", unsafe_allow_html=True)
            
            # Erstelle einen farbigen Balken basierend auf dem Status
            if status == "completed":
                st.progress(1.0)
                st.markdown(f"<p style='text-align: center; color: {color};'>✅ Abgeschlossen</p>", unsafe_allow_html=True)
            elif status == "in_progress":
                st.progress(0.5)
                st.markdown(f"<p style='text-align: center; color: {color};'>⏳ In Bearbeitung</p>", unsafe_allow_html=True)
            else:
                st.progress(0.0)
                st.markdown(f"<p style='text-align: center; color: {color};'>⏱️ Ausstehend</p>", unsafe_allow_html=True)

def render_pipeline_status():
    """Rendert den Status der Pipelines."""
    st.header("🔄 Pipeline-Status")
    
    tasks_data = load_tasks()
    pipelines = tasks_data.get("pipelines", [])
    
    if not pipelines:
        st.warning("Keine Pipeline-Daten verfügbar.")
        return
    
    # Erstelle eine Tabelle mit den Pipeline-Daten
    pipeline_data = []
    for pipeline in pipelines:
        name = pipeline.get("name", "Unbekannte Pipeline")
        total = pipeline.get("tasks", 0)
        completed = pipeline.get("completed", 0)
        in_progress = pipeline.get("in_progress", 0)
        pending = pipeline.get("pending", 0)
        
        # Berechne den Fortschritt in Prozent
        progress = (completed / total) * 100 if total > 0 else 0
        
        pipeline_data.append({
            "Name": name,
            "Gesamt": total,
            "Abgeschlossen": completed,
            "In Bearbeitung": in_progress,
            "Ausstehend": pending,
            "Fortschritt": f"{progress:.1f}%"
        })
    
    # Zeige die Tabelle an
    st.dataframe(pipeline_data)
    
    # Zeige einen Gesamtfortschritt an
    total_tasks = tasks_data.get("status", {}).get("total", 0)
    completed_tasks = tasks_data.get("status", {}).get("completed", 0)
    in_progress_tasks = tasks_data.get("status", {}).get("in_progress", 0)
    pending_tasks = tasks_data.get("status", {}).get("pending", 0)
    
    total_progress = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
    
    st.subheader("Gesamtfortschritt")
    st.progress(total_progress / 100)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Gesamt", total_tasks)
    with col2:
        st.metric("Abgeschlossen", completed_tasks)
    with col3:
        st.metric("In Bearbeitung", in_progress_tasks)
    with col4:
        st.metric("Ausstehend", pending_tasks)

def render_task_list():
    """Rendert die Liste der Aufgaben."""
    st.header("📝 Aufgabenliste")
    
    tasks_data = load_tasks()
    tasks = tasks_data.get("tasks", [])
    
    if not tasks:
        st.warning("Keine Aufgaben verfügbar.")
        return
    
    # Filter für den Status
    status_filter = st.selectbox(
        "Status filtern",
        ["Alle", "Abgeschlossen", "In Bearbeitung", "Ausstehend"],
        index=0
    )
    
    # Filter für die Pipeline
    pipelines = [pipeline.get("name") for pipeline in tasks_data.get("pipelines", [])]
    pipeline_filter = st.selectbox(
        "Pipeline filtern",
        ["Alle"] + pipelines,
        index=0
    )
    
    # Filtere die Aufgaben
    filtered_tasks = tasks
    if status_filter != "Alle":
        status_map = {
            "Abgeschlossen": "completed",
            "In Bearbeitung": "in_progress",
            "Ausstehend": "pending"
        }
        filtered_tasks = [task for task in filtered_tasks if task.get("status") == status_map[status_filter]]
    
    if pipeline_filter != "Alle":
        filtered_tasks = [task for task in filtered_tasks if task.get("pipeline") == pipeline_filter]
    
    # Zeige die gefilterten Aufgaben an
    for task in filtered_tasks:
        with st.expander(f"{task.get('name')} ({task.get('pipeline')})"):
            st.markdown(f"**Typ:** {task.get('type', 'Unbekannt')}")
            st.markdown(f"**Details:** {task.get('details', '')}")
            
            # Zeige den Status an und erlaube das Ändern
            status = task.get("status", "pending")
            status_map = {
                "completed": "Abgeschlossen",
                "in_progress": "In Bearbeitung",
                "pending": "Ausstehend"
            }
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**Status:** {status_map.get(status, 'Unbekannt')}")
            
            with col2:
                new_status = st.selectbox(
                    "Status ändern",
                    ["completed", "in_progress", "pending"],
                    index=["completed", "in_progress", "pending"].index(status),
                    key=f"status_{task.get('pipeline')}_{task.get('name')}"
                )
                
                if new_status != status:
                    if st.button("Aktualisieren", key=f"update_{task.get('pipeline')}_{task.get('name')}"):
                        success = update_task_status(
                            task.get("pipeline"),
                            task.get("name"),
                            new_status
                        )
                        
                        if success:
                            st.success("Status erfolgreich aktualisiert.")
                            st.rerun()
                        else:
                            st.error("Fehler beim Aktualisieren des Status.")

def render_reflections():
    """Rendert die Reflektionen."""
    st.header("🤔 Reflektionen")
    
    reflections = load_reflections()
    
    if not reflections:
        st.warning("Keine Reflektionen verfügbar.")
        return
    
    # Zeige die Reflektionen an
    for reflection in reflections:
        with st.expander(f"{reflection.get('title')} ({format_timestamp(reflection.get('date', ''))})"):
            st.markdown(reflection.get("content", ""))

def render_handover():
    """Rendert das Handover-Dokument."""
    st.header("📋 Handover")
    
    handover = load_handover()
    
    if not handover:
        st.warning("Kein Handover-Dokument verfügbar.")
        return
    
    # Zeige das Handover-Dokument an
    st.markdown(f"**Datum:** {format_timestamp(handover.get('date', ''))}")
    
    with st.expander("Handover-Dokument anzeigen"):
        st.markdown(handover.get("content", ""))

def render_artifacts():
    """Rendert die Artefakte."""
    st.header("📦 Artefakte")
    
    artifacts = load_artifacts()
    
    if not artifacts:
        st.warning("Keine Artefakte verfügbar.")
        return
    
    # Zeige die Artefakte an
    for artifact in artifacts:
        with st.expander(f"{artifact.get('title')} ({format_timestamp(artifact.get('date', ''))})"):
            st.markdown(artifact.get("summary", ""))
            
            # Zeige einen Link zum vollständigen Artefakt an
            st.markdown(f"[Vollständiges Artefakt anzeigen]({artifact.get('path')})")

def render_sidebar():
    """Rendert die Seitenleiste."""
    st.sidebar.title("GENXAIS v1.9")
    
    # Zeige die aktuelle Konfiguration an
    config = load_config()
    st.sidebar.subheader("Konfiguration")
    st.sidebar.markdown(f"""
    **Version:** {config.get('version', 'v1.9')}  
    **Phase:** {config.get('phase', 'VAN')}  
    **Start:** {format_timestamp(config.get('start_time', ''))}  
    **Letzte Aktualisierung:** {format_timestamp(config.get('last_update', ''))}
    """)
    
    # Zeige die Aufgabenstatistik an
    tasks_data = load_tasks()
    st.sidebar.subheader("Aufgabenstatistik")
    
    total_tasks = tasks_data.get("status", {}).get("total", 0)
    completed_tasks = tasks_data.get("status", {}).get("completed", 0)
    in_progress_tasks = tasks_data.get("status", {}).get("in_progress", 0)
    pending_tasks = tasks_data.get("status", {}).get("pending", 0)
    
    st.sidebar.markdown(f"""
    **Gesamt:** {total_tasks}  
    **Abgeschlossen:** {completed_tasks}  
    **In Bearbeitung:** {in_progress_tasks}  
    **Ausstehend:** {pending_tasks}
    """)
    
    # Zeige die Aktionen an
    st.sidebar.subheader("Aktionen")
    
    if st.sidebar.button("Dashboard aktualisieren"):
        st.rerun()
    
    if st.sidebar.button("Prompt generieren"):
        prompt = generate_prompt()
        st.sidebar.success("Prompt erfolgreich generiert.")
        
        with st.sidebar.expander("Prompt anzeigen"):
            st.code(prompt, language="markdown")
    
    # Zeige die Navigation an
    st.sidebar.subheader("Navigation")
    
    if st.sidebar.button("Phasenstatus"):
        st.session_state.section = "phase_status"
    
    if st.sidebar.button("Pipeline-Status"):
        st.session_state.section = "pipeline_status"
    
    if st.sidebar.button("Aufgabenliste"):
        st.session_state.section = "task_list"
    
    if st.sidebar.button("Reflektionen"):
        st.session_state.section = "reflections"
    
    if st.sidebar.button("Handover"):
        st.session_state.section = "handover"
    
    if st.sidebar.button("Artefakte"):
        st.session_state.section = "artifacts"

def main():
    """Hauptfunktion des Dashboards."""
    # Initialisiere die Session-State
    if "section" not in st.session_state:
        st.session_state.section = "phase_status"
    
    # Rendere die Seitenleiste
    render_sidebar()
    
    # Rendere den Header
    render_header()
    
    # Rendere die ausgewählte Sektion
    if st.session_state.section == "phase_status":
        render_phase_status()
    elif st.session_state.section == "pipeline_status":
        render_pipeline_status()
    elif st.session_state.section == "task_list":
        render_task_list()
    elif st.session_state.section == "reflections":
        render_reflections()
    elif st.session_state.section == "handover":
        render_handover()
    elif st.session_state.section == "artifacts":
        render_artifacts()
    
    # Rendere alle Sektionen, wenn keine ausgewählt ist
    else:
        render_phase_status()
        render_pipeline_status()
        render_task_list()
        render_reflections()
        render_handover()
        render_artifacts()

if __name__ == "__main__":
    main()
