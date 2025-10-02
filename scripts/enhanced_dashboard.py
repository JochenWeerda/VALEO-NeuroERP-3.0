***REMOVED***!/usr/bin/env python
***REMOVED*** -*- coding: utf-8 -*-

"""
GENXAIS Enhanced Streamlit Dashboard
Dieses Script erstellt ein verbessertes Streamlit-Dashboard zur Visualisierung des GENXAIS-Zyklus.
"""

import streamlit as st
import json
import time
import datetime
import os
import sys
from pathlib import Path
import pandas as pd
import altair as alt

***REMOVED*** Importiere die Versionskonfiguration
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.genxais_version import get_version, get_previous_version

***REMOVED*** Konfiguration
st.set_page_config(
    page_title="GENXAIS Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

***REMOVED*** Pfade
DATA_DIR = Path("data/dashboard")
DATA_DIR.mkdir(parents=True, exist_ok=True)
PHASES_PATH = DATA_DIR / "phases.json"
PIPELINES_PATH = DATA_DIR / "pipelines.json"
GRAPHITI_DIR = DATA_DIR / "graphiti"
GRAPHITI_DIR.mkdir(parents=True, exist_ok=True)
DECISION_MAP_FILE_TEMPLATE = "decision_map_{}.json"

***REMOVED*** Daten laden
@st.cache_data(ttl=10)  ***REMOVED*** Kürzerer TTL für häufigere Aktualisierungen
def load_data(version=None):
    """Lädt die Daten für das Dashboard"""
    if version is None:
        ***REMOVED*** Lade Version direkt aus der JSON-Datei
        try:
            with open("config/genxais_version.json", "r", encoding="utf-8") as f:
                version_data = json.load(f)
                version = version_data.get("current", "v1.8")
                ***REMOVED*** Debug-Ausgabe für die geladene Version
                print(f"Geladene Version aus genxais_version.json: {version}")
        except Exception as e:
            st.error(f"Fehler beim Laden der Version: {e}")
            version = "v1.8"  ***REMOVED*** Fallback
    
    ***REMOVED*** Pfade mit Version
    decision_map_path = GRAPHITI_DIR / DECISION_MAP_FILE_TEMPLATE.format(version)
    
    ***REMOVED*** Lade Phasen-Daten
    if PHASES_PATH.exists():
        try:
            with open(PHASES_PATH, 'r', encoding='utf-8') as f:
                phases = json.load(f)
                ***REMOVED*** Stelle sicher, dass die aktuelle Version verwendet wird
                phases["version"] = version
        except Exception as e:
            st.error(f"Fehler beim Laden der Phasen-Daten: {e}")
            phases = {"version": version, "phases": [], "current_phase": "Keine Phase aktiv"}
    else:
        phases = {"version": version, "phases": [], "current_phase": "Keine Phase aktiv"}
    
    ***REMOVED*** Lade Pipeline-Daten
    if PIPELINES_PATH.exists():
        try:
            with open(PIPELINES_PATH, 'r', encoding='utf-8') as f:
                pipelines = json.load(f)
                ***REMOVED*** Stelle sicher, dass die aktuelle Version verwendet wird
                pipelines["version"] = version
        except Exception as e:
            st.error(f"Fehler beim Laden der Pipeline-Daten: {e}")
            pipelines = {"version": version, "pipelines": []}
    else:
        pipelines = {"version": version, "pipelines": []}
    
    ***REMOVED*** Lade Graphiti-Daten
    if decision_map_path.exists():
        try:
            with open(decision_map_path, 'r', encoding='utf-8') as f:
                graphiti = json.load(f)
                ***REMOVED*** Stelle sicher, dass die aktuelle Version verwendet wird
                graphiti["version"] = version
        except Exception as e:
            st.error(f"Fehler beim Laden der Graphiti-Daten: {e}")
            graphiti = {"version": version, "dot_source": "digraph G { A -> B }"}
    else:
        graphiti = {"version": version, "dot_source": "digraph G { A -> B }"}
    
    ***REMOVED*** Normalisiere Fortschrittswerte
    normalize_progress_values(phases)
    normalize_progress_values(pipelines)
    
    return phases, pipelines, graphiti

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

***REMOVED*** Hilfsfunktionen
def format_timestamp(timestamp):
    """Formatiert einen Zeitstempel"""
    if timestamp:
        try:
            dt = datetime.datetime.fromisoformat(timestamp)
            return dt.strftime("%d.%m.%Y %H:%M:%S")
        except:
            return timestamp
    return "Keine Daten"

def get_status_color(status):
    """Gibt die Farbe für einen Status zurück"""
    status_colors = {
        "active": "***REMOVED***1E88E5",     ***REMOVED*** Blau
        "completed": "***REMOVED***4CAF50",  ***REMOVED*** Grün
        "pending": "***REMOVED***9E9E9E",    ***REMOVED*** Grau
        "planning": "***REMOVED***FFC107",   ***REMOVED*** Gelb
        "error": "***REMOVED***F44336"       ***REMOVED*** Rot
    }
    return status_colors.get(status.lower(), "***REMOVED***9E9E9E")

def create_phase_progress_chart(phases_data):
    """Erstellt ein Fortschrittsdiagramm für die Phasen"""
    ***REMOVED*** Daten für das Diagramm vorbereiten
    chart_data = []
    for phase in phases_data.get("phases", []):
        chart_data.append({
            "phase": phase.get("name", ""),
            "progress": min(100, max(0, phase.get("progress", 0))),  ***REMOVED*** Normalisiere Werte
            "status": phase.get("status", "pending")
        })
    
    ***REMOVED*** Dataframe erstellen
    df = pd.DataFrame(chart_data)
    if df.empty:
        return None
    
    ***REMOVED*** Chart erstellen
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('progress:Q', scale=alt.Scale(domain=[0, 100]), title='Fortschritt (%)'),
        y=alt.Y('phase:N', title='Phase', sort=None),
        color=alt.Color('status:N', 
                      scale=alt.Scale(
                          domain=['active', 'completed', 'pending', 'planning', 'error'],
                          range=['***REMOVED***1E88E5', '***REMOVED***4CAF50', '***REMOVED***9E9E9E', '***REMOVED***FFC107', '***REMOVED***F44336']
                      ),
                      title='Status'),
        tooltip=['phase:N', 'progress:Q', 'status:N']
    ).properties(
        title='Phasen-Fortschritt',
        width=600,
        height=300
    )
    
    return chart

