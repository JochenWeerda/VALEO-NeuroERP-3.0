#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GENXAIS Dashboard Prompt Module
-------------------------------
Dieses Modul stellt Funktionen für das Streamlit-Dashboard bereit und integriert
die Reflektion und Aufgaben für GENXAIS v1.9.
"""

import streamlit as st
import os
import sys
import json
import yaml
import time
import subprocess
from datetime import datetime
import glob
import re
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import logging

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('dashboard_prompt_module.log')
    ]
)
logger = logging.getLogger(__name__)

# Pfade konfigurieren
BASE_DIR = Path(__file__).resolve().parent.parent
TASKS_DIR = BASE_DIR / "tasks"
OUTPUT_DIR = BASE_DIR / "output"
MEMORY_BANK_DIR = BASE_DIR / "memory-bank"
CONFIG_PATH = "config/version.yaml"
PIPELINE_STATUS_PATH = "data/pipeline_status.json"
HANDOVER_PATH = "data/handover"
MEMORY_BANK_PATH = "memory-bank"
TASKS_PATH = "tasks"
RAG_TOKEN_PATH = "config/rag/api_token.json"
DASHBOARD_CONFIG_PATH = OUTPUT_DIR / "dashboard_config.json"
PROMPTS_DIR = BASE_DIR / "prompts"

# Standardkonfiguration
DEFAULT_CONFIG = {
    "version": "v1.9",
    "phase": "VAN",
    "load_components": ["handover", "memorybank", "rag", "todos", "artefacts"],
    "start_time": datetime.now().isoformat()
}

def load_config() -> Dict[str, Any]:
    """
    Lädt die Dashboard-Konfiguration.
    
    Returns:
        Dict mit der Konfiguration
    """
    if DASHBOARD_CONFIG_PATH.exists():
        try:
            with open(DASHBOARD_CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Fehler beim Laden der Konfiguration: {str(e)}")
            return DEFAULT_CONFIG
    
    # Wenn keine Konfiguration existiert, erstelle eine neue
    save_config(DEFAULT_CONFIG)
    return DEFAULT_CONFIG

def save_config(config: Dict[str, Any]) -> bool:
    """
    Speichert die Dashboard-Konfiguration.
    
    Args:
        config: Die zu speichernde Konfiguration
        
    Returns:
        True, wenn erfolgreich, sonst False
    """
    try:
        OUTPUT_DIR.mkdir(exist_ok=True)
        with open(DASHBOARD_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, default=str)
        return True
    except Exception as e:
        logger.error(f"Fehler beim Speichern der Konfiguration: {str(e)}")
        return False

def load_version():
    """Lädt die aktuelle Version aus der Konfigurationsdatei."""
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                version_config = yaml.safe_load(f)
                return version_config.get("current_version", "1.8.1")
        else:
            return "1.8.1"  # Fallback
    except Exception as e:
        st.error(f"Fehler beim Laden der Version: {str(e)}")
        return "1.8.1"  # Fallback

def load_pipeline_status():
    """Lädt den aktuellen Pipeline-Status."""
    try:
        if os.path.exists(PIPELINE_STATUS_PATH):
            with open(PIPELINE_STATUS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            return {"phase": "VAN", "progress": 0, "status": "idle"}
    except Exception as e:
        st.error(f"Fehler beim Laden des Pipeline-Status: {str(e)}")
        return {"phase": "VAN", "progress": 0, "status": "idle"}

def load_handover(phase):
    """Lädt den letzten Handover-Inhalt für eine bestimmte Phase."""
    try:
        handover_file = f"{HANDOVER_PATH}/{phase.lower()}_handover.md"
        if os.path.exists(handover_file):
            with open(handover_file, "r", encoding="utf-8") as f:
                return f.read()
        return None
    except Exception as e:
        st.error(f"Fehler beim Laden des Handovers: {str(e)}")
        return None

def load_tasks():
    """Lädt die verfügbaren Tasks aus der tasks.yaml Datei."""
    try:
        task_files = glob.glob(f"{TASKS_PATH}/*.yaml")
        if task_files:
            latest_task_file = max(task_files, key=os.path.getctime)
            with open(latest_task_file, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        return None
    except Exception as e:
        st.error(f"Fehler beim Laden der Tasks: {str(e)}")
        return None

def load_memory_entries(category="reflection", limit=5):
    """Lädt die letzten Memory-Einträge aus einer bestimmten Kategorie."""
    try:
        memory_files = glob.glob(f"{MEMORY_BANK_PATH}/{category}/*.md")
        entries = []
        
        if memory_files:
            # Sortiere nach Erstellungsdatum (neueste zuerst)
            sorted_files = sorted(memory_files, key=os.path.getctime, reverse=True)
            
            for file_path in sorted_files[:limit]:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Extrahiere Titel aus Markdown
                    title = os.path.basename(file_path)
                    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                    if match:
                        title = match.group(1)
                    
                    entries.append({
                        "title": title,
                        "path": file_path,
                        "date": datetime.fromtimestamp(os.path.getctime(file_path)).strftime("%Y-%m-%d %H:%M:%S"),
                        "content": content[:200] + "..." if len(content) > 200 else content
                    })
        
        return entries
    except Exception as e:
        st.error(f"Fehler beim Laden der Memory-Einträge: {str(e)}")
        return []

def save_prompt(prompt, directory="prompts"):
    """Speichert den generierten Prompt als Markdown-Datei."""
    try:
        os.makedirs(directory, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{directory}/genxais_prompt_{timestamp}.md"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(prompt)
        
        return filename
    except Exception as e:
        st.error(f"Fehler beim Speichern des Prompts: {str(e)}")
        return None

def save_prompt_to_file(prompt):
    """Speichert einen Prompt in der latest_prompt.json-Datei."""
    try:
        os.makedirs("data/cursor_prompts", exist_ok=True)
        
        # Prompt-Daten erstellen
        prompt_data = {
            "prompt": prompt,
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "phase": "GENERATED",
            "source": "streamlit_dashboard",
            "target": "cursor.ai",
            "version": load_version()
        }
        
        # Prompt in JSON-Datei speichern
        with open("data/cursor_prompts/latest_prompt.json", "w", encoding="utf-8") as file:
            json.dump(prompt_data, file, indent=2)
        
        return True
    except Exception as e:
        st.error(f"Fehler beim Speichern des Prompts: {str(e)}")
        return False

def get_current_prompt():
    """Liest den aktuellen Prompt aus der latest_prompt.json-Datei."""
    try:
        prompt_file = "data/cursor_prompts/latest_prompt.json"
        if os.path.exists(prompt_file):
            with open(prompt_file, "r", encoding="utf-8") as file:
                data = json.load(file)
                return data.get("prompt", "")
        return ""
    except Exception as e:
        st.error(f"Fehler beim Lesen des Prompts: {str(e)}")
        return ""

def check_rag_server_status(endpoint="http://localhost:8000/api/status"):
    """Prüft, ob der RAG-Server läuft."""
    try:
        response = requests.get(endpoint, timeout=2)
        if response.status_code == 200:
            return True, response.json()
        return False, None
    except Exception as e:
        return False, str(e)

def get_rag_api_token():
    """Liest den RAG-API-Token aus der Konfigurationsdatei."""
    try:
        if os.path.exists(RAG_TOKEN_PATH):
            with open(RAG_TOKEN_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("api_token", "")
        return ""
    except Exception as e:
        st.error(f"Fehler beim Lesen des RAG-API-Tokens: {str(e)}")
        return ""

def query_rag_server(query, endpoint="http://localhost:8000/api/query", token=None):
    """Sendet eine Abfrage an den RAG-Server."""
    try:
        if not token:
            token = get_rag_api_token()
            if not token:
                return False, "Kein API-Token verfügbar"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        data = {
            "query": query
        }
        
        response = requests.post(endpoint, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            return True, response.json()
        elif response.status_code == 401:
            return False, "Nicht autorisiert. Überprüfen Sie den API-Token."
        else:
            return False, f"Fehler: HTTP {response.status_code}"
    
    except Exception as e:
        return False, str(e)

def start_rag_server():
    """Startet den RAG-Server."""
    try:
        # Prüfe, ob der RAG-Server bereits läuft
        status, _ = check_rag_server_status()
        if status:
            return True, "RAG-Server läuft bereits."
        
        # Starte den RAG-Server
        process = subprocess.Popen(
            [sys.executable, "scripts/start_rag_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE  # Öffne ein neues Konsolenfenster
        )
        
        # Warte kurz, damit der Prozess starten kann
        time.sleep(2)
        
        # Prüfe, ob der Server gestartet wurde
        status, _ = check_rag_server_status()
        if status:
            return True, "RAG-Server erfolgreich gestartet."
        else:
            # Fehlerausgabe lesen
            stdout, stderr = process.communicate(timeout=1)
            if stderr:
                return False, f"Fehler beim Starten des RAG-Servers: {stderr}"
            return False, "RAG-Server konnte nicht gestartet werden."
    
    except Exception as e:
        return False, f"Fehler beim Starten des RAG-Servers: {str(e)}"

def generate_prompt(config):
    """Generiert einen Initialisierungsprompt basierend auf der Konfiguration."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Informationsquellen formatieren
    info_sources = "\n".join([f"- ✅ {q}" for q in config["infoquellen"]])
    
    # Startbefehl generieren
    info_params = ",".join([q.split()[0].lower() for q in config["infoquellen"]])
    debug_flag = "--debug" if config.get("debug_modus", False) else ""
    
    command = f"python -m streamlit run launch_cycle.py --phase {config['startphase']} --pipelines {config['anzahl_pipelines']} --load_info {info_params} {debug_flag} --timeout {config['timeout']}"
    
    # Zusätzliche Informationen sammeln
    additional_info = ""
    
    # Handover einbeziehen
    if "Letztes Handover" in config["infoquellen"]:
        handover = load_handover(config["startphase"])
        if handover:
            excerpt = handover[:300] + "..." if len(handover) > 300 else handover
            additional_info += f"\n\n## 📝 Letztes Handover (Auszug):\n```markdown\n{excerpt}\n```"
    
    # Memory-Bank einbeziehen
    if "Memory Bank" in config["infoquellen"]:
        memories = load_memory_entries()
        if memories:
            additional_info += "\n\n## 🧠 Letzte Memory-Einträge:\n"
            for i, memory in enumerate(memories[:3]):
                additional_info += f"### {memory['title']}\n"
                additional_info += f"*{memory['date']}*\n"
                additional_info += f"```\n{memory['content']}\n```\n"
    
    # Tasks einbeziehen
    if "Tasks.yaml" in config["infoquellen"]:
        tasks = load_tasks()
        if tasks:
            additional_info += "\n\n## ✅ Aktuelle Tasks:\n"
            try:
                for i, task in enumerate(tasks.get("tasks", [])[:5]):
                    additional_info += f"- **{task.get('name', 'Unbenannt')}**: {task.get('description', 'Keine Beschreibung')}\n"
            except:
                additional_info += "- Fehler beim Parsen der Tasks\n"
    
    # RAG-Server einbeziehen
    if "RAG-Server" in config["infoquellen"]:
        rag_token = config.get("rag_token", "")
        if rag_token:
            # Abfrage an den RAG-Server senden
            success, result = query_rag_server("Gib mir eine Zusammenfassung der aktuellen Projektlage", token=rag_token)
            if success:
                additional_info += "\n\n## 🔍 RAG-Server Antwort:\n"
                additional_info += f"```\n{result.get('response', 'Keine Antwort')}\n```\n"
            else:
                additional_info += "\n\n## 🔍 RAG-Server:\n"
                additional_info += f"Fehler bei der Abfrage des RAG-Servers: {result}\n"
        else:
            additional_info += "\n\n## 🔍 RAG-Server:\n"
            additional_info += "Kein API-Token für den RAG-Server angegeben.\n"
    
    # Aufgabentyp-spezifische Anweisungen
    task_instructions = get_task_instructions(config.get("aufgabentyp", "Code-Generierung"))
    
    # Prompt zusammenbauen - neues produktiveres Format
    prompt = f"""
# VALEO-NeuroERP Entwicklungsaufgabe

## Kontext
- **Projekt:** VALEO-NeuroERP v{config['version']}
- **Zeitstempel:** {timestamp}
- **Modus:** {config['modus']}
- **Phase:** {config['startphase']}
- **Aufgabentyp:** {config.get('aufgabentyp', 'Code-Generierung')}

## Aufgabenstellung
{config.get('aufgabenbeschreibung', 'Implementiere eine neue Komponente für das VALEO-NeuroERP-System.')}

## Spezifische Anweisungen
{task_instructions}

## Erwartete Ergebnisse
1. **Funktionierender Code:** Generiere lauffähigen Code, der direkt in das Projekt integriert werden kann
2. **Dokumentation:** Erstelle präzise Dokumentation für alle implementierten Funktionen
3. **Tests:** Entwickle passende Tests für die neuen Komponenten
4. **Integration:** Stelle sicher, dass deine Implementierung mit dem bestehenden System kompatibel ist

## Projektinformationen
{additional_info}

## Technische Anforderungen
- Halte dich an die bestehenden Coding-Standards des Projekts
- Implementiere fehlertoleranten Code mit angemessener Ausnahmebehandlung
- Achte auf Performance und Skalierbarkeit
- Berücksichtige Sicherheitsaspekte

## Lieferergebnisse
Bitte liefere folgende Artefakte:
1. Vollständigen Quellcode mit Kommentaren
2. Installationsanweisungen (falls erforderlich)
3. Dokumentation der API/Schnittstellen
4. Testfälle und erwartete Ergebnisse

## Hinweise zur Ausführung
```bash
{command}
```

Beginne mit der Implementierung der angeforderten Funktionalität. Konzentriere dich auf produktiven Code, der tatsächliche Ergebnisse liefert.
"""
    
    return prompt

