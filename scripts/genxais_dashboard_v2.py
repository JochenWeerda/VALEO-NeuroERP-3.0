# -*- coding: utf-8 -*-
import streamlit as st
import os
import json
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import glob

# Konfiguration
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
        ["Übersicht", "Phasenstatus", "Pipelines", "Aufgaben", "Dokumente", "Landhandel"]
    )
    
    st.header("Filter")
    pipeline_filter = st.multiselect(
        "Pipeline",
        ["API", "Frontend", "Backend", "Dokumentation", "Test", "DevOps", "Sicherheit", "Landhandel"],
        default=["API", "Frontend", "Backend", "Landhandel"]
    )
    
    st.header("Zeitraum")
    start_date = st.date_input("Startdatum", datetime.now().date())
    end_date = st.date_input("Enddatum", datetime.now().date())

# Hilfsfunktionen
def load_phase_results():
    """Lädt die Ergebnisse der Phasen aus den Dateien"""
    phases = ["van", "plan", "create", "implementation", "reflektion"]
    results = {}
    
    for phase in phases:
        file_path = f"output/{phase}_result.md"
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                results[phase] = f.read()
        else:
            results[phase] = "Keine Daten verfügbar"
    
    return results

def load_tasks():
    """Lädt die Aufgaben aus der YAML-Konfiguration"""
    # In einer echten Anwendung würde hier die YAML-Datei geparst werden
    # Hier verwenden wir Beispieldaten
    tasks = [
        {"name": "Landhandel-API-Endpunkte erstellen", "pipeline": "API", "status": "completed"},
        {"name": "KI-Endpunkte für Preisgestaltung", "pipeline": "API", "status": "in_progress"},
        {"name": "API-Dokumentation aktualisieren", "pipeline": "API", "status": "pending"},
        {"name": "Bestandsverwaltungs-Dashboard", "pipeline": "Frontend", "status": "completed"},
        {"name": "Saisonale Planungsansicht", "pipeline": "Frontend", "status": "in_progress"},
        {"name": "Mobile Optimierung", "pipeline": "Frontend", "status": "pending"},
        {"name": "KI-Modell für Preisgestaltung", "pipeline": "Backend", "status": "in_progress"},
        {"name": "Automatisierte Buchungsvorschläge", "pipeline": "Backend", "status": "pending"},
        {"name": "Datenmodell für Landhandel", "pipeline": "Backend", "status": "completed"},
        {"name": "Redis-Caching optimieren", "pipeline": "Backend", "status": "completed"},
        {"name": "Saatgut-Verwaltung", "pipeline": "Landhandel", "status": "completed"},
        {"name": "Düngemittel-Verwaltung", "pipeline": "Landhandel", "status": "completed"},
        {"name": "Pflanzenschutzmittel-Verwaltung", "pipeline": "Landhandel", "status": "completed"},
        {"name": "Bestandsverwaltung", "pipeline": "Landhandel", "status": "completed"},
        {"name": "Saisonale Planung", "pipeline": "Landhandel", "status": "completed"},
    ]
    return tasks

# Seiten
def show_overview():
    """Zeigt die Übersichtsseite an"""
    st.header("📊 Übersicht")
    
    # Fortschrittsbalken
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Abgeschlossene Phasen", "4/5", "+1")
    with col2:
        st.metric("Offene Aufgaben", "5", "-10")
    with col3:
        st.metric("Testabdeckung", "85%", "+10%")
    
    # Grafik: Aufgaben nach Pipeline
    st.subheader("Aufgaben nach Pipeline")
    tasks = load_tasks()
    pipeline_counts = {}
    for task in tasks:
        pipeline = task["pipeline"]
        if pipeline in pipeline_counts:
            pipeline_counts[pipeline] += 1
        else:
            pipeline_counts[pipeline] = 1
    
    fig, ax = plt.subplots()
    ax.bar(pipeline_counts.keys(), pipeline_counts.values())
    ax.set_ylabel("Anzahl Aufgaben")
    ax.set_title("Aufgaben nach Pipeline")
    st.pyplot(fig)
    
    # Neueste Aktivitäten
    st.subheader("Neueste Aktivitäten")
    activities = [
        {"time": "2025-07-04 10:30:00", "description": "IMPLEMENTATION-Phase abgeschlossen"},
        {"time": "2025-07-04 09:15:22", "description": "Redis-Caching für Landhandel-Module konfiguriert"},
        {"time": "2025-07-04 08:45:15", "description": "Testdaten für Landhandel-Module erstellt"},
        {"time": "2025-07-03 14:05:37", "description": "GENXAIS Zyklus v1.9 abgeschlossen"},
        {"time": "2025-07-03 14:04:12", "description": "IMPLEMENTATION-Phase gestartet"},
        {"time": "2025-07-03 13:45:22", "description": "CREATE-Phase abgeschlossen"}
    ]
    activities_df = pd.DataFrame(activities)
    st.table(activities_df)