def create_pipeline_progress_chart(pipelines_data):
    """Erstellt ein Fortschrittsdiagramm für die Pipelines"""
    ***REMOVED*** Daten für das Diagramm vorbereiten
    chart_data = []
    for pipeline in pipelines_data.get("pipelines", []):
        chart_data.append({
            "pipeline": pipeline.get("name", ""),
            "progress": float(min(100, max(0, pipeline.get("progress", 0)))),  ***REMOVED*** Normalisiere Werte und konvertiere zu float
            "status": pipeline.get("status", "pending"),
            "runtime": pipeline.get("runtime", "0h 0m")
        })
    
    ***REMOVED*** Dataframe erstellen
    df = pd.DataFrame(chart_data)
    if df.empty:
        return None
    
    ***REMOVED*** Debug-Ausgabe für Entwicklungszwecke
    ***REMOVED*** print(f"Pipeline DataFrame: {df}")
    
    ***REMOVED*** Chart erstellen
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('progress:Q', scale=alt.Scale(domain=[0, 100]), title='Fortschritt (%)'),
        y=alt.Y('pipeline:N', title='Pipeline', sort=None),
        color=alt.Color('status:N', 
                      scale=alt.Scale(
                          domain=['active', 'running', 'setup', 'finalizing', 'completed', 'pending', 'planning', 'error'],
                          range=['***REMOVED***1E88E5', '***REMOVED***1E88E5', '***REMOVED***42A5F5', '***REMOVED***64B5F6', '***REMOVED***4CAF50', '***REMOVED***9E9E9E', '***REMOVED***FFC107', '***REMOVED***F44336']
                      ),
                      title='Status'),
        tooltip=['pipeline:N', 'progress:Q', 'status:N', 'runtime:N']
    ).properties(
        title='Pipeline-Status',
        width=600,
        height=300
    )
    
    return chart

