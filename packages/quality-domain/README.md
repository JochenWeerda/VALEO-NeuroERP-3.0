***REMOVED*** @valero-neuroerp/quality-domain

Qualitätsmanagement & Qualitätssicherung (QM/QS) Domain für VALEO-NeuroERP 3.0

***REMOVED******REMOVED*** 📋 Überblick

Die Quality-Domain ist ein zentraler Baustein des ERP-Systems und verantwortlich für:

- **Prüfpläne** (Quality Plans): Definition von Qualitätskriterien und Prüfregeln
- **Proben** (Samples): Erfassung und Verwaltung von Qualitätsproben
- **Laborergebnisse** (Sample Results): Analyse und Bewertung von Proben
- **Abweichungen** (Non-Conformities): Dokumentation und Verfolgung von Qualitätsabweichungen
- **CAPA** (Corrective & Preventive Actions): Korrektur- und Vorbeugungsmaßnahmen

***REMOVED******REMOVED*** 🏗️ Architektur

***REMOVED******REMOVED******REMOVED*** Domain-Driven Design (DDD)

```
quality-domain/
├── src/
│   ├── app/                      ***REMOVED*** Application Layer
│   │   ├── server.ts             ***REMOVED*** Fastify Server
│   │   ├── routes/               ***REMOVED*** REST API Routes
│   │   └── middleware/           ***REMOVED*** Auth, Tenant, Logging, etc.
│   ├── domain/                   ***REMOVED*** Domain Layer
│   │   ├── entities/             ***REMOVED*** Domain Models (Zod Schemas)
│   │   └── services/             ***REMOVED*** Business Logic / Use Cases
│   ├── infra/                    ***REMOVED*** Infrastructure Layer
│   │   ├── db/                   ***REMOVED*** Database (Drizzle + PostgreSQL)
│   │   ├── messaging/            ***REMOVED*** Event Bus (NATS)
│   │   ├── telemetry/            ***REMOVED*** OpenTelemetry
│   │   └── security/             ***REMOVED*** JWT/Auth
│   └── contracts/                ***REMOVED*** API Contracts
└── tests/                        ***REMOVED*** Unit & E2E Tests
```

***REMOVED******REMOVED*** 🚀 Quick Start

***REMOVED******REMOVED******REMOVED*** Voraussetzungen

- Node.js ≥ 20
- PostgreSQL ≥ 14
- NATS Server (optional, für Events)
- Redis (optional, für Caching)

***REMOVED******REMOVED******REMOVED*** Installation

```bash
***REMOVED*** Dependencies installieren
npm install

***REMOVED*** Environment-Variablen kopieren
cp .env.example .env

***REMOVED*** Datenbank-Migrationen ausführen
npm run migrate:up

***REMOVED*** Entwicklungsserver starten
npm run dev
```

***REMOVED******REMOVED******REMOVED*** Environment-Variablen

Siehe `.env.example` für eine vollständige Liste. Wichtigste Variablen:

```env
PORT=3007
DATABASE_URL=postgres://postgres:postgres@localhost:5432/quality_db
NATS_URL=nats://localhost:4222
OTEL_ENABLED=true
```

***REMOVED******REMOVED*** 📡 API-Endpunkte

***REMOVED******REMOVED******REMOVED*** Base URL
`http://localhost:3007/quality/api/v1`

***REMOVED******REMOVED******REMOVED*** Quality Plans

- `POST /plans` - Prüfplan erstellen
- `GET /plans` - Prüfpläne auflisten
- `GET /plans/:id` - Prüfplan abrufen
- `PATCH /plans/:id` - Prüfplan aktualisieren
- `POST /plans/:id/deactivate` - Prüfplan deaktivieren

***REMOVED******REMOVED******REMOVED*** Samples

- `POST /samples` - Probe erstellen
- `GET /samples` - Proben auflisten
- `GET /samples/:id` - Probe abrufen
- `POST /samples/:id/results` - Laborergebnis hinzufügen
- `GET /samples/:id/results` - Ergebnisse abrufen
- `POST /samples/:id/analyze` - Probe analysieren (Freigabe/Sperre)

***REMOVED******REMOVED******REMOVED*** Non-Conformities

- `POST /ncs` - Abweichung erfassen
- `GET /ncs` - Abweichungen auflisten (pagination)
- `GET /ncs/:id` - Abweichung abrufen
- `PATCH /ncs/:id` - Abweichung aktualisieren
- `POST /ncs/:id/close` - Abweichung abschließen
- `POST /ncs/:id/assign` - Abweichung zuweisen
- `POST /ncs/:id/link-capa` - Mit CAPA verknüpfen
- `GET /ncs/stats` - NC-Statistiken

