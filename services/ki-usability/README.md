# KI Usability API

Microservice für einheitliche KI-Usability: **Action Registry** und **Voice-to-Intent** (Sprachsteuerung).  
Abgestimmt auf [UX-Standard VALEO](../../docs/UX-STANDARD-VALEO.md) (PageToolbar + Tastaturkürzel + Sprachsteuerung).

## Endpoints

- `GET /api/v1/actions` – Liste aller Aktionen (Query: `?domain=finance&mask=...`)
- `GET /api/v1/actions/{action_id}` – Eine Aktion
- `POST /api/v1/voice/resolve` – Text → `{ action_id, params, confidence }`
- `GET /health` – Health Check

## Lauf

```bash
cd services/ki-usability
pip install -r requirements.txt
uvicorn main:app --reload --port 5200
```

## Docker

```bash
docker build -t ki-usability-api .
docker run -p 5200:5200 ki-usability-api
```

## Konfiguration

Umgebungsvariablen (optional, Präfix `KI_USABILITY_`):

- `HOST`, `PORT` (default 5200)
- `BACKEND_CORS_ORIGINS` (Komma-getrennt)
- `AI_SERVICE_URL`, `AI_SERVICE_ENABLED` (für spätere NLU-Anbindung)

## Architektur

Siehe [docs/architecture/KI-USABILITY-MICROSERVICES.md](../../docs/architecture/KI-USABILITY-MICROSERVICES.md).
