***REMOVED***!/usr/bin/env python3
***REMOVED*** -*- coding: utf-8 -*-

"""
Cursor.ai Prompt Integration für VALEO-NeuroERP

Dieses Skript ermöglicht die direkte Integration von generierten Prompts
mit der Cursor.ai IDE über MCP und Langgraph.
"""

import os
import sys
import json
import time
import yaml
import requests
import pyperclip
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

***REMOVED*** Konfiguration
PROMPT_FILE = "data/cursor_prompts/latest_prompt.json"
PROMPT_SPEC_DIR = "data/cursor_prompts/specs"
MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "http://localhost:8000")
LANGGRAPH_URL = os.environ.get("LANGGRAPH_URL", "http://localhost:7010")
MCP_API_KEY = os.environ.get("MCP_API_KEY")
CURSOR_TASK_DIR = os.path.expanduser("~/cursor-tasks")

class PromptSpec:
    """Standardisiertes Format für Cursor.ai-Prompts."""
    
    def __init__(self, goal="", context="", requirements=None, hints=None):
        self.goal = goal
        self.context = context
        self.requirements = requirements or []
        self.hints = hints or []
    
    @classmethod
    def from_json(cls, data):
        """Erstellt ein PromptSpec aus JSON-Daten."""
        if isinstance(data, str):
            ***REMOVED*** Falls ein String übergeben wird, behandle es als Raw-Prompt
            return cls(goal=data)
        
        return cls(
            goal=data.get("goal", ""),
            context=data.get("context", ""),
            requirements=data.get("requirements", []),
            hints=data.get("hints", [])
        )
    
    def to_markdown(self):
        """Konvertiert das PromptSpec in Markdown."""
        md = []
        
        ***REMOVED*** Ziel
        md.append("***REMOVED******REMOVED*** 🎯 Ziel")
        md.append(self.goal)
        md.append("")
        
        ***REMOVED*** Kontext
        md.append("***REMOVED******REMOVED*** 📎 Kontext")
        md.append(self.context)
        md.append("")
        
        ***REMOVED*** Anforderungen
        md.append("***REMOVED******REMOVED*** ✅ Anforderungen")
        for req in self.requirements:
            md.append(f"- {req}")
        md.append("")
        
        ***REMOVED*** Hinweise
        md.append("***REMOVED******REMOVED*** 🧠 Hinweise")
        for hint in self.hints:
            md.append(f"- {hint}")
        md.append("")
        
        ***REMOVED*** Standardhinweise
        md.append("👉 Schreibe klaren, dokumentierten Code mit Typannotation.")
        
        return "\n".join(md)
    
    def save_to_file(self, filename):
        """Speichert das PromptSpec in einer Markdown-Datei."""
        with open(filename, "w", encoding="utf-8") as f:
            f.write(self.to_markdown())

