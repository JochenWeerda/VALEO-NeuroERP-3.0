#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Einfache Version des GENXAIS-Prompt-Generators für VALEO-NeuroERP

Diese Datei implementiert einen einfachen Generator für Initialisierungsprompts im GENXAIS-Zyklus.
"""

import streamlit as st
from datetime import datetime
import os
import requests

def check_mcp_status():
    """Prüft, ob der MCP-Server läuft."""
    # Liste der möglichen Ports für den MCP-Server
    ports = [8000, 5000, 3000]
    
    for port in ports:
        try:
            response = requests.get(f"http://localhost:{port}/api/status", timeout=0.5)
            if response.status_code == 200:
                return True, port
        except:
            continue
    
    # Prüfe, ob der MCP-Prozess läuft, auch wenn die API nicht erreichbar ist
    try:
        import psutil
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                # Sicherstellen, dass cmdline nicht None ist
                cmdline = proc.info.get('cmdline', [])
                if cmdline and any('mcp_server' in cmd.lower() for cmd in cmdline if cmd):
                    return True, None
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    except ImportError:
        # psutil nicht installiert, ignorieren
        pass
    
    return False, None

def send_prompt_to_mcp(prompt, api_key=None):
    """Sendet einen Prompt an den MCP-Server."""
    # Liste der möglichen Ports für den MCP-Server
    ports = [8000, 5000, 3000]
    
    # API-Key aus Umgebungsvariablen laden, falls nicht übergeben
    if api_key is None:
        api_key = os.environ.get("LINKUP_API_KEY", "")
    
    # Header für die Anfrage vorbereiten
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    for port in ports:
        try:
            response = requests.post(
                f"http://localhost:{port}/api/prompt",
                json={"prompt": prompt, "api_key": api_key},
                headers=headers,
                timeout=2
            )
            if response.status_code == 200:
                return True, f"Prompt erfolgreich an MCP gesendet (Port: {port})!"
            elif response.status_code == 401:
                return False, "API-Key ungültig oder nicht angegeben."
        except:
            continue
    
    return False, "MCP-Server nicht erreichbar. Bitte starte den MCP-Server und versuche es erneut."

def main():
    # Titel
    st.title(" VALEO  Initialisierungsprompt Generator (GENXAIS-Zyklus)")
    
    # Eingaben vom Nutzer
    pfad = st.text_input(" Projektpfad", os.path.abspath("."))
    modus = st.selectbox(" Betriebsmodus", ["Multi-Pipeline", "Single-Pipeline"], index=0)
    startphase = st.selectbox(" Startphase", ["VAN", "PLAN", "CREATE", "IMPLEMENT", "REFLECT"], index=0)
    
    # Infoquellen Auswahl
    infoquellen = st.multiselect(
        " Informationsquellen einbeziehen:",
        ["Memory Bank", "Tasks.yaml", "ToDos.md", "RAG-Server", "LangGraph", "Letztes Handover"],
        default=["Memory Bank", "Tasks.yaml", "Letztes Handover"]
    )
    
    # API-Key Eingabe (optional)
    with st.expander("API-Key Konfiguration"):
        api_key = st.text_input("LinkUp API-Key", 
                               value=os.environ.get("LINKUP_API_KEY", ""), 
                               type="password")
        if st.button("API-Key speichern"):
            os.environ["LINKUP_API_KEY"] = api_key
            st.success("API-Key gespeichert!")
    
    # MCP-Status anzeigen
    try:
        mcp_running, port = check_mcp_status()
        if mcp_running:
            st.success(f"MCP-Server: Verbunden {f'(Port: {port})' if port else ''}")
        else:
            st.warning("MCP-Server: Nicht erreichbar. Prompts können nicht direkt gesendet werden.")
    except Exception as e:
        st.error(f"Fehler bei der MCP-Server-Prüfung: {str(e)}")
        mcp_running = False
    
    # Button zur Generierung
    if st.button(" Initialisierungsprompt erstellen"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        prompt = f"""
#  GENXAIS Initialisierungsprompt für VALEO  Die NeuroERP

** Zeitstempel:** {timestamp}  
** Projektpfad:** `{pfad}`  
** Modus:** {modus}  
** Startphase:** {startphase}

---

##  Eingebundene Informationsquellen:
{chr(10).join(f"-  {q}" for q in infoquellen)}

---

##  Ziel der Initialisierung:
Einleitung der neuen Runde im GENXAIS-Zyklus für die Weiterentwicklung von VALEO  Die NeuroERP.  
Konfiguration erfolgt auf Basis aktueller Datenlage aus den obigen Quellen.  

---

##  Aufgaben:
- Automatisches Auslesen und Zusammenführen von:
  - `tasks.yaml` & `todos.md` aus dem Projektverzeichnis
  - Memory-Einträgen der vorherigen Reflexionsphase
  - Letztem `handover.md`
  - RAG-Server Antworten (Fallback-Strategie bei Lücken)
  - Aktuellen Zuständen im LangGraph-Flow

---

##  Startbefehl zur Initialisierung:

```bash
python -m streamlit run launch_cycle.py --phase {startphase} --pipelines 5 --load_info memory,tasks,todos
```
"""
        
        # Prompt anzeigen
        st.text_area("Generierter Initialisierungsprompt", value=prompt, height=400)
        
        # Container für Buttons erstellen
        button_container = st.container()
        
        # Buttons für Aktionen
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("An cursor.ai senden"):
                if mcp_running:
                    success, message = send_prompt_to_mcp(prompt, api_key)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                else:
                    try:
                        # Direkt an Cursor.ai senden (Zwischenablage)
                        import pyperclip
                        pyperclip.copy(prompt)
                        st.success("MCP nicht erreichbar. Prompt in die Zwischenablage kopiert! Bitte in cursor.ai einfügen.")
                    except Exception as e:
                        st.error(f"Fehler beim Kopieren des Prompts: {str(e)}")
        
        with col2:
            # Prompt in die Zwischenablage kopieren
            if st.button("In Zwischenablage kopieren"):
                try:
                    import pyperclip
                    pyperclip.copy(prompt)
                    st.success("Prompt in die Zwischenablage kopiert!")
                except Exception as e:
                    st.error(f"Fehler beim Kopieren des Prompts: {str(e)}")
        
        with col3:
            # Prompt als Datei speichern
            st.download_button(
                label="Als Datei speichern",
                data=prompt,
                file_name=f"genxais_init_{startphase.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown"
            )
        
        # Speichern des Prompts lokal
        try:
            os.makedirs("data/cursor_prompts/genxais", exist_ok=True)
            timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            with open(f"data/cursor_prompts/genxais/init_{startphase.lower()}_{timestamp_str}.md", "w", encoding="utf-8") as file:
                file.write(prompt)
            st.success("Prompt wurde lokal gespeichert.")
        except Exception as e:
            st.warning(f"Fehler beim Speichern des Prompts: {str(e)}")

if __name__ == "__main__":
    main()