***REMOVED******REMOVED******REMOVED*** CAPA

- `POST /capas` - CAPA erstellen
- `GET /capas` - CAPAs auflisten (pagination)
- `GET /capas/:id` - CAPA abrufen
- `PATCH /capas/:id` - CAPA aktualisieren
- `POST /capas/:id/implement` - CAPA implementieren
- `POST /capas/:id/verify` - CAPA verifizieren
- `POST /capas/:id/close` - CAPA abschließen
- `POST /capas/:id/escalate` - CAPA eskalieren
- `GET /capas/overdue` - Überfällige CAPAs
- `GET /capas/stats` - CAPA-Statistiken

***REMOVED******REMOVED******REMOVED*** Health Checks

- `GET /health` - Server-Status
- `GET /ready` - Bereitschaftsprüfung
- `GET /live` - Liveness-Prüfung

***REMOVED******REMOVED*** 📚 OpenAPI-Dokumentation

Interaktive API-Dokumentation verfügbar unter:
```
http://localhost:3007/documentation
```

OpenAPI JSON Schema:
```
http://localhost:3007/quality/api/v1/openapi.json
```

***REMOVED******REMOVED*** 🔐 Authentifizierung & Autorisierung

***REMOVED******REMOVED******REMOVED*** Headers (erforderlich)

```http
Authorization: Bearer <JWT-Token>
x-tenant-id: <UUID>
```

***REMOVED******REMOVED******REMOVED*** Permissions

- `quality:plan:create` - Prüfpläne erstellen
- `quality:plan:update` - Prüfpläne bearbeiten
- `quality:sample:create` - Proben erfassen
- `quality:sample:analyze` - Proben analysieren
- `quality:nc:create` - Abweichungen erfassen
- `quality:nc:approve` - Abweichungen genehmigen
- `quality:capa:create` - CAPAs erstellen
- `quality:capa:verify` - CAPAs verifizieren

***REMOVED******REMOVED*** 🔔 Domain-Events

Die Domain publiziert folgende Events über NATS:

***REMOVED******REMOVED******REMOVED*** Quality Plan Events
- `quality.plan.created`
- `quality.plan.updated`
- `quality.plan.deactivated`

***REMOVED******REMOVED******REMOVED*** Sample Events
- `quality.sample.taken`
- `quality.sample.result.added`
- `quality.sample.analyzed`

***REMOVED******REMOVED******REMOVED*** Quality Status Events
- `quality.batch.released`
- `quality.batch.quarantined`
- `quality.batch.rejected`
- `quality.issue.detected`

***REMOVED******REMOVED******REMOVED*** NC & CAPA Events
- `quality.nc.created`
- `quality.nc.updated`
- `quality.nc.closed`
- `quality.capa.created`
- `quality.capa.implemented`
- `quality.capa.verified`

***REMOVED******REMOVED*** 🔗 Integration mit anderen Domains

***REMOVED******REMOVED******REMOVED*** Production Domain
- Empfängt Batch-Completion-Events
- Sendet Quality-Status-Events zurück (Released/Rejected)
- Rückstellproben-Verwaltung

***REMOVED******REMOVED******REMOVED*** Contracts Domain
- Qualitätsvereinbarungen in Verträgen
- Claims bei Abweichungen
- Spezifikationsprüfung bei Lieferungen

***REMOVED******REMOVED******REMOVED*** Inventory Domain
- Freigaben/Sperren wirken auf Lot-Verfügbarkeit
- Quarantäne-Lagerung

***REMOVED******REMOVED******REMOVED*** Analytics Domain
- Pass/Fail-Raten je Commodity
- NC-Quote je Lieferant
- CAPA-Durchlaufzeiten
- Prognosen zu Qualitätsrisiken

***REMOVED******REMOVED*** 🧪 Testing

```bash
***REMOVED*** Unit-Tests
npm run test

***REMOVED*** Mit Coverage
npm run test:coverage

***REMOVED*** Watch-Mode
npm run test:watch

***REMOVED*** E2E-Tests (erfordert laufende DB)
npm run test:e2e
```

***REMOVED******REMOVED*** 🐳 Docker

***REMOVED******REMOVED******REMOVED*** Build Image
```bash
docker build -t valero-quality-domain:latest .
```

***REMOVED******REMOVED******REMOVED*** Run Container
```bash
docker run -d \
  --name quality-domain \
  -p 3007:3007 \
  -e DATABASE_URL=postgres://... \
  -e NATS_URL=nats://... \
  valero-quality-domain:latest
```

