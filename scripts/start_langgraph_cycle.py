#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GENXAIS v1.9 LangGraph Zyklus (Produktiv)
----------------------------------------
Dieses Skript startet den produktiven LangGraph-Zyklus für GENXAIS v1.9.
"""

import os
import sys
import json
import yaml
import datetime
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, TypedDict, Literal

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("output/genxais_cycle.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("GENXAIS")

# Versuche die erforderlichen Pakete zu importieren
try:
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.runnables import RunnablePassthrough
    from langgraph.graph import StateGraph, END
except ImportError as e:
    logger.error(f"Fehler beim Importieren der erforderlichen Pakete: {e}")
    logger.error("Bitte installiere die folgenden Pakete:")
    logger.error("pip install langchain-openai langgraph langchain-core langchain-community")
    sys.exit(1)

# Pfade konfigurieren
BASE_DIR = Path(__file__).resolve().parent.parent
TASKS_DIR = BASE_DIR / "tasks"
OUTPUT_DIR = BASE_DIR / "output"
MEMORY_BANK_DIR = BASE_DIR / "memory-bank"
CONFIG_DIR = BASE_DIR / "config"
CONFIG_PATH = OUTPUT_DIR / "dashboard_config.json"
PROMPTS_DIR = BASE_DIR / "prompts"

# Stellen sicher, dass die Verzeichnisse existieren
OUTPUT_DIR.mkdir(exist_ok=True)

# API-Schlüssel laden
API_KEYS_PATH = CONFIG_DIR / "api_keys.local.json"

def load_api_keys() -> Dict[str, str]:
    """
    Lädt die API-Schlüssel aus der Konfigurationsdatei.
    
    Returns:
        Dict mit den API-Schlüsseln
    """
    if not API_KEYS_PATH.exists():
        logger.error(f"API-Schlüssel-Datei nicht gefunden: {API_KEYS_PATH}")
        return {}
    
    try:
        with open(API_KEYS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Fehler beim Laden der API-Schlüssel: {str(e)}")
        return {}

def load_tasks_config() -> Dict[str, Any]:
    """
    Lädt die GENXAIS-Konfigurationsdatei.
    
    Returns:
        Dict mit der Konfiguration
    """
    config_path = TASKS_DIR / "genxais_cycle_v1.9.yaml"
    if not config_path.exists():
        logger.error(f"Konfigurationsdatei nicht gefunden: {config_path}")
        return {}
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Fehler beim Laden der Konfiguration: {str(e)}")
        return {}

def load_or_create_prompt() -> str:
    """
    Lädt den GENXAIS-Prompt oder erstellt einen neuen.
    
    Returns:
        Der Prompt als String
    """
    # Prüfe, ob der Prompt in der Umgebungsvariable vorhanden ist
    env_prompt = os.environ.get("GENXAIS_PROMPT")
    if env_prompt:
        return env_prompt
    
    # Bestimme die Version aus der Umgebungsvariable oder verwende 1.9 als Standard
    version = os.environ.get("GENXAIS_VERSION", "1.9")
    
    prompt_path = PROMPTS_DIR / f"genxais_prompt_v{version}.md"
    if prompt_path.exists():
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Fehler beim Laden des Prompts: {str(e)}")
    
    # Erstelle einen neuen Prompt
    prompt = f"""# 🚀 GENXAIS v{version} – Produktiver Entwicklungszyklus für VALEO-NeuroERP

## 📋 Projektübersicht
- **Projektverzeichnis:** {BASE_DIR}
- **Streamlit UI Port:** 8502
- **Modus:** Multi-Pipeline (7 Pipelines)
- **Startphase:** VAN
- **Letztes Handover:** `output/handover.md`

## 🔄 Aktueller Zyklus
- **Version:** {version}
- **Start:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Ziel:** Produktive Implementierung aller Pipelines

## 📊 Pipelines
1. API-Pipeline
2. Frontend-Pipeline
3. Backend-Pipeline
4. Dokumentations-Pipeline
5. Test-Pipeline
6. DevOps-Pipeline
7. Sicherheits-Pipeline

