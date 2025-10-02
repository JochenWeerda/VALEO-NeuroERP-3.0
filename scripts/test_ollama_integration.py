"""
Test-Skript für die Ollama-Integration im VAN-Modus.
Testet die Verbindung zu lokalen LLMs über Ollama.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

***REMOVED*** Lokales Repo-Verzeichnis priorisieren
repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root))

from backend.apm_framework.llm_service import LLMService, LLMProvider

***REMOVED*** Logging konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_ollama_connection():
    """Testet die Verbindung zu Ollama."""
    try:
        ***REMOVED*** Ollama-Service initialisieren
        llm_service = LLMService(LLMProvider.OLLAMA)
        logger.info("Ollama-Service initialisiert")
        
        ***REMOVED*** Verfügbare Modelle prüfen
        base_url = llm_service.base_url
        logger.info(f"Ollama Base-URL: {base_url}")
        
        ***REMOVED*** Test-Anforderung
        test_requirement = "Als Disponent möchte ich eingehende Bestellungen automatisch prüfen lassen."
        
        logger.info("Teste Anforderungsanalyse mit Ollama...")
        analysis = await llm_service.analyze_requirement(
            test_requirement,
            context={"project_id": "test-ollama", "test": True}
        )
        
        logger.info("✅ Anforderungsanalyse erfolgreich!")
        print("\n=== Ollama-Analyse ===")
        print(analysis)
        
        ***REMOVED*** Teste Klärungsfragen
        logger.info("Teste Generierung von Klärungsfragen...")
        questions = await llm_service.generate_clarification_questions(
            analysis,
            context={"project_id": "test-ollama", "test": True}
        )
        
        logger.info("✅ Klärungsfragen erfolgreich generiert!")
        print(f"\n=== Klärungsfragen ({len(questions)}) ===")
        for i, question in enumerate(questions, 1):
            print(f"{i}. {question}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Fehler bei Ollama-Test: {str(e)}")
        return False


async def test_ollama_models():
    """Listet verfügbare Ollama-Modelle auf."""
    try:
        import aiohttp
        
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        async with aiohttp.ClientSession() as session:
            ***REMOVED*** Verfügbare Modelle abrufen
            async with session.get(f"{base_url}/api/tags") as response:
                if response.status == 200:
                    models_data = await response.json()
                    models = models_data.get("models", [])
                    
                    print(f"\n=== Verfügbare Ollama-Modelle ({len(models)}) ===")
                    for model in models:
                        name = model.get("name", "Unbekannt")
                        size = model.get("size", 0)
                        size_mb = size / (1024 * 1024) if size > 0 else 0
                        print(f"📦 {name} ({size_mb:.1f} MB)")
                    
                    return models
                else:
                    logger.error(f"Fehler beim Abrufen der Modelle: {response.status}")
                    return []
                    
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Modelle: {str(e)}")
        return []


async def test_ollama_van_mode():
    """Testet den VAN-Modus mit Ollama."""
    try:
        from backend.apm_framework.mongodb_connector import APMMongoDBConnector
        from backend.apm_framework.van_mode import VANMode
        
        ***REMOVED*** MongoDB-Connector (Mock für Test)
        mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        mongo_db = os.getenv("MONGODB_DB", "valeo_neuroerp")
        
        connector = APMMongoDBConnector(mongo_uri, mongo_db)
        
        ***REMOVED*** VAN-Modus mit Ollama initialisieren
        van_mode = VANMode(connector, "test-ollama", "ollama")
        
        logger.info("VAN-Modus mit Ollama initialisiert")
        
        ***REMOVED*** Test-Anforderung
        test_requirement = """
        Als Disponent im VALEO NeuroERP möchte ich, dass eingehende Kundenbestellungen 
        automatisch auf Vollständigkeit und Plausibilität geprüft werden. 
        Bei Unklarheiten sollen automatisch präzise Klärungsfragen generiert werden.
        """
        
        logger.info("Führe VAN-Analyse mit Ollama aus...")
        result = await van_mode.run(test_requirement)
        
        logger.info("✅ VAN-Analyse mit Ollama erfolgreich!")
        print("\n=== VAN-Ergebnis mit Ollama ===")
        print(f"ID: {result.get('id', 'N/A')}")
        print(f"LLM-Provider: {result.get('llm_provider', 'N/A')}")
        print(f"Klärungsfragen: {len(result.get('clarifications', []))}")
        print(f"Ähnliche Anforderungen: {len(result.get('similar_requirements', []))}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Fehler bei VAN-Modus-Test: {str(e)}")
        return False


async def main():
    """Hauptfunktion für alle Tests."""
    print("🚀 Ollama-Integration Test für VALEO NeuroERP VAN-Modus")
    print("=" * 60)
    
    ***REMOVED*** Umgebungsvariablen setzen
    os.environ.setdefault("OLLAMA_BASE_URL", "http://localhost:11434")
    os.environ.setdefault("OLLAMA_MODEL", "llama3.2:3b")
    
    print(f"🔧 Konfiguration:")
    print(f"   Ollama URL: {os.getenv('OLLAMA_BASE_URL')}")
    print(f"   Standard-Modell: {os.getenv('OLLAMA_MODEL')}")
    print()
    
    ***REMOVED*** Test 1: Ollama-Verbindung
    print("📡 Test 1: Ollama-Verbindung")
    connection_ok = await test_ollama_connection()
    print()
    
    ***REMOVED*** Test 2: Verfügbare Modelle
    print("📦 Test 2: Verfügbare Modelle")
    models = await test_ollama_models()
    print()
    
    ***REMOVED*** Test 3: VAN-Modus Integration
    print("🧠 Test 3: VAN-Modus mit Ollama")
    van_ok = await test_ollama_van_mode()
    print()
    
    ***REMOVED*** Zusammenfassung
    print("📊 Test-Zusammenfassung")
    print("=" * 30)
    print(f"✅ Ollama-Verbindung: {'OK' if connection_ok else 'FEHLER'}")
    print(f"✅ Verfügbare Modelle: {len(models)} gefunden")
    print(f"✅ VAN-Modus: {'OK' if van_ok else 'FEHLER'}")
    
    if connection_ok and van_ok:
        print("\n🎉 Alle Tests erfolgreich! Ollama ist bereit für den VAN-Modus.")
        print("\n💡 Nächste Schritte:")
        print("   1. Demo mit Ollama starten: LLM_PROVIDER=ollama python scripts/run_van_workflow_demo.py")
        print("   2. Verschiedene Modelle testen: OLLAMA_MODEL=mistral:7b python scripts/run_van_workflow_demo.py")
        print("   3. Frontend mit Ollama-Integration starten")
    else:
        print("\n⚠️  Einige Tests fehlgeschlagen. Bitte prüfen Sie:")
        print("   1. Ist Ollama installiert und läuft?")
        print("   2. Ist der Standardport 11434 verfügbar?")
        print("   3. Sind Modelle heruntergeladen? (ollama pull llama3.2:3b)")


if __name__ == "__main__":
    asyncio.run(main())
