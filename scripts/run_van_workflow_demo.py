"""
Einfaches Demo-Skript zum Ausführen des VAN-Modus über den APMWorkflow.

Nutzt:
- backend.apm_framework.APMWorkflow
- backend.apm_framework.RAGService (optional)
- backend.apm_framework.LLMService (optional)

Konfiguration via Umgebungsvariablen (optional):
- MONGODB_URI (Standard: mongodb://localhost:27017/)
- MONGODB_DB (Standard: valeo_neuroerp)
- APM_PROJECT_ID (Standard: demo-project-van)
- LLM_PROVIDER (Standard: ollama, Optionen: openai, claude, deepseek, ollama, mock)
- OLLAMA_MODEL (Standard: llama3.2:3b)
"""

import os
import sys
import json
import asyncio
import logging
from typing import Dict, Any
from pathlib import Path

# Lokales Repo-Verzeichnis priorisieren
repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root))

from backend.apm_framework.mongodb_connector import APMMongoDBConnector
from backend.apm_framework.apm_workflow import APMWorkflow
from backend.apm_framework.rag_service import RAGService
from backend.apm_framework.llm_service import create_llm_service


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("run_van_workflow_demo")


def load_demo_requirement() -> str:
    """Lädt eine Demobeschreibung der Anforderung, falls vorhanden, sonst Default-Text."""
    config_path = os.path.join("config", "van_mode_demo.json")
    try:
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                cfg: Dict[str, Any] = json.load(f)
                req = cfg.get("requirement_text")
                if isinstance(req, str) and req.strip():
                    return req.strip()
    except Exception as e:
        logger.warning("Konnte Demo-Konfiguration nicht laden: %s", e)
    # Fallback
    return (
        "Als Disponent möchte ich eingehende Bestellungen automatisch prüfen, "
        "validieren und bei Unklarheiten Rückfragen generieren, damit der "
        "Auftragsdurchlauf ohne manuelle Verzögerungen funktioniert."
    )


async def main() -> None:
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    mongodb_db = os.getenv("MONGODB_DB", "valeo_neuroerp")
    project_id = os.getenv("APM_PROJECT_ID", "demo-project-van")
    llm_provider = os.getenv("LLM_PROVIDER", "ollama")  # Ollama als Standard
    ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

    logger.info("Starte VAN-Workflow-Demo (DB=%s, Projekt=%s, LLM=%s, Modell=%s)", 
                mongodb_db, project_id, llm_provider, ollama_model)

    # Connector und Workflow initialisieren
    connector = APMMongoDBConnector(mongodb_uri, mongodb_db)
    workflow = APMWorkflow(connector, project_id)

    # Optional: RAG-Service setzen (nutzt dieselbe DB)
    try:
        rag_service = RAGService(connector, project_id)
        workflow.set_rag_service(rag_service)
        logger.info("RAG-Service gesetzt")
    except Exception as e:
        logger.warning("RAG-Service konnte nicht initialisiert werden: %s", e)

    # Optional: LLM-Service setzen
    try:
        llm_service = create_llm_service(llm_provider)
        # LLM-Service direkt an VAN-Modus setzen
        workflow.van_mode.set_llm_provider(llm_provider)
        logger.info("LLM-Service mit Provider %s gesetzt", llm_provider)
        
        # Zusätzliche Info für Ollama
        if llm_provider == "ollama":
            logger.info("Ollama-Modell: %s", ollama_model)
            logger.info("Ollama-URL: %s", os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))
            
    except Exception as e:
        logger.warning("LLM-Service konnte nicht initialisiert werden: %s", e)

    # Beispielanforderung laden
    requirement_text = load_demo_requirement()

    # VAN-Modus ausführen
    result = await workflow.run_van(requirement_text)

    # Ausgabe
    print("\n=== VAN-Demo Ergebnis ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # Zusätzliche Informationen
    print(f"\n=== Zusätzliche Informationen ===")
    print(f"LLM-Provider: {result.get('llm_provider', 'unbekannt')}")
    print(f"RAG-Service: {result.get('rag_service', 'unbekannt')}")
    print(f"Klärungsfragen generiert: {len(result.get('clarifications', []))}")
    print(f"Ähnliche Anforderungen gefunden: {len(result.get('similar_requirements', []))}")
    
    # Ollama-spezifische Informationen
    if llm_provider == "ollama":
        print(f"\n=== Ollama-Informationen ===")
        print(f"Verwendetes Modell: {ollama_model}")
        print(f"Ollama-URL: {os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')}")
        print(f"💡 Tipp: Testen Sie verschiedene Modelle mit OLLAMA_MODEL=mistral:7b")


if __name__ == "__main__":
    asyncio.run(main())