def show_phase_status():
    """Zeigt den Status der Phasen an"""
    st.header("🔄 Phasenstatus")
    
    phases = ["VAN", "PLAN", "CREATE", "IMPLEMENTATION", "REFLEKTION"]
    phase_status = {
        "VAN": "Abgeschlossen",
        "PLAN": "Abgeschlossen",
        "CREATE": "Abgeschlossen",
        "IMPLEMENTATION": "Abgeschlossen",
        "REFLEKTION": "In Vorbereitung"
    }
    
    # Phasen-Fortschritt
    for phase in phases:
        st.subheader(f"{phase}-Phase")
        progress = 1.0 if phase_status[phase] == "Abgeschlossen" else 0.0
        st.progress(progress)
        st.write(f"Status: {phase_status[phase]}")
    
    # Phasen-Ergebnisse
    st.subheader("Phasen-Ergebnisse")
    phase_results = load_phase_results()
    selected_phase = st.selectbox("Wähle eine Phase", list(phase_results.keys()))
    st.markdown(phase_results[selected_phase][:500] + "...")  # Zeige nur die ersten 500 Zeichen
    
    if st.button("Vollständiges Ergebnis anzeigen"):
        st.markdown(phase_results[selected_phase])

def show_pipelines():
    """Zeigt den Status der Pipelines an"""
    st.header("🔄 Pipelines")
    
    pipelines = [
        {"name": "API-Pipeline", "status": "Aktiv", "progress": 0.65},
        {"name": "Frontend-Pipeline", "status": "Aktiv", "progress": 0.45},
        {"name": "Backend-Pipeline", "status": "Aktiv", "progress": 0.70},
        {"name": "Landhandel-Pipeline", "status": "Abgeschlossen", "progress": 1.0},
        {"name": "Dokumentations-Pipeline", "status": "Geplant", "progress": 0.0},
        {"name": "Test-Pipeline", "status": "Geplant", "progress": 0.0},
        {"name": "DevOps-Pipeline", "status": "Geplant", "progress": 0.0},
        {"name": "Sicherheits-Pipeline", "status": "Geplant", "progress": 0.0}
    ]
    
    # Filtere Pipelines
    filtered_pipelines = [p for p in pipelines if p["name"].split("-")[0] in pipeline_filter]
    
    # Pipeline-Status
    for pipeline in filtered_pipelines:
        st.subheader(pipeline["name"])
        st.progress(pipeline["progress"])
        st.write(f"Status: {pipeline['status']}")
        st.write(f"Fortschritt: {int(pipeline['progress'] * 100)}%")
    
    # Pipeline-Metriken
    st.subheader("Pipeline-Metriken")
    metrics = {
        "API-Pipeline": {"Endpunkte": 25, "Tests": 18, "Dokumentation": 15},
        "Frontend-Pipeline": {"Komponenten": 12, "Tests": 8, "Responsive": "Ja"},
        "Backend-Pipeline": {"Modelle": 15, "KI-Modelle": 3, "Cache-Hit-Rate": "75%"},
        "Landhandel-Pipeline": {"Modelle": 7, "API-Endpunkte": 12, "Frontend-Komponenten": 1}
    }
    
    for pipeline_name, metric in metrics.items():
        if pipeline_name.split("-")[0] in pipeline_filter:
            st.write(f"**{pipeline_name}**")
            st.json(metric)

