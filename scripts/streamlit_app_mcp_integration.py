***REMOVED***!/usr/bin/env python3
***REMOVED*** -*- coding: utf-8 -*-

"""
Streamlit-App mit MCP-SSE-Integration für VALEO-NeuroERP

Diese Datei implementiert eine Streamlit-App, die MCP-Server und Server-Sent Events
für Echtzeit-Updates und nahtlose Integration mit KI-Assistenten verwendet.
"""

import streamlit as st
import time
import json
import threading
import os
import yaml
import requests
import pyperclip
import openai
from flask import Flask, Response, request
from datetime import datetime

***REMOVED*** Konfiguration
CONFIG_PATH = "config/version.yaml"
PIPELINE_STATUS_PATH = "data/pipeline_status.json"
HANDOVER_PATH = "data/handover"
SSE_PORT = 5000
MCP_PORT = 6010

***REMOVED*** OpenAI API-Key konfigurieren
openai.api_key = os.environ.get("OPENAI_API_KEY")

***REMOVED*** Streamlit-App-Titel und Konfiguration
st.set_page_config(
    page_title="VALEO-NeuroERP Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

***REMOVED*** Hilfsfunktionen für Konfiguration und Status
def load_config():
    """Lädt die Konfiguration aus der YAML-Datei."""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as file:
            return yaml.safe_load(file)
    return {"current_version": "1.0.0"}

def get_current_version():
    """Gibt die aktuelle Version zurück."""
    config = load_config()
    return config.get("current_version", "1.0.0")

def load_pipeline_status():
    """Lädt den aktuellen Pipeline-Status."""
    if os.path.exists(PIPELINE_STATUS_PATH):
        with open(PIPELINE_STATUS_PATH, "r") as file:
            return json.load(file)
    return {"phase": "none", "progress": 0, "status": "idle", "completed": []}

def save_pipeline_status(status):
    """Speichert den Pipeline-Status."""
    os.makedirs(os.path.dirname(PIPELINE_STATUS_PATH), exist_ok=True)
    with open(PIPELINE_STATUS_PATH, "w") as file:
        json.dump(status, file)

def load_handover(phase):
    """Lädt den Handover-Inhalt für eine bestimmte Phase."""
    handover_file = f"{HANDOVER_PATH}/{phase.lower()}_handover.md"
    if os.path.exists(handover_file):
        with open(handover_file, "r") as file:
            return file.read()
    return None

def save_handover(phase, content):
    """Speichert den Handover-Inhalt für eine Phase."""
    os.makedirs(HANDOVER_PATH, exist_ok=True)
    handover_file = f"{HANDOVER_PATH}/{phase.lower()}_handover.md"
    with open(handover_file, "w") as file:
        file.write(content)

def call_chatgpt_api(prompt_template):
    """Ruft die ChatGPT API auf, um einen Prompt zu generieren."""
    try:
        if not openai.api_key:
            st.error("Kein OpenAI API-Key gefunden. Bitte setzen Sie die Umgebungsvariable OPENAI_API_KEY.")
            return "Fehler: Kein OpenAI API-Key gefunden."
            
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Du bist ein Prompt-Generator für das GENXAIS-Framework. Deine Aufgabe ist es, basierend auf Handover-Inhalten und Review-Änderungen einen optimalen Prompt für die nächste Phase zu erstellen."},
                {"role": "user", "content": prompt_template}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Fehler beim Aufruf der ChatGPT API: {str(e)}")
        return "Fehler bei der Prompt-Generierung. Bitte versuchen Sie es später erneut."

***REMOVED*** Vereinfachte MCP-Server-Implementierung ohne externe Abhängigkeit
class ValeoMCPServer:
    def __init__(self):
        self.tools = {}
        self.sse_clients = []
        self.register_tools()
        
    def tool(self, func):
        """Decorator für die Registrierung von Tools."""
        self.tools[func.__name__] = func
        return func
    
    def register_tools(self):
        """Registriert die Tools für den MCP-Server."""
        
        @self.tool
        def get_pipeline_status():
            """Gibt den aktuellen Status der Pipeline zurück."""
            return load_pipeline_status()
        
        @self.tool
        def update_pipeline_status(phase=None, progress=None, status=None):
            """Aktualisiert den Status der Pipeline."""
            current_status = load_pipeline_status()
            
            if phase is not None:
                current_status["phase"] = phase
            if progress is not None:
                current_status["progress"] = progress
            if status is not None:
                current_status["status"] = status
                if status == "completed" and phase is not None:
                    if "completed" not in current_status:
                        current_status["completed"] = []
                    current_status["completed"].append(phase)
            
            save_pipeline_status(current_status)
            self.send_sse_event("pipeline_status", current_status)
            return current_status
        
        @self.tool
        def get_handover_content(phase=None):
            """Gibt den Inhalt des Handovers für die angegebene Phase zurück."""
            if phase is None:
                current_status = load_pipeline_status()
                phase = current_status.get("phase", "none")
            
            content = load_handover(phase)
            return {"phase": phase, "content": content}
        
        @self.tool
        def save_handover_content(phase, content):
            """Speichert den Handover-Inhalt für eine Phase."""
            save_handover(phase, content)
            self.send_sse_event("handover", {"phase": phase, "content": content})
            return {"success": True}
        
        @self.tool
        def generate_prompt(handover_content, review_changes):
            """Generiert einen Prompt basierend auf Handover und Review-Änderungen."""
            prompt_template = f"""
            Basierend auf folgendem Handover:
            {handover_content}
            
            Und diesen Review-Änderungen:
            {review_changes}
            
            Generiere einen optimalen Prompt für die nächste Phase des GENXAIS-Frameworks.
            """
            
            ***REMOVED*** API-Aufruf an ChatGPT
            generated_prompt = call_chatgpt_api(prompt_template)
            
            self.send_sse_event("cursor_prompt", {"prompt": generated_prompt})
            return {"prompt": generated_prompt}
        
        @self.tool
        def cursor_integration(prompt, source="valeo_neuroerp", phase="", target="cursor.ai", use_langgraph=False):
            """Integriert einen Prompt mit Cursor.ai über MCP."""
            try:
                ***REMOVED*** Prompt in JSON-Datei speichern
                os.makedirs("data/cursor_prompts", exist_ok=True)
                prompt_data = {
                    "prompt": prompt,
                    "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "phase": phase,
                    "source": source,
                    "target": target,
                    "version": get_current_version()
                }
                
                with open("data/cursor_prompts/latest_prompt.json", "w") as file:
                    json.dump(prompt_data, file, indent=2)
                
                ***REMOVED*** Event senden
                self.send_sse_event("cursor_prompt", {"prompt": prompt})
                
                ***REMOVED*** Wenn Langgraph verwendet werden soll, hier Langgraph-Integration aufrufen
                if use_langgraph:
                    ***REMOVED*** Hier würde die Langgraph-Integration erfolgen
                    ***REMOVED*** Für dieses Beispiel simulieren wir nur den Aufruf
                    print("Langgraph-Integration für Cursor.ai aufgerufen")
                
                return {"success": True, "message": "Prompt an Cursor.ai gesendet"}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        @self.tool
        def get_version():
            """Gibt die aktuelle Version zurück."""
            return {"version": get_current_version()}
    
    def send_sse_event(self, event_type, data):
        """Sendet ein SSE-Event an alle registrierten Clients."""
        for client in self.sse_clients:
            try:
                client.put({"type": event_type, "data": data})
            except:
                ***REMOVED*** Client entfernen, wenn er nicht mehr erreichbar ist
                self.sse_clients.remove(client)
    
    def start(self):
        """Startet den MCP-Server."""
        ***REMOVED*** Hier würde normalerweise der Server gestartet werden
        ***REMOVED*** Da wir die externe Abhängigkeit entfernt haben, simulieren wir nur den Start
        print(f"MCP-Server gestartet auf Port {MCP_PORT}")
        return self

***REMOVED*** Flask-Server für SSE
app = Flask(__name__)
mcp_server = ValeoMCPServer()
event_queue = []

@app.route('/sse')
def sse():
    """SSE-Endpunkt für Echtzeit-Updates."""
    def event_stream():
        client_queue = []
        mcp_server.sse_clients.append(client_queue)
        
        try:
            ***REMOVED*** Initial-Status senden
            yield f"event: pipeline_status\ndata: {json.dumps(load_pipeline_status())}\n\n"
            
            while True:
                ***REMOVED*** Auf neue Events warten
                if client_queue:
                    event = client_queue.pop(0)
                    yield f"event: {event['type']}\ndata: {json.dumps(event['data'])}\n\n"
                else:
                    ***REMOVED*** Heartbeat senden, um die Verbindung aufrechtzuerhalten
                    yield f"event: heartbeat\ndata: {json.dumps({'time': time.time()})}\n\n"
                    time.sleep(1)
        except:
            ***REMOVED*** Client aus der Liste entfernen
            if client_queue in mcp_server.sse_clients:
                mcp_server.sse_clients.remove(client_queue)
    
    return Response(event_stream(), mimetype="text/event-stream")

@app.route('/cursor', methods=['POST'])
def cursor_prompt():
    """Endpunkt für die Übertragung von Prompts an cursor.ai."""
    data = request.json
    prompt = data.get('prompt', '')
    
    ***REMOVED*** Hier könnte eine direkte Integration mit cursor.ai erfolgen
    ***REMOVED*** Für dieses Beispiel kopieren wir den Prompt in die Zwischenablage
    pyperclip.copy(prompt)
    
    return {"success": True}

@app.route('/api/execute', methods=['POST'])
def api_execute():
    """API-Endpunkt für die Ausführung von MCP-Tools."""
    try:
        data = request.json
        tool_name = data.get('tool')
        params = data.get('params', {})
        
        if tool_name not in mcp_server.tools:
            return {"error": f"Tool {tool_name} nicht gefunden"}, 404
        
        ***REMOVED*** Tool ausführen
        result = mcp_server.tools[tool_name](**params)
        return result
    except Exception as e:
        return {"error": str(e)}, 500

@app.route('/api/status', methods=['GET'])
def api_status():
    """API-Endpunkt für den Status des MCP-Servers."""
    return {
        "status": "running",
        "version": get_current_version(),
        "tools": list(mcp_server.tools.keys())
    }

@app.route('/sse/status', methods=['GET'])
def sse_status():
    """API-Endpunkt für den Status des SSE-Servers."""
    return {
        "status": "running",
        "version": get_current_version(),
        "clients": len(mcp_server.sse_clients)
    }

***REMOVED*** Flask-Server in separatem Thread starten
def run_flask():
    app.run(port=SSE_PORT, threaded=True)

***REMOVED*** Streamlit-App-Komponenten
def create_header():
    """Erstellt den Header der Streamlit-App."""
    col1, col2 = st.columns([1, 3])
    with col1:
        ***REMOVED*** Logo anzeigen (falls vorhanden, sonst Text)
        try:
            st.image("C:/Users/Jochen/Pictures/VALEO -  Die NeuroERP/9fda3b64-198a-4f0f-b5d8-108d9376a541.png", width=100)
        except:
            st.markdown("**VALEO**")
    with col2:
        st.title(f"VALEO-NeuroERP v{get_current_version()}")
        st.caption("KI-gestütztes ERP-System mit Pipeline-Integration")

def create_sidebar():
    """Erstellt die Sidebar der Streamlit-App."""
    st.sidebar.header("Navigation")
    
    ***REMOVED*** Versionswechsler
    st.sidebar.subheader("Version")
    versions = ["1.0.0", "1.5.0", "1.8.1", "2.0.0"]
    current_version = get_current_version()
    selected_version = st.sidebar.selectbox("Wähle Version", versions, index=versions.index(current_version) if current_version in versions else 0)
    
    if selected_version != current_version:
        if st.sidebar.button("Version wechseln"):
            ***REMOVED*** Konfiguration aktualisieren
            config = load_config()
            config["current_version"] = selected_version
            with open(CONFIG_PATH, "w") as file:
                yaml.dump(config, file)
            st.sidebar.success(f"Version auf {selected_version} geändert. Seite wird neu geladen...")
            st.rerun()
    
    ***REMOVED*** GENXAIS-Framework-Toggle
    st.sidebar.subheader("GENXAIS-Framework")
    use_genxais = st.sidebar.toggle("Framework aktivieren", value=True)
    
    ***REMOVED*** Pipeline-Auswahl
    st.sidebar.subheader("Pipelines")
    available_pipelines = [
        "Edge-Validation-Pipeline",
        "Conflict-Analysis-Pipeline",
        "Edge-Refactoring-Pipeline",
        "Metrics-Definition-Pipeline",
        "Mutation-Aggregator-Pipeline"
    ]
    selected_pipelines = st.sidebar.multiselect("Aktive Pipelines", available_pipelines, default=available_pipelines[:3])
    
    if st.sidebar.button("Optimale Pipeline-Anzahl vorschlagen"):
        with st.sidebar.spinner("Analysiere Projekt..."):
            time.sleep(1)  ***REMOVED*** Simuliere Analyse
            st.sidebar.info("Basierend auf der Projektgröße und Komplexität werden 3 Pipelines empfohlen.")

def create_pipeline_status_section():
    """Erstellt den Bereich für den Pipeline-Status."""
    st.header("Pipeline-Fortschritt")
    
    ***REMOVED*** Status laden
    status = load_pipeline_status()
    
    ***REMOVED*** Fortschrittsbalken
    st.progress(status["progress"] / 100)
    
    ***REMOVED*** Status-Details
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Phase", status["phase"])
    with col2:
        st.metric("Fortschritt", f"{status['progress']}%")
    with col3:
        st.metric("Status", status["status"])
    
    ***REMOVED*** Abgeschlossene Phasen
    if "completed" in status and status["completed"]:
        st.subheader("Abgeschlossene Phasen")
        for phase in status["completed"]:
            st.success(phase)

def create_handover_section():
    """Erstellt den Bereich für das Handover-Fenster."""
    st.header("Handover")
    
    ***REMOVED*** Status laden
    status = load_pipeline_status()
    phase = status.get("phase", "none")
    
    ***REMOVED*** Handover-Inhalt laden
    handover_content = load_handover(phase)
    
    if handover_content:
        with st.expander("Handover-Informationen", expanded=True):
            st.markdown(f"***REMOVED******REMOVED*** Handover für Phase: {phase}")
            st.markdown(handover_content)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Als Markdown exportieren"):
                    ***REMOVED*** Handover als Markdown exportieren
                    st.download_button(
                        label="Download Markdown",
                        data=handover_content,
                        file_name=f"{phase}_handover.md",
                        mime="text/markdown"
                    )
            with col2:
                if st.button("Als PDF exportieren"):
                    st.info("PDF-Export-Funktionalität wird implementiert.")
    else:
        st.info(f"Kein Handover für Phase {phase} verfügbar.")

def create_prompt_generation_section():
    """Erstellt den Bereich für die Prompt-Generierung."""
    st.header("Prompt-Generierung")
    
    ***REMOVED*** Status laden
    status = load_pipeline_status()
    phase = status.get("phase", "none")
    
    ***REMOVED*** Handover-Inhalt laden
    handover_content = load_handover(phase) or ""
    
    ***REMOVED*** Tabs für verschiedene Prompt-Typen
    tab1, tab2 = st.tabs(["Standard-Prompt", "PromptSpec-Format"])
    
    with tab1:
        ***REMOVED*** Review-Änderungen
        review_changes = st.text_area("Review-Änderungen", height=100)
        
        generate_button = st.button("Prompt generieren", key="gen_standard")
        
        if generate_button:
            with st.spinner("Generiere Prompt mit ChatGPT..."):
                try:
                    ***REMOVED*** Prompt-Template erstellen
                    prompt_template = f"""
                    Basierend auf dem Handover für Phase {phase}:
                    {handover_content}
                    
                    Und diesen Review-Änderungen:
                    {review_changes}
                    
                    Generiere einen optimalen Prompt für die nächste Phase des GENXAIS-Frameworks.
                    """
                    
                    ***REMOVED*** API-Aufruf an ChatGPT
                    generated_prompt = call_chatgpt_api(prompt_template)
                    
                    if generated_prompt:
                        ***REMOVED*** Prompt anzeigen
                        st.text_area("Generierter Prompt", value=generated_prompt, height=300)
                        
                        ***REMOVED*** Prompt speichern
                        os.makedirs("data/cursor_prompts", exist_ok=True)
                        with open("data/cursor_prompts/latest_prompt.json", "w", encoding="utf-8") as file:
                            json.dump({
                                "prompt": generated_prompt,
                                "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                                "phase": phase,
                                "source": {
                                    "handover": f"data/handover/{phase.lower()}_handover.md",
                                    "review_changes": review_changes
                                },
                                "target": "cursor.ai",
                                "version": get_current_version()
                            }, file, indent=2)
                        
                        ***REMOVED*** Container für Buttons erstellen
                        button_container = st.container()
                        
                        ***REMOVED*** Buttons für Aktionen
                        col1, col2 = button_container.columns(2)
                        with col1:
                            if st.button("An cursor.ai senden", key="send_standard"):
                                ***REMOVED*** Direkt an Cursor.ai senden
                                try:
                                    pyperclip.copy(generated_prompt)
                                    st.success("Prompt in die Zwischenablage kopiert und an cursor.ai gesendet!")
                                except Exception as e:
                                    st.error(f"Fehler beim Kopieren des Prompts: {str(e)}")
                        with col2:
                            st.download_button(
                                label="Als Datei speichern",
                                data=generated_prompt,
                                file_name=f"prompt_{phase.lower()}_{time.strftime('%Y%m%d_%H%M%S')}.txt",
                                mime="text/plain"
                            )
                except Exception as e:
                    st.error(f"Fehler bei der Prompt-Generierung: {str(e)}")
    
    with tab2:
        ***REMOVED*** PromptSpec-Format
        st.subheader("PromptSpec-Format")
        
        ***REMOVED*** Ziel
        goal = st.text_area("🎯 Ziel", height=100, 
                           placeholder="Implementiere eine Funktion `summarize_transactions()` im Modul `finance_module.py`, die alle Transaktionen der letzten 30 Tage zusammenfasst.")
        
        ***REMOVED*** Kontext
        context_options = st.multiselect(
            "Kontextquellen",
            ["Handover-Dokument", "Review-Änderungen", "Benutzerdefiniert"]
        )
        
        context = ""
        review = ""
        custom_context = ""
        
        if "Handover-Dokument" in context_options and handover_content:
            context += f"Handover-Dokument:\n```\n{handover_content[:500]}...\n```\n\n"
        
        if "Review-Änderungen" in context_options:
            review = st.text_area("Review-Änderungen", height=100)
            if review:
                context += f"Review-Änderungen:\n{review}\n\n"
        
        if "Benutzerdefiniert" in context_options:
            custom_context = st.text_area("Benutzerdefinierter Kontext", height=100)
            if custom_context:
                context += f"Zusätzlicher Kontext:\n{custom_context}\n\n"
        
        ***REMOVED*** Anforderungen
        st.subheader("✅ Anforderungen")
        requirements = []
        for i in range(1, 4):  ***REMOVED*** Drei Anforderungsfelder standardmäßig
            req = st.text_input(f"Anforderung {i}")
            if req:
                requirements.append(req)
        
        ***REMOVED*** Hinweise
        st.subheader("🧠 Hinweise")
        hints = []
        for i in range(1, 3):  ***REMOVED*** Zwei Hinweisfelder standardmäßig
            hint = st.text_input(f"Hinweis {i}")
            if hint:
                hints.append(hint)
        
        ***REMOVED*** Standard-Hinweise
        hints.append("Cursor arbeitet mit OpenAI GPT-4o")
        hints.append("Kontextlänge: max. 8k Tokens")
        hints.append(f"Phase: {phase}")
        
        ***REMOVED*** Generieren-Button
        if st.button("PromptSpec generieren", key="gen_spec"):
            with st.spinner("Generiere PromptSpec..."):
                try:
                    ***REMOVED*** Markdown erstellen
                    md = []
                    
                    ***REMOVED*** Ziel
                    md.append("***REMOVED******REMOVED*** 🎯 Ziel")
                    md.append(goal)
                    md.append("")
                    
                    ***REMOVED*** Kontext
                    md.append("***REMOVED******REMOVED*** 📎 Kontext")
                    md.append(context)
                    md.append("")
                    
                    ***REMOVED*** Anforderungen
                    md.append("***REMOVED******REMOVED*** ✅ Anforderungen")
                    for req in requirements:
                        md.append(f"- {req}")
                    md.append("")
                    
                    ***REMOVED*** Hinweise
                    md.append("***REMOVED******REMOVED*** 🧠 Hinweise")
                    for hint in hints:
                        md.append(f"- {hint}")
                    md.append("")
                    
                    ***REMOVED*** Standardhinweise
                    md.append("👉 Schreibe klaren, dokumentierten Code mit Typannotation.")
                    
                    prompt_spec = "\n".join(md)
                    
                    ***REMOVED*** Prompt anzeigen
                    st.text_area("Generiertes PromptSpec", value=prompt_spec, height=300)
                    
                    ***REMOVED*** Prompt speichern
                    os.makedirs("data/cursor_prompts", exist_ok=True)
                    os.makedirs("data/cursor_prompts/specs", exist_ok=True)
                    
                    timestamp = time.strftime("%Y%m%d-%H%M%S")
                    spec_filename = f"valeo-task-{phase.lower()}-{timestamp}.md"
                    spec_path = os.path.join("data/cursor_prompts/specs", spec_filename)
                    
                    with open(spec_path, "w", encoding="utf-8") as file:
                        file.write(prompt_spec)
                    
                    with open("data/cursor_prompts/latest_prompt.json", "w", encoding="utf-8") as file:
                        json.dump({
                            "prompt": prompt_spec,
                            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                            "phase": phase,
                            "source": {
                                "handover": f"data/handover/{phase.lower()}_handover.md",
                                "review_changes": review if "Review-Änderungen" in context_options else "",
                                "custom_context": custom_context if "Benutzerdefiniert" in context_options else ""
                            },
                            "target": "cursor.ai",
                            "version": get_current_version(),
                            "prompt_spec": {
                                "goal": goal,
                                "context": context,
                                "requirements": requirements,
                                "hints": hints
                            }
                        }, file, indent=2)
                    
                    ***REMOVED*** Container für Buttons erstellen
                    action_container = st.container()
                    
                    ***REMOVED*** Buttons für Aktionen
                    col1, col2, col3 = action_container.columns(3)
                    
                    ***REMOVED*** Button 1: An cursor.ai senden
                    with col1:
                        if st.button("An cursor.ai senden", key="send_spec_btn"):
                            try:
                                ***REMOVED*** Direkt an Cursor.ai senden
                                pyperclip.copy(prompt_spec)
                                st.success("PromptSpec in die Zwischenablage kopiert und an cursor.ai gesendet!")
                            except Exception as e:
                                st.error(f"Fehler beim Senden des PromptSpec: {str(e)}")
                    
                    ***REMOVED*** Button 2: Als Markdown speichern
                    with col2:
                        st.download_button(
                            label="Als Markdown speichern",
                            data=prompt_spec,
                            file_name=spec_filename,
                            mime="text/markdown",
                            key="download_spec"
                        )
                    
                    ***REMOVED*** Button 3: Cursor Task erstellen
                    with col3:
                        if st.button("Cursor Task erstellen", key="create_task_btn"):
                            try:
                                ***REMOVED*** Cursor Task erstellen
                                cursor_task_dir = os.path.expanduser("~/cursor-tasks")
                                os.makedirs(cursor_task_dir, exist_ok=True)
                                cursor_task_file = os.path.join(cursor_task_dir, spec_filename)
                                
                                with open(cursor_task_file, "w", encoding="utf-8") as file:
                                    file.write(prompt_spec)
                                
                                st.success(f"Cursor Task erstellt: {cursor_task_file}")
                            except Exception as e:
                                st.error(f"Fehler beim Erstellen des Cursor Tasks: {str(e)}")
                except Exception as e:
                    st.error(f"Fehler bei der PromptSpec-Generierung: {str(e)}")

def create_genxais_cycle_section():
    """Erstellt den Bereich für den GENXAIS-Zyklus-Prompt-Generator."""
    st.header("🧠 GENXAIS-Zyklus Initialisierung")
    
    ***REMOVED*** Eingaben vom Nutzer
    col1, col2 = st.columns(2)
    
    with col1:
        pfad = st.text_input("📂 Projektpfad", os.path.abspath("."))
        modus = st.selectbox("⚙️ Betriebsmodus", ["Multi-Pipeline", "Single-Pipeline"], index=0)
    
    with col2:
        startphase = st.selectbox("🚀 Startphase", ["VAN", "PLAN", "CREATE", "IMPLEMENT", "REFLECT"], index=0)
        ***REMOVED*** Infoquellen Auswahl
        infoquellen = st.multiselect(
            "📡 Informationsquellen einbeziehen:",
            ["Memory Bank", "Tasks.yaml", "ToDos.md", "RAG-Server", "LangGraph", "Letztes Handover"],
            default=["Memory Bank", "Tasks.yaml", "Letztes Handover"]
        )
    
    ***REMOVED*** Button zur Generierung
    if st.button("🧾 Initialisierungsprompt erstellen"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        prompt = f"""
***REMOVED*** 🔁 GENXAIS Initialisierungsprompt für VALEO – Die NeuroERP

**📅 Zeitstempel:** {timestamp}  
**📂 Projektpfad:** `{pfad}`  
**⚙️ Modus:** {modus}  
**🚀 Startphase:** {startphase}

---

***REMOVED******REMOVED*** 📡 Eingebundene Informationsquellen:
{chr(10).join(f"- ✅ {q}" for q in infoquellen)}

---

***REMOVED******REMOVED*** 🔍 Ziel der Initialisierung:
Einleitung der neuen Runde im GENXAIS-Zyklus für die Weiterentwicklung von VALEO – Die NeuroERP.  
Konfiguration erfolgt auf Basis aktueller Datenlage aus den obigen Quellen.  

---

***REMOVED******REMOVED*** 🧠 Aufgaben:
- Automatisches Auslesen und Zusammenführen von:
  - `tasks.yaml` & `todos.md` aus dem Projektverzeichnis
  - Memory-Einträgen der vorherigen Reflexionsphase
  - Letztem `handover.md`
  - RAG-Server Antworten (Fallback-Strategie bei Lücken)
  - Aktuellen Zuständen im LangGraph-Flow

---

***REMOVED******REMOVED*** ⚙️ Startbefehl zur Initialisierung:

```bash
python -m streamlit run launch_cycle.py --phase {startphase} --pipelines 5 --load_info memory,tasks,todos
```
"""
        
        ***REMOVED*** Prompt anzeigen
        st.text_area("Generierter Initialisierungsprompt", value=prompt, height=400)
        
        ***REMOVED*** Container für Buttons erstellen
        button_container = st.container()
        
        ***REMOVED*** Buttons für Aktionen
        col1, col2, col3 = button_container.columns(3)
        
        with col1:
            if st.button("An cursor.ai senden", key="send_genxais"):
                try:
                    ***REMOVED*** Direkt an Cursor.ai senden über MCP
                    response = requests.post(
                        f"http://localhost:{MCP_PORT}/api/execute",
                        json={
                            "tool": "cursor_integration",
                            "params": {
                                "prompt": prompt,
                                "source": "valeo_neuroerp",
                                "phase": startphase,
                                "target": "cursor.ai",
                                "use_langgraph": True
                            }
                        },
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        st.success("Prompt an cursor.ai gesendet!")
                    else:
                        st.error(f"Fehler beim Senden des Prompts: {response.text}")
                except Exception as e:
                    st.error(f"Fehler beim Senden des Prompts: {str(e)}")
        
        with col2:
            ***REMOVED*** Prompt in die Zwischenablage kopieren
            if st.button("In Zwischenablage kopieren", key="copy_genxais"):
                try:
                    pyperclip.copy(prompt)
                    st.success("Prompt in die Zwischenablage kopiert!")
                except Exception as e:
                    st.error(f"Fehler beim Kopieren des Prompts: {str(e)}")
        
        with col3:
            ***REMOVED*** Prompt als Datei speichern
            st.download_button(
                label="Als Datei speichern",
                data=prompt,
                file_name=f"genxais_init_{startphase.lower()}_{time.strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown"
            )
        
        ***REMOVED*** Speichern des Prompts in der Datenbank
        try:
            os.makedirs("data/cursor_prompts/genxais", exist_ok=True)
            with open(f"data/cursor_prompts/genxais/init_{startphase.lower()}_{time.strftime('%Y%m%d_%H%M%S')}.md", "w", encoding="utf-8") as file:
                file.write(prompt)
            
            ***REMOVED*** Zusätzliche Metadaten speichern
            with open(f"data/cursor_prompts/genxais/init_{startphase.lower()}_{time.strftime('%Y%m%d_%H%M%S')}.json", "w", encoding="utf-8") as file:
                json.dump({
                    "timestamp": timestamp,
                    "phase": startphase,
                    "mode": modus,
                    "sources": infoquellen,
                    "project_path": pfad,
                    "version": get_current_version()
                }, file, indent=2)
        except Exception as e:
            st.warning(f"Fehler beim Speichern des Prompts: {str(e)}")
    
    ***REMOVED*** Erweiterte Optionen
    with st.expander("Erweiterte Optionen"):
        st.subheader("Benutzerdefinierte Vorlage")
        
        ***REMOVED*** Vorlage laden
        template_options = ["Standard", "Detailliert", "Minimal", "Benutzerdefiniert"]
        selected_template = st.selectbox("Vorlage auswählen", template_options)
        
        if selected_template == "Benutzerdefiniert":
            st.text_area("Benutzerdefinierte Vorlage", 
                         value="***REMOVED*** 🔁 GENXAIS Initialisierungsprompt\n\n**📅 Zeitstempel:** {timestamp}\n**🚀 Phase:** {phase}\n\n***REMOVED******REMOVED*** 📡 Quellen:\n{sources}\n\n***REMOVED******REMOVED*** 🔍 Ziel:\n{goal}\n\n***REMOVED******REMOVED*** 🧠 Aufgaben:\n{tasks}",
                         height=200)
        
        st.subheader("Pipeline-Konfiguration")
        
        ***REMOVED*** Anzahl der Pipelines
        num_pipelines = st.slider("Anzahl der Pipelines", 1, 10, 5)
        
        ***REMOVED*** Pipeline-Typen
        pipeline_types = st.multiselect(
            "Pipeline-Typen",
            ["Edge-Validation", "Conflict-Analysis", "Edge-Refactoring", 
             "Anomaly-Detection", "Code-Quality", "Security-Scan", 
             "Performance-Test", "Integration-Test", "Documentation"],
            default=["Edge-Validation", "Conflict-Analysis", "Edge-Refactoring"]
        )
        
        st.info(f"Konfiguriert für {num_pipelines} Pipelines vom Typ: {', '.join(pipeline_types)}")

def add_sse_client():
    """Fügt den SSE-Client zur Streamlit-App hinzu."""
    ***REMOVED*** Verwende ein div-Element mit einer ID, um es später zu aktualisieren
    st.markdown(f"""
    <div id="sse-status" style="display: none;">Nicht verbunden</div>
    <script>
    document.addEventListener('DOMContentLoaded', function() {{
        let eventSource = null;
        
        function connectSSE() {{
            if (eventSource) {{
                eventSource.close();
            }}
            
            try {{
                eventSource = new EventSource('http://localhost:{SSE_PORT}/sse');
                
                eventSource.onopen = function() {{
                    document.getElementById('sse-status').innerText = 'Verbunden';
                    document.getElementById('sse-status').style.color = 'green';
                }};
                
                eventSource.addEventListener('pipeline_status', function(event) {{
                    try {{
                        const data = JSON.parse(event.data);
                        // Aktualisiere UI-Elemente mit den neuen Daten
                        window.parent.postMessage({{
                            type: 'pipeline_status',
                            data: data
                        }}, '*');
                    }} catch (e) {{
                        console.error('Fehler beim Verarbeiten des pipeline_status-Events:', e);
                    }}
                }});
                
                eventSource.addEventListener('handover', function(event) {{
                    try {{
                        const data = JSON.parse(event.data);
                        // Zeige Handover-Fenster an
                        window.parent.postMessage({{
                            type: 'handover',
                            data: data
                        }}, '*');
                    }} catch (e) {{
                        console.error('Fehler beim Verarbeiten des handover-Events:', e);
                    }}
                }});
                
                eventSource.addEventListener('cursor_prompt', function(event) {{
                    try {{
                        const data = JSON.parse(event.data);
                        // Kopiere Prompt in die Zwischenablage
                        navigator.clipboard.writeText(data.prompt).then(() => {{
                            console.log('Prompt in die Zwischenablage kopiert');
                        }}).catch(err => {{
                            console.error('Fehler beim Kopieren des Prompts:', err);
                        }});
                    }} catch (e) {{
                        console.error('Fehler beim Verarbeiten des cursor_prompt-Events:', e);
                    }}
                }});
                
                eventSource.addEventListener('heartbeat', function(event) {{
                    // Heartbeat empfangen, nichts tun
                    document.getElementById('sse-status').innerText = 'Verbunden (letzte Aktivität: ' + new Date().toLocaleTimeString() + ')';
                }});
                
                eventSource.addEventListener('error', function(event) {{
                    console.error('SSE-Fehler:', event);
                    document.getElementById('sse-status').innerText = 'Verbindungsfehler';
                    document.getElementById('sse-status').style.color = 'red';
                    
                    // Versuche, die Verbindung wiederherzustellen
                    setTimeout(connectSSE, 5000);
                }});
            }} catch (e) {{
                console.error('Fehler beim Verbinden mit dem SSE-Server:', e);
                document.getElementById('sse-status').innerText = 'Verbindungsfehler';
                document.getElementById('sse-status').style.color = 'red';
                
                // Versuche, die Verbindung wiederherzustellen
                setTimeout(connectSSE, 5000);
            }}
        }}
        
        // Initialer Verbindungsaufbau
        connectSSE();
    }});
    </script>
    """, unsafe_allow_html=True)

def main():
    """Hauptfunktion der Streamlit-App."""
    try:
        ***REMOVED*** Header erstellen
        create_header()
        
        ***REMOVED*** Sidebar erstellen
        create_sidebar()
        
        ***REMOVED*** Tabs erstellen
        tab1, tab2, tab3, tab4 = st.tabs(["Pipeline-Status", "Handover", "Prompt-Generierung", "GENXAIS-Zyklus"])
        
        with tab1:
            create_pipeline_status_section()
        
        with tab2:
            create_handover_section()
        
        with tab3:
            create_prompt_generation_section()
        
        with tab4:
            create_genxais_cycle_section()
        
        ***REMOVED*** SSE-Client hinzufügen
        add_sse_client()
        
        ***REMOVED*** Status-Anzeige für Server
        st.sidebar.subheader("Server-Status")
        server_status_container = st.sidebar.container()
        
        try:
            ***REMOVED*** MCP-Server-Status prüfen
            response = requests.get(f"http://localhost:{MCP_PORT}/api/status", timeout=1)
            if response.status_code == 200:
                server_status_container.success("MCP-Server: Verbunden")
            else:
                server_status_container.error("MCP-Server: Fehler")
        except:
            server_status_container.warning("MCP-Server: Nicht erreichbar")
        
        try:
            ***REMOVED*** SSE-Server-Status prüfen
            response = requests.get(f"http://localhost:{SSE_PORT}/sse/status", timeout=1)
            if response.status_code == 200:
                server_status_container.success("SSE-Server: Verbunden")
            else:
                server_status_container.error("SSE-Server: Fehler")
        except:
            server_status_container.warning("SSE-Server: Nicht erreichbar")
        
        ***REMOVED*** Watchdog für Loops und Hänger
        if 'last_activity' not in st.session_state:
            st.session_state.last_activity = time.time()
        
        ***REMOVED*** Prüfen, ob eine lange Pause ohne Fortschritt vorliegt
        if time.time() - st.session_state.last_activity > 120:  ***REMOVED*** 2 Minuten
            st.warning("""
            Es wurde für längere Zeit keine Aktivität festgestellt. Mögliche Probleme:
            
            1. Große Dateien (>1500 Zeilen) können zu Editor-Problemen führen. Erwägen Sie eine Modularisierung.
            2. Komplexe Berechnungen könnten zu Verzögerungen führen.
            3. Netzwerkprobleme könnten die Kommunikation beeinträchtigen.
            
            Versuchen Sie, die Seite neu zu laden oder die Anwendung neu zu starten.
            """)
        
        ***REMOVED*** Aktivität aktualisieren
        st.session_state.last_activity = time.time()
    except Exception as e:
        st.error(f"Fehler in der Hauptfunktion: {str(e)}")
        st.info("Versuchen Sie, die Seite neu zu laden oder die Anwendung neu zu starten.")

***REMOVED*** Streamlit-App starten
if __name__ == "__main__":
    try:
        ***REMOVED*** Verzeichnisse erstellen
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        os.makedirs(os.path.dirname(PIPELINE_STATUS_PATH), exist_ok=True)
        os.makedirs(HANDOVER_PATH, exist_ok=True)
        os.makedirs("data/cursor_prompts", exist_ok=True)
        os.makedirs("data/cursor_prompts/specs", exist_ok=True)
        
        ***REMOVED*** Prüfen, ob die Konfigurationsdateien existieren
        if not os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "w", encoding="utf-8") as file:
                yaml.dump({
                    "current_version": "1.8.1",
                    "available_versions": ["1.0.0", "1.5.0", "1.8.1", "2.0.0-beta"]
                }, file)
        
        if not os.path.exists(PIPELINE_STATUS_PATH):
            with open(PIPELINE_STATUS_PATH, "w", encoding="utf-8") as file:
                json.dump({
                    "phase": "IMPLEMENT",
                    "progress": 75,
                    "status": "running",
                    "completed": ["VAN", "PLAN"],
                    "active_pipelines": [
                        "Edge-Validation-Pipeline",
                        "Conflict-Analysis-Pipeline",
                        "Edge-Refactoring-Pipeline"
                    ],
                    "last_update": time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "next_phase": "VERIFY",
                    "estimated_completion": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(time.time() + 3600))
                }, file)
        
        ***REMOVED*** MCP-Server starten
        mcp_server_thread = threading.Thread(target=mcp_server.start, daemon=True)
        mcp_server_thread.start()
        
        ***REMOVED*** Flask-Server starten
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
        
        ***REMOVED*** Streamlit-App starten (wird automatisch von Streamlit aufgerufen)
        main()
    except Exception as e:
        st.error(f"Fehler beim Starten der Anwendung: {str(e)}")
        st.info("Bitte überprüfen Sie die Konfiguration und starten Sie die Anwendung neu.") 