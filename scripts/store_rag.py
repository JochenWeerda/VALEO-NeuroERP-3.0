import sys
sys.path.append('../linkup_mcp')

from rag_system.document_store import MCPDocumentStore
from rag_system.embeddings import MCPEmbeddings
import datetime

def store_in_rag():
    ***REMOVED*** RAG System initialisieren
    doc_store = MCPDocumentStore()
    embeddings = MCPEmbeddings()
    
    ***REMOVED*** Dokument vorbereiten
    document = {
        "title": "VALERO-NeuroERP Systemstruktur v1.04",
        "content": """
***REMOVED*** Systemarchitektur

***REMOVED******REMOVED*** Backend
- Microservices (Node.js + Express)
- Redis Caching
- MongoDB für Dokumente
- PostgreSQL für Transaktionen
- Load Balancing (20+ Nutzer)

***REMOVED******REMOVED*** Frontend
- React mit Lazy Loading
- Client-side Caching
- Progressive Web App
- Offline-First
- Modulare Komponenten

***REMOVED******REMOVED*** KI-Integration
- Lokales LLM
- GPT-4 API
- Caching
- Asynchrone Verarbeitung
- Batch-Processing

***REMOVED*** Kernmodule

***REMOVED******REMOVED*** Belegerfassung
- Schnelle Masken
- Lokaler Cache
- Auto-Nummerierung
- Vorlagen
- Offline-Modus

***REMOVED******REMOVED*** Warenwirtschaft
- Echtzeit-Bestände
- Optimierte Abfragen
- Stammdaten-Cache
- Batch-Updates
- Schnellsuche

***REMOVED******REMOVED*** Finanzbuchhaltung
- Performanter Kontenrahmen
- Optimierte Buchungen
- Background-Berechnungen
- Inkrementelle Updates
- Auto-Abstimmung

***REMOVED******REMOVED*** CRM
- Cached Basisdaten
- Lazy Loading Details
- Schnellsuche
- Priorisierte Updates
- Effiziente Historie

***REMOVED*** Performance

***REMOVED******REMOVED*** Ziele
- Belegerfassung: < 1s
- Suche: < 2s
- Reports: < 5s
- KI: < 3s
- Stammdaten: < 1s

***REMOVED******REMOVED*** Skalierung
- 20 Nutzer Standard
- Bis 50 Nutzer skalierbar
- Load Balancing ab 15
- Auto-Optimierung

***REMOVED*** Implementation
- Phase 1 (4W): Basis
- Phase 2 (4W): Module
- Phase 3 (2W): KI
- Phase 4 (2W): Optimierung
""",
        "metadata": {
            "version": "1.04",
            "type": "system_structure",
            "date": datetime.datetime.now().isoformat(),
            "category": "technical_documentation",
            "tags": ["architecture", "performance", "modules", "implementation"]
        }
    }
    
    ***REMOVED*** In RAG System speichern
    doc_id = doc_store.add_document(document)
    
    ***REMOVED*** Embeddings erstellen
    embeddings.create_embeddings(doc_id)
    
    print("Dokument erfolgreich im RAG-System gespeichert")

if __name__ == "__main__":
    store_in_rag() 