def get_task_instructions(task_type):
    """Gibt aufgabenspezifische Anweisungen basierend auf dem Aufgabentyp zurück."""
    instructions = {
        "Code-Generierung": """
- Erstelle neuen, funktionierenden Code, der die beschriebene Funktionalität implementiert
- Achte auf eine klare Struktur und Modularität
- Implementiere eine vollständige Fehlerbehandlung
- Füge aussagekräftige Kommentare hinzu
- Berücksichtige Performance-Aspekte
""",
        "Komponenten-Integration": """
- Analysiere die bestehenden Komponenten und ihre Schnittstellen
- Entwickle den notwendigen Integrationscode
- Stelle sicher, dass alle Abhängigkeiten korrekt aufgelöst werden
- Implementiere geeignete Tests für die Integration
- Dokumentiere die Integrationsschritte
""",
        "Fehlerbehebung": """
- Analysiere den Fehler und identifiziere die Ursache
- Entwickle eine Lösung, die das Problem behebt
- Stelle sicher, dass keine neuen Fehler eingeführt werden
- Füge Tests hinzu, die den Fehlerfall abdecken
- Dokumentiere die Fehlerbehebung
""",
        "Refactoring": """
- Verbessere die Codequalität ohne die Funktionalität zu ändern
- Identifiziere und eliminiere Code-Duplikationen
- Verbessere die Lesbarkeit und Wartbarkeit
- Stelle durch Tests sicher, dass die Funktionalität erhalten bleibt
- Dokumentiere die Änderungen
""",
        "Test-Entwicklung": """
- Entwickle umfassende Tests für die beschriebene Komponente
- Decke normale Anwendungsfälle sowie Grenzfälle ab
- Implementiere Unit-Tests, Integrationstests und ggf. End-to-End-Tests
- Stelle sicher, dass die Tests reproduzierbar und wartbar sind
- Dokumentiere die Testabdeckung
""",
        "Dokumentation": """
- Erstelle eine umfassende Dokumentation für die beschriebene Komponente
- Beschreibe die Architektur, Schnittstellen und Verwendung
- Füge Beispiele für typische Anwendungsfälle hinzu
- Erstelle eine API-Dokumentation
- Achte auf Klarheit und Verständlichkeit
""",
        "Datenbank-Migration": """
- Entwickle Skripte für die Migration der Datenbankstruktur
- Stelle sicher, dass keine Daten verloren gehen
- Implementiere Rollback-Mechanismen für den Fehlerfall
- Teste die Migration mit repräsentativen Daten
- Dokumentiere den Migrationsprozess
""",
        "API-Entwicklung": """
- Entwerfe eine RESTful API für die beschriebene Funktionalität
- Implementiere alle notwendigen Endpunkte
- Stelle eine angemessene Fehlerbehandlung und Validierung sicher
- Dokumentiere die API mit OpenAPI/Swagger
- Implementiere Tests für alle Endpunkte
""",
        "UI-Komponente": """
- Entwickle eine benutzerfreundliche UI-Komponente
- Stelle sicher, dass die Komponente responsiv und zugänglich ist
- Implementiere eine saubere Trennung von Logik und Darstellung
- Berücksichtige Best Practices für UX/UI-Design
- Teste die Komponente auf verschiedenen Geräten und Browsern
"""
    }
    
    return instructions.get(task_type, "Implementiere die angeforderte Funktionalität gemäß den Best Practices.")