class PromptFileHandler(FileSystemEventHandler):
    """Handler für Änderungen an der Prompt-Datei."""
    
    def on_modified(self, event):
        if event.src_path.endswith(PROMPT_FILE):
            self.process_prompt_file()
    
    def process_prompt_file(self):
        """Verarbeitet die Prompt-Datei und sendet den Prompt an Cursor.ai über MCP."""
        try:
            ***REMOVED*** Warten, um sicherzustellen, dass die Datei vollständig geschrieben wurde
            time.sleep(0.5)
            
            ***REMOVED*** Prompt aus Datei lesen
            with open(PROMPT_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
                prompt = data.get("prompt", "")
            
            if not prompt:
                print("Kein Prompt in der Datei gefunden.")
                return
            
            ***REMOVED*** Prompt in die Zwischenablage kopieren (als Fallback)
            pyperclip.copy(prompt)
            print(f"Prompt in die Zwischenablage kopiert: {prompt[:50]}...")
            
            ***REMOVED*** Prompt in standardisiertes Format konvertieren
            spec = self.convert_to_prompt_spec(prompt, data)
            
            ***REMOVED*** Prompt als Cursor Task speichern
            task_file = self.save_as_cursor_task(spec, data)
            
            ***REMOVED*** Versuche, den Prompt über MCP an Cursor.ai zu senden
            self.send_to_mcp(prompt, data, spec, task_file)
            
        except Exception as e:
            print(f"Fehler beim Verarbeiten des Prompts: {str(e)}")
    
    def convert_to_prompt_spec(self, prompt, data):
        """Konvertiert einen Prompt in das standardisierte PromptSpec-Format."""
        ***REMOVED*** Versuche, aus dem Prompt strukturierte Informationen zu extrahieren
        goal = prompt.split("\n")[0] if prompt else ""
        
        ***REMOVED*** Kontext aus den Quelldaten extrahieren
        context = ""
        source = data.get("source", {})
        if source:
            handover = source.get("handover", "")
            if handover and os.path.exists(handover):
                with open(handover, "r", encoding="utf-8") as f:
                    context += f"Handover-Dokument:\n```\n{f.read()[:500]}...\n```\n\n"
            
            review_changes = source.get("review_changes", "")
            if review_changes:
                context += f"Review-Änderungen:\n{review_changes}\n\n"
        
        ***REMOVED*** Anforderungen und Hinweise
        requirements = ["Implementierung gemäß VALEO-NeuroERP Standards"]
        hints = [
            "Cursor arbeitet mit OpenAI GPT-4o",
            "Kontextlänge: max. 8k Tokens",
            f"Phase: {data.get('phase', 'unbekannt')}"
        ]
        
        return PromptSpec(goal=goal, context=context, requirements=requirements, hints=hints)
    
    def save_as_cursor_task(self, spec, data):
        """Speichert den Prompt als Cursor Task."""
        ***REMOVED*** Sicherstellen, dass das Verzeichnis existiert
        os.makedirs(CURSOR_TASK_DIR, exist_ok=True)
        os.makedirs(PROMPT_SPEC_DIR, exist_ok=True)
        
        ***REMOVED*** Dateinamen generieren
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        phase = data.get("phase", "unknown").lower()
        task_name = f"valeo-task-{phase}-{timestamp}"
        
        ***REMOVED*** Speicherpfade
        spec_file = os.path.join(PROMPT_SPEC_DIR, f"{task_name}.md")
        cursor_task_file = os.path.join(CURSOR_TASK_DIR, f"{task_name}.md")
        
        ***REMOVED*** PromptSpec speichern
        spec.save_to_file(spec_file)
        spec.save_to_file(cursor_task_file)
        
        print(f"Prompt als Cursor Task gespeichert: {cursor_task_file}")
        return cursor_task_file
    
    def send_to_mcp(self, prompt, data, spec, task_file):
        """Sendet den Prompt über MCP an Cursor.ai."""
        try:
            ***REMOVED*** MCP-Anfrage vorbereiten
            headers = {
                "Content-Type": "application/json"
            }
            
            if MCP_API_KEY:
                headers["Authorization"] = f"Bearer {MCP_API_KEY}"
            
            ***REMOVED*** Vereinfachte Payload für den /api/prompt-Endpunkt
            payload = {
                "prompt": spec.to_markdown()
            }
            
            ***REMOVED*** Anfrage an MCP senden
            response = requests.post(
                f"{MCP_SERVER_URL}/api/prompt",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                print("Prompt erfolgreich über MCP an Cursor.ai gesendet!")
                
                ***REMOVED*** Optional: Langgraph-Integration für Workflow-Steuerung
                self.trigger_langgraph_workflow(prompt, data, spec)
            else:
                print(f"Fehler beim Senden des Prompts über MCP: {response.status_code}")
                print(f"Antwort: {response.text}")
                
                ***REMOVED*** Fallback: Öffne Cursor.ai direkt und füge den Prompt ein
                self.open_cursor_with_prompt(task_file)
        
        except Exception as e:
            print(f"Fehler bei der MCP-Anfrage: {str(e)}")
            ***REMOVED*** Fallback: Öffne Cursor.ai direkt
            self.open_cursor_with_prompt(task_file)
    
    def trigger_langgraph_workflow(self, prompt, data, spec):
        """Startet einen Langgraph-Workflow für die Prompt-Verarbeitung."""
        try:
            if not LANGGRAPH_URL:
                return
                
            ***REMOVED*** Langgraph-Anfrage vorbereiten
            headers = {
                "Content-Type": "application/json"
            }
            
            ***REMOVED*** Workflow-Payload
            payload = {
                "workflow": "cursor_prompt_workflow",
                "inputs": {
                    "prompt": spec.to_markdown(),
                    "phase": data.get("phase", ""),
                    "source": data.get("source", {}),
                    "version": data.get("version", ""),
                    "goal": spec.goal,
                    "context": spec.context,
                    "requirements": spec.requirements
                }
            }
            
            ***REMOVED*** Anfrage an Langgraph senden
            response = requests.post(
                f"{LANGGRAPH_URL}/api/workflows/execute",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                print("Langgraph-Workflow erfolgreich gestartet!")
            else:
                print(f"Fehler beim Starten des Langgraph-Workflows: {response.status_code}")
        
        except Exception as e:
            print(f"Fehler bei der Langgraph-Integration: {str(e)}")
    
    def open_cursor_with_prompt(self, task_file):
        """Öffnet Cursor.ai und fügt den Prompt ein (Fallback)."""
        try:
            ***REMOVED*** Prüfen, ob Cursor.ai installiert ist
            cursor_path = "C:\\Program Files\\Cursor\\Cursor.exe"
            if os.path.exists(cursor_path):
                ***REMOVED*** Starte Cursor.ai mit dem Task-File
                subprocess.Popen([cursor_path, task_file])
                print(f"Cursor.ai geöffnet mit Task: {task_file}")
            else:
                print(f"Cursor.ai konnte nicht gefunden werden. Task wurde gespeichert unter: {task_file}")
        except Exception as e:
            print(f"Fehler beim Öffnen von Cursor.ai: {str(e)}")

def ensure_prompt_directory():
    """Stellt sicher, dass das Prompt-Verzeichnis existiert."""
    os.makedirs(os.path.dirname(PROMPT_FILE), exist_ok=True)
    os.makedirs(PROMPT_SPEC_DIR, exist_ok=True)
    os.makedirs(CURSOR_TASK_DIR, exist_ok=True)
    
    ***REMOVED*** Erstelle eine leere Prompt-Datei, falls sie nicht existiert
    if not os.path.exists(PROMPT_FILE):
        with open(PROMPT_FILE, "w", encoding="utf-8") as file:
            json.dump({"prompt": ""}, file)

def create_example_prompt_spec():
    """Erstellt ein Beispiel-PromptSpec."""
    example = PromptSpec(
        goal="Implementiere eine Funktion `summarize_transactions()` im Modul `finance_module.py`, die alle Transaktionen der letzten 30 Tage zusammenfasst.",
        context="- Alle Daten liegen im DataFrame `df_transactions`\n- Verwende die Spalten: `amount`, `category`, `date`",
        requirements=[
            "Gruppierung nach Kategorie",
            "Gesamtsumme",
            "Ausgabe als JSON"
        ],
        hints=[
            "Cursor arbeitet mit OpenAI GPT-4o (BYO-API)",
            "Kontextlänge: max. 8k Tokens"
        ]
    )
    
    example_file = os.path.join(PROMPT_SPEC_DIR, "example_prompt_spec.md")
    example.save_to_file(example_file)
    print(f"Beispiel-PromptSpec erstellt: {example_file}")

def start_watching():
    """Startet die Überwachung der Prompt-Datei."""
    ensure_prompt_directory()
    create_example_prompt_spec()
    
    event_handler = PromptFileHandler()
    observer = Observer()
    observer.schedule(event_handler, os.path.dirname(PROMPT_FILE), recursive=False)
    observer.start()
    
    print(f"Überwache Änderungen an {PROMPT_FILE}...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    
    observer.join()

if __name__ == "__main__":
    print("Cursor.ai Prompt Integration über MCP gestartet")
    
    ***REMOVED*** MCP-Verbindung prüfen
    try:
        response = requests.get(f"{MCP_SERVER_URL}/api/status")
        if response.status_code == 200:
            print(f"MCP-Server verbunden: {MCP_SERVER_URL}")
        else:
            print(f"MCP-Server nicht erreichbar: {MCP_SERVER_URL}")
    except:
        print(f"MCP-Server nicht erreichbar: {MCP_SERVER_URL}")
    
    ***REMOVED*** Starte die Überwachung
    start_watching() 