#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GENXAIS-Prompt-Generator für VALEO-NeuroERP

Diese Datei implementiert einen Generator für Initialisierungsprompts im GENXAIS-Zyklus.
Sie nutzt Streamlit für die Benutzeroberfläche und integriert Daten aus verschiedenen Quellen.
"""

import streamlit as st
from datetime import datetime
import os
import yaml
import json
import sys
import glob
import re
import time

# Pfade konfigurieren
CONFIG_PATH = "config/version.yaml"
PIPELINE_STATUS_PATH = "data/pipeline_status.json"
HANDOVER_PATH = "data/handover"
MEMORY_BANK_PATH = "memory-bank"
TASKS_PATH = "tasks"

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
    
    # Prompt zusammenbauen
    prompt = f"""
# 🔁 GENXAIS Initialisierungsprompt für VALEO – Die NeuroERP

**📅 Zeitstempel:** {timestamp}  
**📂 Projektpfad:** `{config['pfad']}`  
**⚙️ Modus:** {config['modus']}  
**🚀 Startphase:** {config['startphase']}

---

## 📡 Eingebundene Informationsquellen:
{info_sources}

---

## 🔍 Ziel der Initialisierung:
Einleitung der neuen Runde im GENXAIS-Zyklus für die Weiterentwicklung von VALEO – Die NeuroERP v{config['version']}.  
Konfiguration erfolgt auf Basis aktueller Datenlage aus den obigen Quellen.  

---

## 🧠 Aufgaben:
- Automatisches Auslesen und Zusammenführen von:
  - `tasks.yaml` & `todos.md` aus dem Projektverzeichnis
  - Memory-Einträgen der vorherigen Reflexionsphase
  - Letztem `handover.md`
  - RAG-Server Antworten (Fallback-Strategie bei Lücken)
  - Aktuellen Zuständen im LangGraph-Flow

---

## ⚙️ Startbefehl zur Initialisierung:

```bash
{command}
```

---

## 📊 Systemstatus:
- Aktuelle Phase: {config['current_phase']}
- Fortschritt: {config['progress']}%
- Version: {config['version']}
{additional_info}
"""
    
    return prompt

def main():
    """Hauptfunktion für die Streamlit-App."""
    # Seitenkonfiguration
    st.set_page_config(
        page_title="VALEO - GENXAIS-Zyklus",
        page_icon="🧠",
        layout="wide"
    )

    # Titel
    st.title("🧠 VALEO – Initialisierungsprompt Generator (GENXAIS-Zyklus)")

    # Version und Pipeline-Status laden
    current_version = load_version()
    pipeline_status = load_pipeline_status()
    current_phase = pipeline_status.get("phase", "VAN")
    progress = pipeline_status.get("progress", 0)

    # Sidebar für Konfiguration
    with st.sidebar:
        st.header("⚙️ Konfiguration")
        st.info(f"VALEO-NeuroERP v{current_version}")
        st.progress(progress/100, text=f"Phase: {current_phase} ({progress}%)")
        
        # Letztes Update
        last_update = pipeline_status.get("last_update", "Unbekannt")
        if last_update != "Unbekannt":
            try:
                last_update_time = datetime.fromisoformat(last_update)
                st.caption(f"Letztes Update: {last_update_time.strftime('%d.%m.%Y %H:%M')}")
            except:
                st.caption(f"Letztes Update: {last_update}")
        
        # Aktive Pipelines
        active_pipelines = pipeline_status.get("active_pipelines", [])
        if active_pipelines:
            st.subheader("Aktive Pipelines")
            for pipeline in active_pipelines:
                st.caption(f"• {pipeline}")

    # Hauptbereich
    col1, col2 = st.columns([2, 1])

    with col1:
        # Eingaben vom Nutzer
        pfad = st.text_input("📂 Projektpfad", "C:/Users/Jochen/VALEO-NeuroERP-1.01")
        modus = st.selectbox("⚙️ Betriebsmodus", ["Multi-Pipeline", "Single-Pipeline"], index=0)
        startphase = st.selectbox("🚀 Startphase", ["VAN", "PLAN", "CREATE", "IMPLEMENT", "VERIFY", "REFLECT"], index=0)

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
                rag_endpoint = st.text_input("RAG-Server Endpoint", "http://localhost:8000/query")
                rag_token = st.text_input("RAG-Server API-Token", "", type="password")

    # Konfiguration zusammenstellen
    config = {
        "pfad": pfad,
        "modus": modus,
        "startphase": startphase,
        "infoquellen": infoquellen,
        "anzahl_pipelines": anzahl_pipelines,
        "timeout": timeout,
        "debug_modus": debug_modus,
        "speichern": speichern,
        "version": current_version,
        "current_phase": current_phase,
        "progress": progress
    }
    
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

    # Fußzeile
    st.markdown("---")
    st.markdown("*VALEO-NeuroERP GENXAIS-Framework* | Entwickelt mit Streamlit und Python")

if __name__ == "__main__":
    main() 