## 📝 Aufgaben
Siehe `tasks/genxais_cycle_v{version}.yaml` für detaillierte Aufgabenliste.
"""
    
    # Speichere den Prompt
    try:
        PROMPTS_DIR.mkdir(exist_ok=True)
        with open(prompt_path, "w", encoding="utf-8") as f:
            f.write(prompt)
    except Exception as e:
        logger.error(f"Fehler beim Speichern des Prompts: {str(e)}")
    
    return prompt

def save_result(phase: str, content: str) -> None:
    """
    Speichert das Ergebnis einer Phase.
    
    Args:
        phase: Der Name der Phase
        content: Der Inhalt des Ergebnisses
    """
    try:
        OUTPUT_DIR.mkdir(exist_ok=True)
        with open(OUTPUT_DIR / f"{phase.lower()}_result.md", "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"{phase}-Phase abgeschlossen. Ergebnis gespeichert unter {OUTPUT_DIR / f'{phase.lower()}_result.md'}")
    except Exception as e:
        logger.error(f"Fehler beim Speichern des Ergebnisses: {str(e)}")

def create_handover_document(results: Dict[str, str]) -> None:
    """
    Erstellt ein Handover-Dokument aus den Ergebnissen der Phasen.
    
    Args:
        results: Dict mit den Ergebnissen der Phasen
    """
    try:
        # Erstelle das Handover-Dokument
        handover = f"""# GENXAIS Zyklus Handover

## Zusammenfassung

GENXAIS Zyklus v1.9 wurde am {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} abgeschlossen.

## Durchgeführte Phasen
"""
        
        for phase in ["VAN", "PLAN", "CREATE", "IMPLEMENTATION", "REFLEKTION"]:
            if phase.lower() in results:
                handover += f"- {phase}\n"
        
        handover += f"""
## Reflektionsergebnisse

{results.get("reflektion", "Keine Reflektionsergebnisse verfügbar.")}