***REMOVED******REMOVED******REMOVED*** Docker Compose
```bash
docker-compose up quality-domain
```

***REMOVED******REMOVED*** 📊 Observability

***REMOVED******REMOVED******REMOVED*** Logging
Strukturierte Logs mit Pino:
```json
{
  "level": "info",
  "time": 1696291200000,
  "msg": "Request completed",
  "method": "POST",
  "url": "/quality/api/v1/samples",
  "statusCode": 201,
  "duration": 45,
  "tenantId": "...",
  "requestId": "..."
}
```

***REMOVED******REMOVED******REMOVED*** Metrics
- Request Count, Latency (Histogramme)
- Sample-Analyse-Rate
- NC-Erstellungsrate
- CAPA-Abschlussrate

***REMOVED******REMOVED******REMOVED*** Tracing
OpenTelemetry-Integration für Distributed Tracing.

***REMOVED******REMOVED*** 🛠️ Entwicklung

***REMOVED******REMOVED******REMOVED*** Lokale Datenbank
```bash
***REMOVED*** Postgres starten
docker run -d \
  --name quality-db \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=quality_db \
  -p 5432:5432 \
  postgres:16-alpine
```

***REMOVED******REMOVED******REMOVED*** Migrationen

```bash
***REMOVED*** Migration erstellen
npm run migrate:gen

***REMOVED*** Migration anwenden
npm run migrate:up

***REMOVED*** Drizzle Studio (DB-GUI)
npm run db:studio
```

***REMOVED******REMOVED******REMOVED*** Linting & Formatting

```bash
npm run lint
npm run format
```

***REMOVED******REMOVED*** 📝 Beispiel: Qualitätsprüfung

***REMOVED******REMOVED******REMOVED*** 1. Prüfplan erstellen

```bash
POST /quality/api/v1/plans
Content-Type: application/json
x-tenant-id: 123e4567-e89b-12d3-a456-426614174000

{
  "name": "Rapsöl-Standardprüfung",
  "commodity": "RAPE_OIL",
  "active": true,
  "rules": [
    {
      "analyte": "Moisture",
      "method": "Karl-Fischer",
      "unit": "%",
      "min": 0,
      "max": 0.1,
      "frequency": "perBatch",
      "retainSample": true,
      "retentionDays": 180
    },
    {
      "analyte": "FFA",
      "method": "Titration",
      "unit": "%",
      "min": 0,
      "max": 2.0,
      "frequency": "perBatch",
      "retainSample": false
    }
  ]
}
```

***REMOVED******REMOVED******REMOVED*** 2. Probe erfassen

```bash
POST /quality/api/v1/samples
Content-Type: application/json
x-tenant-id: 123e4567-e89b-12d3-a456-426614174000

{
  "batchId": "batch-uuid",
  "source": "Production",
  "takenAt": "2025-10-01T10:30:00Z",
  "takenBy": "user-uuid",
  "takenLocation": "Silo 3, Top",
  "planId": "plan-uuid",
  "retained": true,
  "retainedLocation": "Kühlschrank A, Fach 3",
  "retainedUntil": "2026-04-01T00:00:00Z"
}
```

***REMOVED******REMOVED******REMOVED*** 3. Laborergebnis hinzufügen

```bash
POST /quality/api/v1/samples/{sampleId}/results
Content-Type: application/json
x-tenant-id: 123e4567-e89b-12d3-a456-426614174000

{
  "analyte": "Moisture",
  "value": 0.08,
  "unit": "%",
  "method": "Karl-Fischer",
  "labId": "Lab-A",
  "analyzedAt": "2025-10-01T14:00:00Z",
  "analyzedBy": "lab-tech-uuid",
  "result": "Pass",
  "limits": {
    "min": 0,
    "max": 0.1
  }
}
```

***REMOVED******REMOVED******REMOVED*** 4. Probe analysieren

```bash
POST /quality/api/v1/samples/{sampleId}/analyze
Content-Type: application/json
x-tenant-id: 123e4567-e89b-12d3-a456-426614174000

***REMOVED*** Response:
{
  "status": "Released",
  "allPass": true
}
```

***REMOVED******REMOVED*** 🤝 Beitragen

1. Feature-Branch erstellen
2. Änderungen committen
3. Tests hinzufügen/aktualisieren
4. Pull Request erstellen

***REMOVED******REMOVED*** 📄 Lizenz

Proprietary - VALEO GmbH

***REMOVED******REMOVED*** 📧 Kontakt

VALEO NeuroERP Team
- Dokumentation: `/docs/`
- Issues: JIRA Quality-Domain Board