def show_tasks():
    """Zeigt die Aufgaben an"""
    st.header("📝 Aufgaben")
    
    tasks = load_tasks()
    
    # Filtere Aufgaben
    filtered_tasks = [t for t in tasks if t["pipeline"] in pipeline_filter]
    
    # Aufgabenliste
    st.subheader("Aufgabenliste")
    tasks_df = pd.DataFrame(filtered_tasks)
    st.dataframe(tasks_df)
    
    # Aufgaben nach Status
    st.subheader("Aufgaben nach Status")
    status_counts = {"pending": 0, "in_progress": 0, "completed": 0}
    for task in filtered_tasks:
        status_counts[task["status"]] += 1
    
    fig, ax = plt.subplots()
    ax.pie(status_counts.values(), labels=status_counts.keys(), autopct='%1.1f%%')
    ax.set_title("Aufgaben nach Status")
    st.pyplot(fig)

def show_documents():
    """Zeigt die Dokumente an"""
    st.header("📄 Dokumente")
    
    # Dokumentenliste
    st.subheader("Generierte Dokumente")
    documents = [
        {"name": "VAN-Ergebnis", "path": "output/van_result.md", "date": "2025-07-03"},
        {"name": "PLAN-Ergebnis", "path": "output/plan_result.md", "date": "2025-07-03"},
        {"name": "CREATE-Ergebnis", "path": "output/create_result.md", "date": "2025-07-03"},
        {"name": "IMPLEMENTATION-Ergebnis", "path": "output/implementation_result.md", "date": "2025-07-04"},
        {"name": "REFLEKTION-Ergebnis", "path": "output/reflektion_result.md", "date": "In Vorbereitung"},
        {"name": "Handover", "path": "output/handover.md", "date": "In Vorbereitung"}
    ]
    
    docs_df = pd.DataFrame(documents)
    st.dataframe(docs_df)
    
    # Dokumentenvorschau
    st.subheader("Dokumentenvorschau")
    selected_doc = st.selectbox("Wähle ein Dokument", [d["name"] for d in documents if d["date"] != "In Vorbereitung"])
    selected_path = next((d["path"] for d in documents if d["name"] == selected_doc), None)
    
    if selected_path and os.path.exists(selected_path):
        with open(selected_path, "r", encoding="utf-8") as f:
            content = f.read()
            st.markdown(content[:500] + "...")  # Zeige nur die ersten 500 Zeichen
            
            if st.button("Vollständiges Dokument anzeigen"):
                st.markdown(content)