def render_prompt_generator():
    """Rendert den Prompt-Generator im Dashboard."""
    # Version und Pipeline-Status laden
    current_version = load_version()
    pipeline_status = load_pipeline_status()
    current_phase = pipeline_status.get("phase", "VAN")
    progress = pipeline_status.get("progress", 0)

    # Hauptbereich
    st.header("🧠 Prompt-Generator")
    col1, col2 = st.columns([2, 1])

    with col1:
        # Eingaben vom Nutzer
        pfad = st.text_input("📂 Projektpfad", "C:/Users/Jochen/VALEO-NeuroERP-1.01")
        modus = st.selectbox("⚙️ Betriebsmodus", ["Multi-Pipeline", "Single-Pipeline"], index=0)
        startphase = st.selectbox("🚀 Startphase", ["VAN", "PLAN", "CREATE", "IMPLEMENT", "VERIFY", "REFLECT"], index=0)

        # Aufgabentyp auswählen
        aufgabentyp = st.selectbox(
            "🎯 Aufgabentyp",
            [
                "Code-Generierung",
                "Komponenten-Integration",
                "Fehlerbehebung",
                "Refactoring",
                "Test-Entwicklung",
                "Dokumentation",
                "Datenbank-Migration",
                "API-Entwicklung",
                "UI-Komponente"
            ],
            index=0
        )
        
        # Spezifische Aufgabenbeschreibung
        aufgabenbeschreibung = st.text_area(
            "📝 Konkrete Aufgabenbeschreibung",
            "Implementiere eine neue Komponente für...",
            height=100
        )

        # Infoquellen Auswahl
        infoquellen = st.multiselect(
            "📡 Informationsquellen einbeziehen:",
            ["Memory Bank", "Tasks.yaml", "ToDos.md", "RAG-Server", "LangGraph", "Letztes Handover"],
            default=["Memory Bank", "Tasks.yaml", "Letztes Handover"]
        )

        # Erweiterte Optionen
        with st.expander("🔧 Erweiterte Optionen"):
            anzahl_pipelines = st.slider("Anzahl der Pipelines", 1, 10, 5)
            timeout = st.number_input("Timeout (Sekunden)", 60, 3600, 600)
            debug_modus = st.checkbox("Debug-Modus aktivieren", False)
            speichern = st.checkbox("Prompt automatisch speichern", True)
            
            # Memory-Bank Kategorien
            if "Memory Bank" in infoquellen:
                memory_categories = st.multiselect(
                    "Memory-Bank Kategorien",
                    ["reflection", "planning", "creative", "validation", "tasks"],
                    default=["reflection"]
                )
            
            # RAG-Server Einstellungen
            if "RAG-Server" in infoquellen:
                # RAG-Server Status prüfen
                rag_status, rag_info = check_rag_server_status()
                
                if rag_status:
                    st.success("✅ RAG-Server ist aktiv und erreichbar")
                else:
                    st.error(f"❌ RAG-Server ist nicht erreichbar: {rag_info}")
                    
                    # Button zum Starten des RAG-Servers
                    if st.button("RAG-Server starten"):
                        with st.spinner("Starte RAG-Server..."):
                            success, message = start_rag_server()
                            if success:
                                st.success(message)
                            else:
                                st.error(message)
                
                # RAG-Server Endpoint
                rag_endpoint = st.text_input("RAG-Server Endpoint", "http://localhost:8000/api/query")
                
                # RAG-Server API-Token
                default_token = get_rag_api_token()
                rag_token = st.text_input(
                    "RAG-Server API-Token", 
                    value=default_token,
                    type="password",
                    help="Der API-Token für den RAG-Server. Standardwert: valeo_rag_api_token_2025"
                )
                
                if not rag_token and default_token:
                    rag_token = default_token
                    st.info(f"API-Token aus Konfigurationsdatei geladen: {rag_token[:5]}...")

    # Konfiguration zusammenstellen
    config = {
        "pfad": pfad,
        "modus": modus,
        "startphase": startphase,
        "aufgabentyp": aufgabentyp,
        "aufgabenbeschreibung": aufgabenbeschreibung,
        "infoquellen": infoquellen,
        "anzahl_pipelines": anzahl_pipelines,
        "timeout": timeout,
        "debug_modus": debug_modus,
        "speichern": speichern,
        "version": current_version,
        "current_phase": current_phase,
        "progress": progress
    }
    
    # RAG-Server-Konfiguration hinzufügen, falls ausgewählt
    if "RAG-Server" in infoquellen:
        config["rag_endpoint"] = rag_endpoint
        config["rag_token"] = rag_token
    
    # Button zur Generierung
    if st.button("🧾 Initialisierungsprompt erstellen"):
        with st.spinner("Generiere Prompt..."):
            # Kurze Verzögerung für bessere UX
            time.sleep(0.5)
            
            # Prompt generieren
            prompt = generate_prompt(config)
            
            # Prompt anzeigen
            with col2:
                st.subheader("Generierter Prompt")
                st.code(prompt, language="markdown")
                
                # Download-Button
                st.download_button(
                    label="📥 Prompt herunterladen",
                    data=prompt,
                    file_name=f"genxais_prompt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown"
                )
                
                # Speichern-Option
                if speichern:
                    saved_path = save_prompt(prompt)
                    if saved_path:
                        st.success(f"Prompt gespeichert unter: {saved_path}")
                    
                    # Speichere für Cursor-Integration
                    save_prompt_to_file(prompt)

    # Aktions-Buttons
    st.subheader("Aktionen")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Button 1: Prompt in Zwischenablage kopieren
        if st.button("Prompt in Zwischenablage kopieren", key="send_to_clipboard"):
            with st.spinner("Kopiere Prompt in die Zwischenablage..."):
                try:
                    # Starte das cursor_clipboard.py-Skript als separaten Prozess
                    process = subprocess.Popen(
                        [sys.executable, "scripts/cursor_clipboard.py"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        creationflags=subprocess.CREATE_NEW_CONSOLE  # Öffne ein neues Konsolenfenster
                    )
                    
                    # Warte kurz, damit der Prozess starten kann
                    time.sleep(1)
                    
                    st.success("Skript zur Kopie des Prompts in die Zwischenablage gestartet!")
                    st.info("Bitte beachten Sie das neue Konsolenfenster für weitere Informationen.")
                    
                except Exception as e:
                    st.error(f"Fehler beim Starten des Skripts: {str(e)}")
    
    with col2:
        # Button 2: Prompt automatisch an Cursor.ai senden
        if st.button("Prompt automatisch an Cursor.ai senden", key="auto_send_to_cursor"):
            with st.spinner("Sende Prompt automatisch an Cursor.ai..."):
                try:
                    # Starte das cursor_auto_paste.py-Skript als separaten Prozess
                    process = subprocess.Popen(
                        [sys.executable, "scripts/cursor_auto_paste.py", "--force"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        creationflags=subprocess.CREATE_NEW_CONSOLE  # Öffne ein neues Konsolenfenster
                    )
                    
                    # Warte kurz, damit der Prozess starten kann
                    time.sleep(1)
                    
                    st.success("Skript zur automatischen Übergabe des Prompts an Cursor.ai gestartet!")
                    st.info("Bitte beachten Sie das neue Konsolenfenster für weitere Informationen.")
                    
                except Exception as e:
                    st.error(f"Fehler beim Starten des Skripts: {str(e)}")
    
    # MongoDB-Integration
    st.subheader("MongoDB-Integration")
    if st.button("Prompt in MongoDB speichern und an Cursor.ai senden", key="mongodb_auto_send"):
        with st.spinner("Speichere Prompt in MongoDB und sende an Cursor.ai..."):
            try:
                # Starte das mongodb_prompt_store.py-Skript als separaten Prozess
                process = subprocess.Popen(
                    [sys.executable, "scripts/mongodb_prompt_store.py", "--force"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    creationflags=subprocess.CREATE_NEW_CONSOLE  # Öffne ein neues Konsolenfenster
                )
                
                # Warte kurz, damit der Prozess starten kann
                time.sleep(1)
                
                st.success("Skript zur Speicherung des Prompts in MongoDB und Übergabe an Cursor.ai gestartet!")
                st.info("Bitte beachten Sie das neue Konsolenfenster für weitere Informationen.")
                
            except Exception as e:
                st.error(f"Fehler beim Starten des Skripts: {str(e)}")
    
    # Aktueller Prompt
    with st.expander("Aktueller Prompt"):
        current_prompt = get_current_prompt()
        if current_prompt:
            st.text_area(
                "Aktueller Prompt",
                value=current_prompt,
                height=200,
                disabled=True
            )
        else:
            st.info("Kein Prompt vorhanden.")

# Konfiguration laden
def load_config(version: str = "v1.9") -> Dict[str, Any]:
    """
    Lädt die Konfiguration für den angegebenen GENXAIS-Zyklus.
    
    Args:
        version: Version des GENXAIS-Zyklus (z.B. "v1.9")
        
    Returns:
        Dict mit der Konfiguration
    """
    config_path = TASKS_DIR / f"genxais_cycle_{version}.yaml"
    if not config_path.exists():
        config_path = TASKS_DIR / f"genxais_cycle_{version.replace('v', '')}.yaml"
    
    if not config_path.exists():
        raise FileNotFoundError(f"Keine Konfigurationsdatei für {version} gefunden.")
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            # Ignoriere YAML-Validierungsfehler und lade die Datei als einfachen Text
            content = f.read()
            # Versuche zuerst mit PyYAML zu laden
            try:
                config = yaml.safe_load(content)
            except Exception as e:
                print(f"YAML-Fehler: {str(e)}")
                # Fallback: Manuelles Parsen
                config = parse_yaml_manually(content)
    except Exception as e:
        print(f"Fehler beim Laden der Konfiguration: {str(e)}")
        # Fallback-Konfiguration
        config = {
            "name": f"GENXAIS Cycle {version}",
            "version": version.replace("v", ""),
            "pipelines": [],
            "agents": [],
            "artifacts": {"track": [], "priority": []}
        }
    
    return config

def parse_yaml_manually(content: str) -> Dict[str, Any]:
    """
    Parst YAML-Inhalt manuell, um mit ungültigen YAML-Dateien umzugehen.
    
    Args:
        content: YAML-Inhalt als String
        
    Returns:
        Dict mit dem geparsten Inhalt
    """
    config = {}
    
    # Einfaches Parsen von Schlüssel-Wert-Paaren
    lines = content.split("\n")
    current_section = None
    current_list = None
    current_dict = None
    
    for line in lines:
        line = line.rstrip()
        
        # Kommentare überspringen
        if line.strip().startswith("#") or not line.strip():
            continue
        
        # Einrückung zählen
        indent = len(line) - len(line.lstrip())
        
        # Neue Sektion
        if ":" in line and indent == 0:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            
            if value:
                # Einfacher Wert
                config[key] = value
            else:
                # Neue Sektion
                current_section = key
                config[current_section] = {}
                current_dict = config[current_section]
                current_list = None
        
        # Listeneintrag auf oberster Ebene
        elif line.strip().startswith("- ") and indent == 0:
            if current_section not in config:
                config[current_section] = []
            
            config[current_section].append(line.strip()[2:])
        
        # Listeneintrag in einer Sektion
        elif line.strip().startswith("- ") and indent == 2:
            if current_section not in config:
                config[current_section] = []
            
            if not isinstance(config[current_section], list):
                config[current_section] = []
            
            config[current_section].append(line.strip()[2:])
            current_list = config[current_section]
        
        # Schlüssel-Wert-Paar in einer Sektion
        elif ":" in line and indent == 2:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            
            if current_section not in config:
                config[current_section] = {}
            
            if not isinstance(config[current_section], dict):
                config[current_section] = {}
            
            if value:
                # Einfacher Wert
                config[current_section][key] = value
            else:
                # Neue Untersektion
                if key not in config[current_section]:
                    config[current_section][key] = {}
                current_dict = config[current_section][key]
                current_list = None
    
    # Pipelines speziell behandeln
    if "pipelines" in config and isinstance(config["pipelines"], list):
        # Versuche, die Pipelines aus dem Inhalt zu extrahieren
        pipelines = []
        in_pipeline = False
        current_pipeline = None
        
        for line in lines:
            if line.strip().startswith("- name:") and "pipelines:" in content[:content.find(line)]:
                in_pipeline = True
                current_pipeline = {"name": line.strip()[8:].strip('"\''), "tasks": []}
                pipelines.append(current_pipeline)
            elif in_pipeline and line.strip().startswith("agents:"):
                agents_str = line.strip()[8:].strip()
                if agents_str.startswith("[") and agents_str.endswith("]"):
                    agents = [a.strip('" \'') for a in agents_str[1:-1].split(",")]
                    current_pipeline["agents"] = agents
            elif in_pipeline and line.strip().startswith("goals:"):
                goals_str = line.strip()[7:].strip()
                if goals_str.startswith("[") and goals_str.endswith("]"):
                    goals = [g.strip('" \'') for g in goals_str[1:-1].split(",")]
                    current_pipeline["goals"] = goals
            elif in_pipeline and line.strip().startswith("- name:") and "tasks:" in content[:content.find(line)]:
                task = {"name": line.strip()[8:].strip('"\''), "status": "pending"}
                current_pipeline["tasks"].append(task)
            elif in_pipeline and line.strip().startswith("type:") and current_pipeline["tasks"]:
                current_pipeline["tasks"][-1]["type"] = line.strip()[6:].strip('"\'')
            elif in_pipeline and line.strip().startswith("details:") and current_pipeline["tasks"]:
                current_pipeline["tasks"][-1]["details"] = line.strip()[9:].strip('"\'')
            elif in_pipeline and line.strip().startswith("priority:") and current_pipeline["tasks"]:
                current_pipeline["tasks"][-1]["priority"] = line.strip()[10:].strip('"\'')
            elif in_pipeline and line.strip().startswith("status:") and current_pipeline["tasks"]:
                current_pipeline["tasks"][-1]["status"] = line.strip()[8:].strip('"\'')
        
        if pipelines:
            config["pipelines"] = pipelines
    
    return config

# Handover-Daten laden
def load_handover() -> Dict[str, Any]:
    """
    Lädt die Handover-Daten aus der letzten Ausführung.
    
    Returns:
        Dict mit Handover-Informationen
    """
    handover_path = OUTPUT_DIR / "handover.md"
    if not handover_path.exists():
        return {"error": "Keine Handover-Datei gefunden."}
    
    with open(handover_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Parse Markdown zu strukturierten Daten
    handover = {
        "title": "GENXAIS Zyklus Handover",
        "date": None,
        "phases": [],
        "pipelines": {},
        "artifacts": {},
        "next_steps": []
    }
    
    sections = content.split("## ")
    for section in sections:
        if not section.strip():
            continue
        
        lines = section.strip().split("\n")
        section_title = lines[0].strip()
        section_content = lines[1:]
        
        if section_title == "Zusammenfassung":
            for line in section_content:
                if "abgeschlossen" in line or "initialisiert" in line:
                    parts = line.split("am")
                    if len(parts) > 1:
                        date_str = parts[1].strip()
                        handover["date"] = date_str
        
        elif section_title == "Durchgeführte Phasen":
            handover["phases"] = [p.strip("- ") for p in section_content if p.strip()]
        
        elif section_title == "Pipelines und Ergebnisse":
            current_pipeline = None
            for line in section_content:
                if line.startswith("### "):
                    current_pipeline = line.strip("### ")
                    handover["pipelines"][current_pipeline] = []
                elif line.startswith("- ") and current_pipeline:
                    task = line.strip("- ")
                    handover["pipelines"][current_pipeline].append(task)
        
        elif section_title == "Erstellte Artefakte":
            handover["artifacts"] = {
                line.split(" (")[0].strip("- "): "nicht erstellt" in line 
                for line in section_content if line.strip()
            }
        
        elif section_title == "Nächste Schritte":
            handover["next_steps"] = [step.strip("- ") for step in section_content if step.strip()]
    
    return handover

# Aufgaben aus dem letzten Zyklus laden
def load_pending_tasks() -> Dict[str, List[Dict[str, str]]]:
    """
    Lädt die ausstehenden Aufgaben aus dem letzten Zyklus.
    
    Returns:
        Dict mit Pipeline-Namen als Schlüssel und Listen von Aufgaben als Werte
    """
    config = load_config()
    pending_tasks = {}
    
    for pipeline in config.get("pipelines", []):
        pipeline_name = pipeline.get("name")
        tasks = pipeline.get("tasks", [])
        
        pending_pipeline_tasks = []
        for task in tasks:
            if task.get("status") == "pending":
                pending_pipeline_tasks.append({
                    "name": task.get("name"),
                    "type": task.get("type"),
                    "details": task.get("details"),
                    "priority": task.get("priority", "medium")
                })
        
        if pending_pipeline_tasks:
            pending_tasks[pipeline_name] = pending_pipeline_tasks
    
    return pending_tasks

# Fehlende Artefakte identifizieren
def identify_missing_artifacts() -> List[str]:
    """
    Identifiziert fehlende Artefakte aus dem letzten Zyklus.
    
    Returns:
        Liste mit Namen der fehlenden Artefakte
    """
    handover = load_handover()
    missing_artifacts = []
    
    for artifact, is_missing in handover.get("artifacts", {}).items():
        if is_missing:
            missing_artifacts.append(artifact)
    
    return missing_artifacts

# Prompt für den nächsten Zyklus generieren
def generate_cycle_prompt(version: str = "v1.9") -> str:
    """
    Generiert ein Prompt für den nächsten GENXAIS-Zyklus.
    
    Args:
        version: Version des nächsten Zyklus
        
    Returns:
        String mit dem generierten Prompt
    """
    config = load_config(version)
    pending_tasks = load_pending_tasks()
    missing_artifacts = identify_missing_artifacts()
    
    prompt = f"""# 🚀 GENXAIS {version} – Initialisierungsprompt zur Weiterentwicklung von VALEO – Die NeuroERP
Nutze langgraph-cycle-task, MCP RAG, MongoDB, memory-bank, todo, tasks
## 📁 Projektverzeichnis:
`{BASE_DIR}`  
**Streamlit UI Port:** 8502  
**Modus:** Multi-Pipeline  
**Startphase:** VAN  
**Letztes Handover:** `output/handover.md`

---

## 🧠 Vorbereitete Aufgaben aus letzter Reflektion:

"""
    
    # Aufgaben nach Pipelines gruppieren
    for pipeline, tasks in pending_tasks.items():
        prompt += f"### {pipeline}:\n"
        for task in tasks:
            prompt += f"- [ ] {task['name']} (Typ: {task['type']})\n"
        prompt += "\n"
    
    prompt += """---

## 📦 Artefakte:
> 🔴 Alle geplanten Artefakte wurden im vorherigen Zyklus **nicht erstellt**.  
Diese sind als "not_created" in der memorybank gekennzeichnet und werden im Prompt dynamisch referenziert.

---

## 🧭 Nächste Schritte:
- ✅ Prüfung und Erzeugung aller offenen Artefakte
- ✅ Zusammenführen der Reflektion in `dashboard_prompt_module.py`
- ✅ Integration in das Hauptprojekt
- ✅ Automatisierte Planung & Start von GENXAIS v1.9 (via Cursor + LangGraph Agenten)

---

## ⚙️ Automatisierter Start:

```bash
python -m streamlit run scripts/streamlit_dashboard.py \\
  --server.port 8502 \\
  --phase VAN \\
  --cycle v1.9 \\
  --load handover memorybank rag todos artefacts
```
"""
    
    return prompt

# Dashboard-Status aktualisieren
def update_dashboard_status(status: Dict[str, Any]) -> None:
    """
    Aktualisiert den Status des Dashboards.
    
    Args:
        status: Dict mit Statusinformationen
    """
    status_path = OUTPUT_DIR / "dashboard_status.json"
    
    # Bestehenden Status laden, falls vorhanden
    if status_path.exists():
        with open(status_path, "r", encoding="utf-8") as f:
            current_status = json.load(f)
        
        # Status aktualisieren
        current_status.update(status)
    else:
        current_status = status
    
    # Status speichern
    with open(status_path, "w", encoding="utf-8") as f:
        json.dump(current_status, f, indent=2, ensure_ascii=False)

# Hauptfunktion zum Starten des Dashboards
def initialize_dashboard(version: str = "v1.9", phase: str = "VAN") -> Dict[str, Any]:
    """
    Initialisiert das Dashboard für den angegebenen GENXAIS-Zyklus.
    
    Args:
        version: Version des GENXAIS-Zyklus
        phase: Startphase des Zyklus
        
    Returns:
        Dict mit Initialisierungsinformationen
    """
    config = load_config(version)
    handover = load_handover()
    pending_tasks = load_pending_tasks()
    missing_artifacts = identify_missing_artifacts()
    
    # Dashboard-Status aktualisieren
    status = {
        "version": version,
        "phase": phase,
        "start_time": datetime.now().isoformat(),
        "config": config,
        "pending_tasks_count": sum(len(tasks) for tasks in pending_tasks.values()),
        "missing_artifacts_count": len(missing_artifacts),
        "pipelines_active": len(config.get("pipelines", [])),
        "agents_active": len(config.get("agents", [])),
    }
    
    update_dashboard_status(status)
    
    # Prompt generieren
    prompt = generate_cycle_prompt(version)
    prompt_path = OUTPUT_DIR / f"genxais_prompt_{version}.md"
    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write(prompt)
    
    return {
        "status": "initialized",
        "version": version,
        "phase": phase,
        "prompt_path": str(prompt_path),
        "dashboard_port": 8502
    }

if __name__ == "__main__":
    # Beim direkten Aufruf des Skripts
    if len(sys.argv) > 1:
        version = sys.argv[1]
    else:
        version = "v1.9"
    
    if len(sys.argv) > 2:
        phase = sys.argv[2]
    else:
        phase = "VAN"
    
    result = initialize_dashboard(version, phase)
    print(json.dumps(result, indent=2, ensure_ascii=False)) 