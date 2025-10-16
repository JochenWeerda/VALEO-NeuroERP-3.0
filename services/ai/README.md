***REMOVED*** VALEO-NeuroERP AI Service

Microservice für AI/ML-Funktionalität im ERP-System.

***REMOVED******REMOVED*** Architektur

**Hybrid REST + MCP**:
- **REST API** (Port 5000): Synchrone AI-Funktionen für 181 Masken
- **MCP Server** (Port 5001): Komplexe Agent-Workflows mit Tools & Prompts

***REMOVED******REMOVED*** Features

***REMOVED******REMOVED******REMOVED*** 1. Assistants API (`/api/v1/assistants`)
AI-Unterstützung für alle 181 ERP-Masken:
- **Autocomplete**: Intelligente Vorschläge basierend auf Kontext
- **Validation**: Business-Logic-Validierung in Echtzeit
- **Suggestions**: Nächste Aktionen vorschlagen
- **Explanation**: Felder & Prozesse erklären

**Beispiel**:
```bash
curl -X POST http://localhost:5000/api/v1/assistants/autocomplete \
  -H "Content-Type: application/json" \
  -d '{
    "mask_id": "sales_order",
    "field": "customer",
    "query": "Müll",
    "context": {},
    "action": "autocomplete"
  }'
```

***REMOVED******REMOVED******REMOVED*** 2. Classification API (`/api/v1/classify`)
Dokumenten-Klassifizierung:
- Rechnungen (mit Extraktion: Betrag, Lieferant, Datum)
- Lieferscheine
- Analyseberichte
- Zertifikate
- E-Mails

**Beispiel**:
```bash
curl -X POST http://localhost:5000/api/v1/classify/document \
  -F "file=@rechnung.pdf"
```

***REMOVED******REMOVED******REMOVED*** 3. RAG API (`/api/v1/rag`)
Semantic Search über ERP-Wissensbasis:
- Dokumentation durchsuchen
- Policies finden
- Ähnliche Vorgänge
- Best Practices

**Beispiel**:
```bash
curl -X POST http://localhost:5000/api/v1/rag/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Wie buche ich Eingangsrechnungen mit SKR03?",
    "domain": "finance",
    "top_k": 5,
    "include_answer": true
  }'
```

***REMOVED******REMOVED******REMOVED*** 4. Agents API (`/api/v1/agents`)
Multi-Step-Workflows mit LangGraph:
- **procurement_advisor**: Bestellvorschläge aus Lager + Feldbuch
- **compliance_checker**: EUDR & Cross-Compliance Prüfung
- **invoice_processor**: Automatische Rechnungsverarbeitung
- **field_optimizer**: Anbauplanung optimieren

**Beispiel**:
```bash
curl -X POST http://localhost:5000/api/v1/agents/run \
  -H "Content-Type: application/json" \
  -d '{
    "workflow": "procurement_advisor",
    "messages": [],
    "context": {
      "inventory_low": ["wheat_seed", "fertilizer_n"]
    }
  }'
```

***REMOVED******REMOVED******REMOVED*** 5. Insights API (`/api/v1/insights`)
Business Intelligence & Prognosen:
- Umsatztrends
- Risiko-Erkennung
- Chancen-Identifikation
- Forecasting

**Beispiel**:
```bash
curl -X POST http://localhost:5000/api/v1/insights/generate \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "sales",
    "entity_id": "CUST-001",
    "period_start": "2025-01-01",
    "period_end": "2025-03-31"
  }'
```

***REMOVED******REMOVED******REMOVED*** 6. MCP Endpoints (`/api/v1/mcp`)
Model Context Protocol für AI-Agents:
- **Tools**: Funktionen die AI aufrufen kann (DB-Query, Dokument-Suche, Order-Creation)
- **Resources**: Daten für Kontext (Policies, Templates)
- **Prompts**: Vorkonfigurierte Templates

**Tools**:
```bash
***REMOVED*** Liste Tools
curl http://localhost:5000/api/v1/mcp/tools

***REMOVED*** Tool aufrufen
curl -X POST http://localhost:5000/api/v1/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "query_database",
    "parameters": {
      "query": "SELECT * FROM contacts WHERE email LIKE '%@example.com'",
      "domain": "crm"
    }
  }'
```

