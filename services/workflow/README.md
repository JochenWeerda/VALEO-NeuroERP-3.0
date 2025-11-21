# Workflow Service

Microservice für deklarative Workflows, Policies, Eventing und Saga-Orchestrierung innerhalb von VALEO NeuroERP 3.0.

## Features

- Registrierung und Versionierung von Workflow-Definitionen (persistiert in PostgreSQL).
- Ausführung mit Hook-Punkten für Policies, Aktionen (inkl. `emit_event`) und KI-Empfehlungen.
- Event-Routing via REST oder NATS (`workflow.<event>`), inkl. optionaler Weiterleitung.
- Saga-Koordinator für Langläuferprozesse inkl. Kompensation.
- Simulation von Workflows zur Validierung neuer Regeln.

## Endpunkte (Auszug)

- `POST /api/v1/workflows/definitions` – Neue Definition registrieren.
- `POST /api/v1/workflows/instances` – Workflow-Instanz starten.
- `POST /api/v1/workflows/instances/{id}/transitions` – Transition auslösen.
- `POST /api/v1/workflows/events` – Domain-Event verarbeiten.
- `POST /api/v1/workflows/simulate` – Szenario simulieren.
- `POST /api/v1/sagas/definitions/{name}` – Saga registrieren.
- `POST /api/v1/sagas/instances/{name}` – Saga starten.

## Quickstart

```bash
cd services/workflow
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 5100
```

### Optionale Infrastruktur

- PostgreSQL (Schema: `workflow_definitions`, `workflow_instances`)
- NATS Event-Bus (`nats://nats:4222`, Subject: `workflow.*`)

## Ausblick

- Erweiterung der Persistenz um Audit-Trails & Archivrechte.
- Native Unterstützung weiterer Event-Broker (Kafka, Redis Streams).
- RAG-gestützte Empfehlungen für neue Transitionen und Sagas.


