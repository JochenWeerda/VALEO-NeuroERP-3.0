# RAG Sync Tool

CLI-Utility zur Synchronisation von Wissensinhalten (`knowledge-base/`) mit der Vektor-Datenbank für die RAG-Pipeline.

## Features

- Rekursive Erfassung von Markdown/Text-Dateien.
- Chunking nach Überschriften mit Tokenlimit.
- Embedding-Provider (Parameter `--embedding-provider`):
  - `auto` *(Standard)* – nutzt `OPENAI_API_KEY`, andernfalls Hash-Embeddings.
  - `openai` – erzwingt OpenAI (erfordert gültigen API-Key).
  - `hash` – deterministische lokale Embeddings (Offline/Tests).
- Optionaler Export als JSON.
- Optionales Upsert gegen einen RAG- oder Vector-Store-Endpunkt.
- Namespace-Unterstützung & Batch-Verarbeitung.

## Installation

```bash
cd tools/rag-sync
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Nutzung

```bash
python rag_sync.py \
  --source knowledge-base \
  --output artifacts/rag/chunks.json \
  --endpoint http://ai-service:5000/api/v1/rag/upsert \
  --namespace compliance \
  --embedding-provider auto \
  --embedding-model text-embedding-3-small
```

### Wichtige Flags

- `--dry-run`: Kein Upsert, nur Analyse/Export.
- `--batch-size`: Kontrolle über Batch-Größe für Upserts.
- `--verbose`: Detailliertes Logging.
- `--embedding-provider auto`: nutzt automatisch OpenAI, sobald `OPENAI_API_KEY` in der Umgebung gesetzt ist.

## Ausblick

- Unterstützung weiterer Dateitypen (HTML, PDF).
- Delta-Sync über File-Hashes.
- Automatischer Trigger via CI/CD.