**Resources**:
```bash
***REMOVED*** Liste Resources
curl http://localhost:5000/api/v1/mcp/resources

***REMOVED*** Resource abrufen
curl http://localhost:5000/api/v1/mcp/resources/policies/procurement
```

**Prompts**:
```bash
***REMOVED*** Liste Prompts
curl http://localhost:5000/api/v1/mcp/prompts

***REMOVED*** Prompt rendern
curl -X POST http://localhost:5000/api/v1/mcp/prompts/render \
  -H "Content-Type: application/json" \
  -d '{
    "prompt_name": "procurement_advisor",
    "variables": {
      "inventory": "Wheat: 200kg, Barley: 50kg",
      "field_plan": "Q1: 100ha Wheat, Q2: 50ha Barley",
      "season": "Spring 2026"
    }
  }'
```

***REMOVED******REMOVED*** Unterstützte Masken (181 gesamt)

| Domain | Masken | Beispiele |
|--------|--------|-----------|
| **Verkauf** | 15 | sales_order, sales_delivery, sales_invoice, sales_quote |
| **CRM** | 4 | crm_contacts, crm_leads, crm_activities, crm_farm_profiles |
| **Einkauf** | 12 | procurement_order, procurement_request, goods_receipt |
| **Finanzen** | 130 | SKR03/04 komplett, general_ledger, ar_invoice, ap_invoice |
| **Lager** | 8 | inventory_stock, inventory_movement, inventory_count |
| **Agrar** | 12 | field_book, seed, fertilizer, pesticide, harvest |

***REMOVED******REMOVED*** Development

***REMOVED******REMOVED******REMOVED*** Lokaler Start
```bash
cd services/ai
python -m venv venv
source venv/bin/activate  ***REMOVED*** Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

***REMOVED******REMOVED******REMOVED*** Docker
```bash
***REMOVED*** Build
docker-compose build ai

***REMOVED*** Start
docker-compose up -d ai

***REMOVED*** Logs
docker-compose logs -f ai
```

***REMOVED******REMOVED*** API-Dokumentation

- **Swagger UI**: http://localhost:5000/docs
- **ReDoc**: http://localhost:5000/redoc
- **OpenAPI**: http://localhost:5000/api/openapi.json
- **Health**: http://localhost:5000/health

***REMOVED******REMOVED*** Konfiguration

Über Umgebungsvariablen (`.env`):
```env
***REMOVED*** OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

***REMOVED*** Vector Store
CHROMA_PERSIST_DIR=/app/data/chroma
CHROMA_COLLECTION_NAME=valeo_erp_knowledge

***REMOVED*** Backend Communication
BACKEND_API_URL=http://backend:8000/api/v1
API_DEV_TOKEN=dev-token

***REMOVED*** Database (Read-Only)
DATABASE_URL=postgresql://valeo_dev:REDACTED_PASSWORD@postgres:5432/valeo_neuro_erp
```

***REMOVED******REMOVED*** Integration mit Backend

Backend kann AI-Service aufrufen:
```python
import httpx

async def get_autocomplete(mask_id: str, field: str, query: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://ai:5000/api/v1/assistants/autocomplete",
            json={
                "mask_id": mask_id,
                "field": field,
                "query": query,
                "context": {},
                "action": "autocomplete"
            }
        )
        return response.json()
```

***REMOVED******REMOVED*** Vector Store Management

```bash
***REMOVED*** Dokument indexieren
curl -X POST http://localhost:5000/api/v1/rag/index/document \
  -H "Content-Type: application/json" \
  -d '{
    "content": "SKR03 ist der Standard-Kontenrahmen...",
    "source": "docs/finance/skr03.md",
    "metadata": {
      "domain": "finance",
      "type": "documentation"
    }
  }'

***REMOVED*** Dokument entfernen
curl -X DELETE http://localhost:5000/api/v1/rag/index/docs/finance/skr03.md
```

***REMOVED******REMOVED*** Monitoring

- **Prometheus Metrics**: http://localhost:5000/metrics
- **Health Check**: http://localhost:5000/health

***REMOVED******REMOVED*** Next Steps

1. ✅ **Service läuft** (Mock-Implementierung)
2. 🔄 **OpenAI Integration** - Echte LLM-Calls
3. 🔄 **ChromaDB Integration** - Vector Store aktivieren
4. 🔄 **LangGraph Workflows** - Komplexe Agents
5. 🔄 **Training Data** - 181 Masken mit Beispielen