def show_landhandel():
    """Zeigt die Landhandel-Module an"""
    st.header("🌾 Landhandel-Module")
    
    # Übersicht
    st.subheader("Übersicht der implementierten Module")
    
    # Datenmodelle
    st.markdown("### Datenmodelle")
    datenmodelle = {
        "Produkt": "Basisklasse für alle Produkttypen",
        "Saatgut": "Spezialisierte Produktklasse für Saatgut",
        "Düngemittel": "Spezialisierte Produktklasse für Düngemittel",
        "Pflanzenschutzmittel": "Spezialisierte Produktklasse für Pflanzenschutzmittel",
        "Bestand": "Verwaltung von Produktbeständen",
        "BestandsBewegung": "Protokollierung von Bestandsbewegungen",
        "SaisonalePlanung": "Verwaltung von saisonalen Planungen"
    }
    
    for model, description in datenmodelle.items():
        st.write(f"**{model}**: {description}")
    
    # API-Endpunkte
    st.markdown("### API-Endpunkte")
    api_endpoints = [
        {"Endpunkt": "/api/v1/saatgut", "Methode": "GET", "Beschreibung": "Liste aller Saatgut-Produkte"},
        {"Endpunkt": "/api/v1/saatgut", "Methode": "POST", "Beschreibung": "Neues Saatgut-Produkt anlegen"},
        {"Endpunkt": "/api/v1/duengemittel", "Methode": "GET", "Beschreibung": "Liste aller Düngemittel-Produkte"},
        {"Endpunkt": "/api/v1/duengemittel", "Methode": "POST", "Beschreibung": "Neues Düngemittel-Produkt anlegen"},
        {"Endpunkt": "/api/v1/pflanzenschutzmittel", "Methode": "GET", "Beschreibung": "Liste aller Pflanzenschutzmittel-Produkte"},
        {"Endpunkt": "/api/v1/bestand", "Methode": "GET", "Beschreibung": "Liste aller Bestände"},
        {"Endpunkt": "/api/v1/bestand/bewegung", "Methode": "POST", "Beschreibung": "Neue Bestandsbewegung anlegen"},
        {"Endpunkt": "/api/v1/saisonplanung", "Methode": "POST", "Beschreibung": "Neue Saisonplanung anlegen"}
    ]
    
    api_df = pd.DataFrame(api_endpoints)
    st.dataframe(api_df)
    
    # Frontend-Komponenten
    st.markdown("### Frontend-Komponenten")
    st.write("**BestandsUebersicht**: Tabellarische Darstellung der Bestände mit Sortier- und Filterfunktionen")
    
    # Beispiel-Bestandsdaten
    st.markdown("### Beispiel-Bestandsdaten")
    bestand_data = [
        {"Produkt": "Winterweizen Premium", "Artikelnummer": "S-1001", "Lager": "Hauptlager", "Menge": 2500.0, "Mindestbestand": 500.0, "Status": "OK"},
        {"Produkt": "Sommergerste Standard", "Artikelnummer": "S-1002", "Lager": "Hauptlager", "Menge": 1800.0, "Mindestbestand": 400.0, "Status": "OK"},
        {"Produkt": "Mais Hybrid F1", "Artikelnummer": "S-2001", "Lager": "Kühlhalle", "Menge": 150.0, "Mindestbestand": 200.0, "Status": "Kritisch"},
        {"Produkt": "NPK 15-15-15", "Artikelnummer": "D-3001", "Lager": "Außenlager", "Menge": 5000.0, "Mindestbestand": 1000.0, "Status": "OK"},
        {"Produkt": "Kalkammonsalpeter", "Artikelnummer": "D-3002", "Lager": "Außenlager", "Menge": 3000.0, "Mindestbestand": 800.0, "Status": "OK"},
        {"Produkt": "Unkraut-Ex", "Artikelnummer": "P-4001", "Lager": "Kühlhalle", "Menge": 250.0, "Mindestbestand": 100.0, "Status": "OK"},
        {"Produkt": "Fungistop", "Artikelnummer": "P-4002", "Lager": "Kühlhalle", "Menge": 180.0, "Mindestbestand": 100.0, "Status": "OK"}
    ]
    
    bestand_df = pd.DataFrame(bestand_data)
    st.dataframe(bestand_df)
    
    # Grafik: Bestand nach Produkttyp
    st.markdown("### Bestand nach Produkttyp")
    produkt_typen = ["Saatgut", "Düngemittel", "Pflanzenschutzmittel"]
    mengen = [4450.0, 8000.0, 430.0]
    
    fig, ax = plt.subplots()
    ax.bar(produkt_typen, mengen)
    ax.set_ylabel("Menge")
    ax.set_title("Bestand nach Produkttyp")
    st.pyplot(fig)

# Hauptfunktion
def main():
    """Hauptfunktion"""
    if page == "Übersicht":
        show_overview()
    elif page == "Phasenstatus":
        show_phase_status()
    elif page == "Pipelines":
        show_pipelines()
    elif page == "Aufgaben":
        show_tasks()
    elif page == "Dokumente":
        show_documents()
    elif page == "Landhandel":
        show_landhandel()

if __name__ == "__main__":
    main()