## Nächste Schritte
1. Überprüfung der erstellten Artefakte
2. Integration der Änderungen in das Hauptprojekt
3. Planung des nächsten GENXAIS-Zyklus (v2.0)
"""
        
        # Speichere das Handover-Dokument
        with open(OUTPUT_DIR / "handover.md", "w", encoding="utf-8") as f:
            f.write(handover)
        
        logger.info(f"Handover-Dokument erstellt: {OUTPUT_DIR / 'handover.md'}")
    except Exception as e:
        logger.error(f"Fehler beim Erstellen des Handover-Dokuments: {str(e)}")

# Typen für den State
class Phase(TypedDict):
    phase: Literal["VAN", "PLAN", "CREATE", "IMPLEMENTATION", "REFLEKTION"]
    messages: List[Dict[str, str]]
    tasks: Dict[str, Any]
    artifacts: Dict[str, Any]
    pipelines: Dict[str, Any]
    history: List[Dict[str, Any]]
    error: Optional[str]
    results: Dict[str, str]

# VAN-Phase
def van_phase(state: Phase) -> Dict[str, Any]:
    """
    Führt die VAN-Phase aus.
    
    Args:
        state: Der aktuelle Zustand
        
    Returns:
        Der aktualisierte Zustand
    """
    logger.info("Führe VAN-Phase aus...")
    
    # Lade den Prompt
    prompt_content = load_or_create_prompt()
    
    # Erstelle die Chain für die VAN-Phase
    van_prompt = ChatPromptTemplate.from_messages([
        ("system", "Du bist ein leistungsstarker KI-Agent im GENXAIS-Framework, der die VAN-Phase (Vision, Analyse, Navigation) durchführt. Deine Aufgabe ist es, den aktuellen Zustand des Projekts zu analysieren, Verbesserungspotentiale zu identifizieren und einen Plan für die nächsten Schritte zu erstellen."),
        ("human", "{prompt}")
    ])
    
    van_chain = van_prompt | llm | StrOutputParser()
    
    # Führe die Chain aus
    try:
        result = van_chain.invoke({"prompt": prompt_content})
        
        # Speichere das Ergebnis
        save_result("van", result)
        
        # Aktualisiere den Zustand
        return {
            "messages": [{"role": "assistant", "content": result}],
            "phase": "PLAN",
            "history": state["history"] + [{"phase": "VAN", "timestamp": datetime.datetime.now().isoformat()}],
            "results": {**state["results"], "van": result}
        }
    except Exception as e:
        logger.error(f"Fehler in der VAN-Phase: {str(e)}")
        return {
            "messages": state["messages"],
            "phase": "PLAN",
            "history": state["history"] + [{"phase": "VAN", "timestamp": datetime.datetime.now().isoformat(), "error": str(e)}],
            "error": str(e),
            "results": state["results"]
        }

# PLAN-Phase
def plan_phase(state: Phase) -> Dict[str, Any]:
    """
    Führt die PLAN-Phase aus.
    
    Args:
        state: Der aktuelle Zustand
        
    Returns:
        Der aktualisierte Zustand
    """
    logger.info("Führe PLAN-Phase aus...")
    
    # Extrahiere die Nachrichten aus dem Zustand
    messages = state["messages"]
    
    # Erstelle die Chain für die PLAN-Phase
    plan_prompt = ChatPromptTemplate.from_messages([
        ("system", "Du bist ein leistungsstarker KI-Agent im GENXAIS-Framework, der die PLAN-Phase durchführt. Deine Aufgabe ist es, basierend auf der Analyse aus der VAN-Phase einen detaillierten Plan für die Implementierung zu erstellen. Berücksichtige dabei die identifizierten Verbesserungspotentiale und priorisiere die Aufgaben."),
        ("human", "Hier ist die Analyse aus der VAN-Phase:\n\n{van_result}\n\nErstelle einen detaillierten Plan für die Implementierung der identifizierten Verbesserungspotentiale.")
    ])
    
    plan_chain = plan_prompt | llm | StrOutputParser()
    
    # Führe die Chain aus
    try:
        result = plan_chain.invoke({"van_result": messages[0]["content"]})
        
        # Speichere das Ergebnis
        save_result("plan", result)
        
        # Aktualisiere den Zustand
        return {
            "messages": state["messages"] + [{"role": "assistant", "content": result}],
            "phase": "CREATE",
            "history": state["history"] + [{"phase": "PLAN", "timestamp": datetime.datetime.now().isoformat()}],
            "results": {**state["results"], "plan": result}
        }
    except Exception as e:
        logger.error(f"Fehler in der PLAN-Phase: {str(e)}")
        return {
            "messages": state["messages"],
            "phase": "CREATE",
            "history": state["history"] + [{"phase": "PLAN", "timestamp": datetime.datetime.now().isoformat(), "error": str(e)}],
            "error": str(e),
            "results": state["results"]
        }

# CREATE-Phase
def create_phase(state: Phase) -> Dict[str, Any]:
    """
    Führt die CREATE-Phase aus.
    
    Args:
        state: Der aktuelle Zustand
        
    Returns:
        Der aktualisierte Zustand
    """
    logger.info("Führe CREATE-Phase aus...")
    
    # Extrahiere die Nachrichten aus dem Zustand
    messages = state["messages"]
    
    # Erstelle die Chain für die CREATE-Phase
    create_prompt = ChatPromptTemplate.from_messages([
        ("system", "Du bist ein leistungsstarker KI-Agent im GENXAIS-Framework, der die CREATE-Phase durchführt. Deine Aufgabe ist es, basierend auf dem Plan aus der PLAN-Phase konkrete Implementierungen zu entwickeln. Erstelle Prototypen, entwickle neue Funktionen und implementiere neue Technologien."),
        ("human", "Hier ist der Plan aus der PLAN-Phase:\n\n{plan_result}\n\nEntwickle konkrete Implementierungen für die geplanten Funktionen.")
    ])
    
    create_chain = create_prompt | llm | StrOutputParser()
    
    # Führe die Chain aus
    try:
        result = create_chain.invoke({"plan_result": messages[1]["content"]})
        
        # Speichere das Ergebnis
        save_result("create", result)
        
        # Aktualisiere den Zustand
        return {
            "messages": state["messages"] + [{"role": "assistant", "content": result}],
            "phase": "IMPLEMENTATION",
            "history": state["history"] + [{"phase": "CREATE", "timestamp": datetime.datetime.now().isoformat()}],
            "results": {**state["results"], "create": result}
        }
    except Exception as e:
        logger.error(f"Fehler in der CREATE-Phase: {str(e)}")
        return {
            "messages": state["messages"],
            "phase": "IMPLEMENTATION",
            "history": state["history"] + [{"phase": "CREATE", "timestamp": datetime.datetime.now().isoformat(), "error": str(e)}],
            "error": str(e),
            "results": state["results"]
        }

# IMPLEMENTATION-Phase
def implementation_phase(state: Phase) -> Dict[str, Any]:
    """
    Führt die IMPLEMENTATION-Phase aus.
    
    Args:
        state: Der aktuelle Zustand
        
    Returns:
        Der aktualisierte Zustand
    """
    logger.info("Führe IMPLEMENTATION-Phase aus...")
    
    # Extrahiere die Nachrichten aus dem Zustand
    messages = state["messages"]
    
    # Erstelle die Chain für die IMPLEMENTATION-Phase
    implementation_prompt = ChatPromptTemplate.from_messages([
        ("system", "Du bist ein leistungsstarker KI-Agent im GENXAIS-Framework, der die IMPLEMENTATION-Phase durchführt. Deine Aufgabe ist es, die entwickelten Funktionen vollständig zu implementieren, in das bestehende System zu integrieren und Tests durchzuführen."),
        ("human", "Hier sind die entwickelten Funktionen aus der CREATE-Phase:\n\n{create_result}\n\nImplementiere diese Funktionen vollständig und integriere sie in das bestehende System.")
    ])
    
    implementation_chain = implementation_prompt | llm | StrOutputParser()
    
    # Führe die Chain aus
    try:
        result = implementation_chain.invoke({"create_result": messages[2]["content"]})
        
        # Speichere das Ergebnis
        save_result("implementation", result)
        
        # Aktualisiere den Zustand
        return {
            "messages": state["messages"] + [{"role": "assistant", "content": result}],
            "phase": "REFLEKTION",
            "history": state["history"] + [{"phase": "IMPLEMENTATION", "timestamp": datetime.datetime.now().isoformat()}],
            "results": {**state["results"], "implementation": result}
        }
    except Exception as e:
        logger.error(f"Fehler in der IMPLEMENTATION-Phase: {str(e)}")
        return {
            "messages": state["messages"],
            "phase": "REFLEKTION",
            "history": state["history"] + [{"phase": "IMPLEMENTATION", "timestamp": datetime.datetime.now().isoformat(), "error": str(e)}],
            "error": str(e),
            "results": state["results"]
        }

# REFLEKTION-Phase
def reflektion_phase(state: Phase) -> Dict[str, Any]:
    """
    Führt die REFLEKTION-Phase aus.
    
    Args:
        state: Der aktuelle Zustand
        
    Returns:
        Der aktualisierte Zustand
    """
    logger.info("Führe REFLEKTION-Phase aus...")
    
    # Extrahiere die Nachrichten aus dem Zustand
    messages = state["messages"]
    
    # Erstelle die Chain für die REFLEKTION-Phase
    reflektion_prompt = ChatPromptTemplate.from_messages([
        ("system", "Du bist ein leistungsstarker KI-Agent im GENXAIS-Framework, der die REFLEKTION-Phase durchführt. Deine Aufgabe ist es, den Projekterfolg zu bewerten, Verbesserungspotentiale zu identifizieren und den nächsten Zyklus zu planen."),
        ("human", "Hier ist die Implementierung aus der IMPLEMENTATION-Phase:\n\n{implementation_result}\n\nBewerte den Projekterfolg, identifiziere Verbesserungspotentiale und plane den nächsten Zyklus.")
    ])
    
    reflektion_chain = reflektion_prompt | llm | StrOutputParser()
    
    # Führe die Chain aus
    try:
        result = reflektion_chain.invoke({"implementation_result": messages[3]["content"]})
        
        # Speichere das Ergebnis
        save_result("reflektion", result)
        
        # Aktualisiere den Zustand
        updated_results = {**state["results"], "reflektion": result}
        
        # Erstelle das Handover-Dokument
        create_handover_document(updated_results)
        
        return {
            "messages": state["messages"] + [{"role": "assistant", "content": result}],
            "phase": "COMPLETE",
            "history": state["history"] + [{"phase": "REFLEKTION", "timestamp": datetime.datetime.now().isoformat()}],
            "results": updated_results
        }
    except Exception as e:
        logger.error(f"Fehler in der REFLEKTION-Phase: {str(e)}")
        return {
            "messages": state["messages"],
            "phase": "COMPLETE",
            "history": state["history"] + [{"phase": "REFLEKTION", "timestamp": datetime.datetime.now().isoformat(), "error": str(e)}],
            "error": str(e),
            "results": state["results"]
        }

# Router für die Phasen
def router(state: Phase) -> str:
    """
    Routet den Zustand zur nächsten Phase.
    
    Args:
        state: Der aktuelle Zustand
        
    Returns:
        Die nächste Phase
    """
    phase = state["phase"]
    
    if phase == "VAN":
        return "van"
    elif phase == "PLAN":
        return "plan"
    elif phase == "CREATE":
        return "create"
    elif phase == "IMPLEMENTATION":
        return "implementation"
    elif phase == "REFLEKTION":
        return "reflektion"
    else:
        return END

def main() -> None:
    """
    Hauptfunktion zum Starten des LangGraph-Zyklus.
    """
    print("=" * 80)
    print("GENXAIS v1.9 LangGraph Zyklus (Produktiv)")
    print("=" * 80)
    print(f"Startzeit: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Projektverzeichnis: {BASE_DIR}")
    print("-" * 80)
    
    # API-Schlüssel laden und in Umgebungsvariablen setzen
    api_keys = load_api_keys()
    if "openai" in api_keys:
        os.environ["OPENAI_API_KEY"] = api_keys["openai"]
    else:
        logger.error("Kein OpenAI API-Schlüssel gefunden.")
        sys.exit(1)
    
    # LLM initialisieren
    global llm
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.2
    )
    
    # Erstelle den Graphen
    logger.info("Starte LangGraph-Zyklus...")
    
    try:
        # Definiere den Workflow
        workflow = StateGraph(Phase)
        
        # Füge die Knoten hinzu
        workflow.add_node("van", van_phase)
        workflow.add_node("plan", plan_phase)
        workflow.add_node("create", create_phase)
        workflow.add_node("implementation", implementation_phase)
        workflow.add_node("reflektion", reflektion_phase)
        
        # Definiere den Startknoten und die Kanten
        workflow.set_entry_point("van")
        workflow.add_edge("van", "plan")
        workflow.add_edge("plan", "create")
        workflow.add_edge("create", "implementation")
        workflow.add_edge("implementation", "reflektion")
        workflow.add_edge("reflektion", END)
        
        # Kompiliere den Graphen
        app = workflow.compile()
        
        # Führe den Graphen aus
        for event in app.stream({
            "phase": "VAN",
            "messages": [],
            "tasks": {},
            "artifacts": {},
            "pipelines": {},
            "history": [],
            "error": None,
            "results": {}
        }):
            # Hier könnten wir den Fortschritt anzeigen
            pass
    except Exception as e:
        logger.error(f"Fehler beim Ausführen des LangGraph-Zyklus: {str(e)}")
    
    print("-" * 80)
    print(f"Endzeit: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

if __name__ == "__main__":
    main() 