***REMOVED*** Dashboard-Layout
def main():
    """Hauptfunktion für das Dashboard"""
    ***REMOVED*** Version auswählen
    st.sidebar.title("GENXAIS Dashboard")
    current_version = get_version()
    previous_version = get_previous_version()
    
    ***REMOVED*** Versionswahl
    versions = [current_version, previous_version]
    selected_version = st.sidebar.selectbox("Version auswählen", versions, index=0)
    
    ***REMOVED*** Daten laden
    phases, pipelines, graphiti = load_data(selected_version)
    
    ***REMOVED*** Titel
    st.title(f"🔁 GENXAIS Zyklus – VALERO {selected_version}")
    st.markdown("Statusanzeige aller Phasen, Pipelines und Entscheidungspfade via Graphiti")
    
    ***REMOVED*** Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Seite auswählen", ["Übersicht", "Phasen", "Pipelines", "Graphiti", "Einstellungen"])
    
    ***REMOVED*** Auto-Refresh
    auto_refresh = st.sidebar.checkbox("Auto-Refresh", value=True)
    refresh_interval = st.sidebar.slider("Refresh-Intervall (Sekunden)", 5, 60, 30)
    
    ***REMOVED*** Übersichtsseite
    if page == "Übersicht":
        ***REMOVED*** Status-Karten
        col1, col2, col3 = st.columns(3)
        
        with col1:
            current_phase = phases.get("current_phase", "Keine Phase aktiv")
            st.info(f"Aktuelle Phase: **{current_phase}**")
        
        with col2:
            active_pipelines = sum(1 for pipeline in pipelines.get("pipelines", []) 
                                if pipeline.get("status") in ["active", "running", "setup", "finalizing"])
            total_pipelines = len(pipelines.get("pipelines", []))
            st.info(f"Aktive Pipelines: **{active_pipelines}/{total_pipelines}**")
        
        with col3:
            version = phases.get("version", selected_version)
            st.info(f"GENXAIS Version: **{version}**")
        
        ***REMOVED*** Fortschrittsdiagramme
        col1, col2 = st.columns(2)
        
        with col1:
            ***REMOVED*** Phasen-Fortschritt
            phase_chart = create_phase_progress_chart(phases)
            if phase_chart:
                st.altair_chart(phase_chart, use_container_width=True)
        
        with col2:
            ***REMOVED*** Pipeline-Fortschritt
            pipeline_chart = create_pipeline_progress_chart(pipelines)
            if pipeline_chart:
                st.altair_chart(pipeline_chart, use_container_width=True)
        
        ***REMOVED*** Graphiti Decision Map
        st.subheader("🧠 Graphiti – Decision Map")
        st.graphviz_chart(graphiti.get("dot_source", "digraph G { A -> B }"))
        
        ***REMOVED*** Letzte Aktualisierung
        st.markdown("---")
        last_updated_phases = format_timestamp(phases.get("last_updated", None))
        last_updated_pipelines = format_timestamp(pipelines.get("last_updated", None))
        st.caption(f"Letzte Aktualisierung: Phasen: {last_updated_phases}, Pipelines: {last_updated_pipelines}")
    
    ***REMOVED*** Phasen-Seite
    elif page == "Phasen":
        st.header(f"GENXAIS {selected_version} Phasen")
        
        ***REMOVED*** Phasen-Fortschritt
        phase_chart = create_phase_progress_chart(phases)
        if phase_chart:
            st.altair_chart(phase_chart, use_container_width=True)
        
        ***REMOVED*** Phasen-Details
        st.subheader("Phasen-Details")
        for phase in phases.get("phases", []):
            phase_name = phase.get("name", "Unbekannte Phase")
            phase_status = phase.get("status", "pending")
            phase_progress = min(100, max(0, phase.get("progress", 0)))  ***REMOVED*** Normalisiere Wert
            
            with st.expander(f"{phase_name} ({phase_status.capitalize()})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Fortschritt", f"{phase_progress}%")
                with col2:
                    st.metric("Status", phase_status.capitalize())
                
                ***REMOVED*** Fortschrittsbalken
                progress_value = float(phase_progress) / 100.0
                progress_value = min(1.0, max(0.0, progress_value))  ***REMOVED*** Sicherstellen, dass der Wert zwischen 0 und 1 liegt
                st.progress(progress_value)
                
                ***REMOVED*** Tasks
                st.subheader("Tasks")
                for task in phase.get("tasks", []):
                    task_name = task.get("name", "Unbekannte Task")
                    task_status = task.get("status", "pending")
                    task_progress = min(100, max(0, task.get("progress", 0)))  ***REMOVED*** Normalisiere Wert
                    
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.write(task_name)
                    with col2:
                        st.write(task_status.capitalize())
                    with col3:
                        st.write(f"{task_progress}%")
        
        ***REMOVED*** Letzte Aktualisierung
        st.markdown("---")
        last_updated = format_timestamp(phases.get("last_updated", None))
        st.caption(f"Letzte Aktualisierung: {last_updated}")
    
    ***REMOVED*** Pipelines-Seite
    elif page == "Pipelines":
        st.header(f"GENXAIS {selected_version} Pipelines")
        
        ***REMOVED*** Pipeline-Fortschritt
        pipeline_chart = create_pipeline_progress_chart(pipelines)
        if pipeline_chart:
            st.altair_chart(pipeline_chart, use_container_width=True)
        
        ***REMOVED*** Pipeline-Details
        st.subheader("Pipeline-Details")
        for pipeline in pipelines.get("pipelines", []):
            pipeline_name = pipeline.get("name", "Unbekannte Pipeline")
            pipeline_status = pipeline.get("status", "pending")
            pipeline_progress = min(100, max(0, pipeline.get("progress", 0)))  ***REMOVED*** Normalisiere Wert
            pipeline_runtime = pipeline.get("runtime", "0h 0m")
            
            with st.expander(f"{pipeline_name} ({pipeline_status.capitalize()})"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Fortschritt", f"{pipeline_progress}%")
                with col2:
                    st.metric("Status", pipeline_status.capitalize())
                with col3:
                    st.metric("Laufzeit", pipeline_runtime)
                
                ***REMOVED*** Fortschrittsbalken
                progress_value = float(pipeline_progress) / 100.0
                progress_value = min(1.0, max(0.0, progress_value))  ***REMOVED*** Sicherstellen, dass der Wert zwischen 0 und 1 liegt
                st.progress(progress_value)
                
                ***REMOVED*** Agenten
                st.subheader("Agenten")
                st.write(", ".join(pipeline.get("agents", [])))
                
                ***REMOVED*** Ziele
                st.subheader("Ziele")
                for goal in pipeline.get("goals", []):
                    goal_name = goal.get("name", "Unbekanntes Ziel")
                    goal_status = goal.get("status", "pending")
                    goal_progress = min(100, max(0, goal.get("progress", 0)))  ***REMOVED*** Normalisiere Wert
                    
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.write(goal_name)
                    with col2:
                        st.write(goal_status.capitalize())
                    with col3:
                        st.write(f"{goal_progress}%")
        
        ***REMOVED*** Letzte Aktualisierung
        st.markdown("---")
        last_updated = format_timestamp(pipelines.get("last_updated", None))
        st.caption(f"Letzte Aktualisierung: {last_updated}")
    
    ***REMOVED*** Graphiti-Seite
    elif page == "Graphiti":
        st.header(f"GENXAIS {selected_version} Graphiti Decision Map")
        
        ***REMOVED*** Decision Map
        st.subheader("Decision Map")
        st.graphviz_chart(graphiti.get("dot_source", "digraph G { A -> B }"))
        
        ***REMOVED*** Knoten- und Kantendetails
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Knoten")
            nodes_df = pd.DataFrame(graphiti.get("nodes", []))
            if not nodes_df.empty:
                st.dataframe(nodes_df, use_container_width=True)
        
        with col2:
            st.subheader("Kanten")
            edges_df = pd.DataFrame(graphiti.get("edges", []))
            if not edges_df.empty:
                st.dataframe(edges_df, use_container_width=True)
        
        ***REMOVED*** Letzte Aktualisierung
        st.markdown("---")
        last_updated = format_timestamp(graphiti.get("last_updated", None))
        st.caption(f"Letzte Aktualisierung: {last_updated}")
    
    ***REMOVED*** Einstellungen-Seite
    elif page == "Einstellungen":
        st.header("Dashboard-Einstellungen")
        
        ***REMOVED*** Allgemeine Einstellungen
        st.subheader("Allgemeine Einstellungen")
        st.write("Auto-Refresh Intervall: ", refresh_interval, " Sekunden")
        
        ***REMOVED*** Daten-Verzeichnisse
        st.subheader("Daten-Verzeichnisse")
        st.write("Hauptverzeichnis: ", DATA_DIR)
        st.write("Phasen-Datei: ", PHASES_PATH)
        st.write("Pipelines-Datei: ", PIPELINES_PATH)
        st.write("Graphiti-Verzeichnis: ", GRAPHITI_DIR)
        
        ***REMOVED*** Version
        st.subheader("Version")
        st.write("Aktuelle GENXAIS Version: ", current_version)
        st.write("Vorherige GENXAIS Version: ", previous_version)
        st.write("Ausgewählte Version: ", selected_version)
        st.write("Dashboard Version: 1.1.0")
        
        ***REMOVED*** Daten neu laden
        if st.button("Daten neu laden"):
            st.cache_data.clear()
            st.rerun()
    
    ***REMOVED*** Auto-Refresh
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()

if __name__ == "__main__":
    main() 