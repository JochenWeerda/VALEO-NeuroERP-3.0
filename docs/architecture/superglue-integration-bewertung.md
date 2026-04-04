# Superglue-Integrationsarchitektur — Bewertung und Planungsgrundlage

**Status:** Draft / Planungsgrundlage
**Datum:** 2026-04-03
**Bezug:** ADR-014 (Integrationsgrenzen), ADR-007 (Agent-Tool-Contract-Governance), NeuroASSIST Target Architecture

## 1. Gegenstand

Bewertung des Architekturvorschlags, [superglue](https://github.com/superglue-ai/superglue) (FSL-1.1-Apache-2.0) als kontrollierte Integrations-Infrastruktur hinter der VALEO Integration Boundary einzusetzen. Superglue übernimmt externe Konnektivität (APIs, Dateien, Legacy); VALEO behält die vollständige Hoheit über Geschäftslogik, Workflow, Policy und Domain Core.

### 1.1 Was superglue mitbringt

| Komponente | Port | Funktion |
|------------|------|----------|
| **GraphQL Server** | 3000 | Primäre Datenschicht, Tool-Ausführung, Konfiguration |
| **Web Dashboard** | 3001 | React-UI (shadcn/Radix) für Integration-Management, Tool-Erstellung, Chat-Agent |
| **REST API** | 3002 | Tool-Execution, Monitoring, Health |
| **PostgreSQL 16** | 5432 | Konfigurationsspeicher (Datastore-Abstraktion) |
| **MinIO** | 9000/9001 | S3-kompatibler Object Storage für Dateien |

Kern-Features:
- LLM-gestützte Transform-Pipeline (Mapping bei Konfiguration, gecachtes JS zur Laufzeit)
- Drift Detection bei API-Schema-Änderungen
- REST, GraphQL, SOAP, DB (Postgres, Redis), Dateisysteme (FTP/SFTP)
- Formate: JSON, XML, CSV
- Chat-basierte Konfigurations-UI (Enterprise: Agent-Chat)
- Retry-Strategien, Worker Pools, optionales Cron-Scheduling

---

## 2. Gesamtbewertung

### 2.1 Architektonische Passung: **85 % tragfähig**

Der Vorschlag ist mit den bestehenden ADRs und der NeuroASSIST-Architektur konsistent. Die Kernentscheidung — superglue als **kontrollierte Infrastruktur hinter der Integration Boundary**, nicht als Business-Logic-Layer — ist die richtige Positionierung.

### 2.2 Stärken

**Passt zu ADR-014 (Integrationsgrenzen)**
Superglue wird korrekt als Partneradapter-Infrastruktur eingeordnet (ADR-014, Punkt 4: „Partneradapter kapseln Fremdsystem-Spezifika und dürfen nicht in den Domain Core ausstrahlen"). Die 4 Zielzonen (Dokumente, Partner/Legacy, Agent-Tools, schnelle Anbindungen) sind saubere Spezialfälle.

**Passt zu ADR-007 (Agent-Tool-Contract-Governance)**
Die Execution Modes (`read → suggest → simulate → execute`) spiegeln das Gate-Modell der NeuroASSIST-Architektur wider (`analysis → proposal → approval → execution`). Das External Result Envelope ist das richtige Pattern für auditierbare Agenten-Aktionen (ADR-007, Punkt 6).

**Klare Nicht-Durchgriffs-Regel**
Superglue darf keine eigene Geschäftslogik etablieren — ADR-014 Punkt 2 wörtlich.

**Phase-Rollout mit HITL**
Die 3 Phasen (Controlled Edge → HITL → Controlled Execution) passen zum Gate-Modell (`approval_gate`, `policy_gate` in der NeuroASSIST Stage Engine).

---

## 3. Risiken und erforderliche Korrekturen

### Risk 1: Doppel-Orchestrierung (`integration-orchestrator` vs. NeuroASSIST)

**Problem:** Der Vorschlag führt einen eigenen `integration-orchestrator` ein. NeuroASSIST hat bereits Stage Engine + Gate Engine + Command Boundary als Orchestrierungsschicht. Zwei Orchestratoren = unklare Zuständigkeit.

**Korrektur:** Kein eigener `integration-orchestrator`. Superglue-Aufrufe laufen als Capability im bestehenden NeuroASSIST Capability Pack. Die Stage Engine entscheidet, wann ein externer Aufruf stattfindet; die Command Boundary erzwingt den Audit-Trail. Superglue ist ein `ExecutionPack`-Provider, kein eigener Orchestrator.

**Auswirkung auf superglue:** Keine. Superglue's eigene Orchestrierung (Worker Pools, Retry, Transform-Pipeline) bleibt intern erhalten. Nur der Aufruf-Einstiegspunkt wird über VALEO's Command Boundary kanalisiert statt über einen separaten Orchestrator.

### Risk 2: Doppel-Katalog (Tool Registry vs. Agent Manifest)

**Problem:** Es existiert bereits `ExternalAgentIntegrationManifest` + `AgentCommandManifest`. Eine separate Tool Registry für superglue-Tools führt zu Drift.

**Korrektur:** Superglue-Tools als Einträge im bestehenden Agent Manifest registrieren mit `provider: superglue` Tag. Die `external_agent_integrations.py`-API (`GET /agent/integrations/providers`) liefert superglue automatisch als Provider.

**Auswirkung auf superglue:** Keine. Superglue's interne Tool-Registry bleibt erhalten. VALEO synchronisiert die relevanten Tools in sein eigenes Manifest — ein Sync-Adapter liest superglue's GraphQL-Katalog und registriert die Tools im VALEO Agent Manifest.

### Risk 3: SSRF-Lücke (Outbound Security Bypass)

**Problem:** `app/core/outbound_security.py` validiert ausgehende HTTP-Calls gegen Allowlists. Superglue macht eigene HTTP-Calls zu externen APIs und umgeht dabei VALEO's SSRF-Schutz.

**Korrektur:** Zweistufig:
1. Docker Network Policy / Egress-Allowlist auf Container-Ebene
2. Adapter Contract prüft `target_url` gegen `validate_outbound_http_target()` bevor der Aufruf an superglue delegiert wird

**Auswirkung auf superglue:** Superglue's Funktionalität bleibt erhalten. Die Einschränkung betrifft nur, welche Ziel-URLs konfiguriert werden dürfen — das ist eine Operations-Entscheidung, kein Code-Eingriff in superglue.

### Risk 4: Fehlende Tenant-Isolation

**Problem:** Superglue ist tenant-agnostisch. VALEO ist multi-tenant. Ohne Tenant-Context im Request: Cross-Tenant-Datenfluss möglich.

**Korrektur:**
- Adapter Contract enthält zwingend `tenant_id` als Pflichtfeld
- External Result Envelope enthält zwingend `tenant_id` + `correlation_id`
- Superglue bekommt tenant-spezifische API-Keys/Credentials aus einem Vault — nie Shared Credentials
- Superglue's Auth-Token wird pro Tenant-Kontext ausgestellt

**Auswirkung auf superglue:** Keine Code-Änderung an superglue nötig. Der VALEO-Adapter-Layer injiziert den Tenant-Context in Headers/Metadata bei jedem Call. Superglue sieht davon nur die Credentials und Request-Daten.

---

## 4. Fehlende Bausteine

| Baustein | Status | Empfehlung |
|----------|--------|------------|
| **Circuit Breaker** | fehlt | Superglue-Calls brauchen Timeout + Retry + Fallback. Analog zur NATS-DLQ (`max_redeliveries=5`). |
| **Event-Integration** | fehlt | Ergebnisse fließen als `IntegrationEvent` über den Outbox-Publisher, nicht als direkte DB-Writes. |
| **Cost Tracking** | fehlt | `cost_cents`-Feld im External Result Envelope für Tenant-Verrechnung. |
| **Schema-Versioning** | fehlt | Adapter Contracts brauchen `schema_version` analog zu Process Events. |

---

## 5. Bewertung der 4 Zielzonen

| Zone | Eignung | Kommentar |
|------|---------|-----------|
| **Dokumente/Dateien** | Gut | Paperless-ngx bleibt nativ. Superglue ergänzt für Nicht-Paperless-DMS (SharePoint, Google Drive etc.). |
| **Partner/Legacy** | Sehr gut | EDI (EDIFACT ORDERS D97A) ist heute hardcoded im Einkauf. Superglue als Abstraktionsschicht für Partner-Formate ist der richtige Move. |
| **Agent Tool-Ausführung** | Vorsicht | Muss zwingend durch NeuroASSIST Stage/Gate laufen. Kein Bypass der Approval-Chain. |
| **Schnelle neue Anbindungen** | Gut | Größter Hebel. Aber jede „schnelle" Anbindung braucht trotzdem einen Adapter Contract. |

---

## 6. Entscheidung: Superglue Web-Frontend

### 6.1 Status Quo

Superglue liefert ein React-Dashboard (Port 3001) mit:
- Integration-Management (CRUD für Tools/Connections)
- Chat-basierte Konfigurations-UI
- Monitoring/Health
- Enterprise: AI Agent Chat

### 6.2 Entscheidung: Eigenständige Service-Seite

**Empfehlung: Superglue-Dashboard als eigenständige interne Admin-Seite betreiben, NICHT in VALEO-Frontend integrieren.**

Begründung:
1. **Zielgruppen-Trennung**: Superglue-Dashboard ist für Integrations-Admins / DevOps, nicht für ERP-Endbenutzer. VALEO-Frontend ist für Fachbenutzer.
2. **Technischer Konflikt**: Beide nutzen React + Radix, aber auf Port 3001. VALEO-Frontend läuft ebenfalls auf 3001 in dev. Port-Collision vermeiden durch superglue auf 3010.
3. **Update-Unabhängigkeit**: Superglue-Updates (neue UI-Features) können unabhängig von VALEO-Frontend-Releases deployed werden.
4. **Kein UI-Merge**: Superglue-Chat und VALEO-UI zu mergen erzeugt UX-Inkohärenz. Die Masken-Sprache (ObjectPage, ListReport, Wizard) passt nicht zu superglue's Chat-first-Paradigma.

### 6.3 Entscheidung: Chat-Kanal

**Empfehlung: Superglue-Chat nur im Admin-Dashboard nutzen, NICHT als Kanal in VALEO-NeuroASSIST einbinden.**

Begründung:
1. Superglue-Chat dient der **Integrations-Konfiguration** (Mappings erstellen, Transforms definieren). Das ist ein Infrastruktur-Vorgang, kein fachlicher ERP-Workflow.
2. VALEO hat mit NeuroASSIST ein eigenes fachliches Assistenzmodell mit Role Contracts, Capability Packs und Stage/Gate-Orchestrierung. Ein zweiter Chat-Kanal mit eigener Semantik untergräbt die Governance.
3. Für fachliche Agenten-Interaktion (Bestellvorschlag, Compliance-Review etc.) bleibt NeuroASSIST der einzige Kanal.
4. Langfristig: Wenn superglue-Konfigurationsaufgaben automatisiert werden sollen, läuft das über einen `platform_improvement_assistant` (NeuroASSIST Rolle 6), der superglue's GraphQL-API programmatisch ansteuert — nicht über Chat.

### 6.4 Zugriff auf das Superglue-Dashboard

```
VALEO-Endbenutzer:
  → VALEO Frontend (Port 3001)
  → Keine Sichtbarkeit auf superglue

Integrations-Admin / DevOps:
  → VALEO Frontend (Port 3001) — für ERP-Arbeit
  → Superglue Dashboard (Port 3010) — für Integration-Config
  → Zugang über separaten Auth-Flow (superglue AUTH_TOKEN)
```

Optional in Phase 3: Ein Link im VALEO Admin-Bereich (`/admin/integrations`) öffnet das superglue-Dashboard in einem neuen Tab. Kein iframe, kein Embedding.

---

## 7. Entscheidung: Deployment-Modell

### 7.1 Empfehlung: Eigenständiger Docker-Container, orchestriert über docker-compose

**NICHT tiefer integrieren.** Superglue als Black-Box-Service behandeln.

### 7.2 Ziel-Deployment

```yaml
# docker-compose.yml (Erweiterung)
services:
  # ... bestehende VALEO-Services (postgres, redis, nats, keycloak, app) ...

  superglue:
    image: superglueai/superglue:latest
    ports:
      - "3010:3001"    # Web Dashboard (remapped, da 3001 = VALEO-Frontend)
      - "3011:3000"    # GraphQL API
      - "3012:3002"    # REST API
    environment:
      SUPERGLUE_AUTH_TOKEN: "${SUPERGLUE_AUTH_TOKEN}"
      GRAPHQL_PLAYGROUND: "false"           # Prod: kein Playground
      DATABASE_URL: "postgresql://${SG_DB_USER}:${SG_DB_PASS}@superglue-db:5432/superglue"
      ENCRYPTION_KEY: "${SG_ENCRYPTION_KEY}"
      # LLM Provider (für Transform-Pipeline)
      LLM_PROVIDER: "anthropic"
      LLM_MODEL_ID: "claude-sonnet-4-6"
      ANTHROPIC_API_KEY: "${ANTHROPIC_API_KEY}"
    depends_on:
      superglue-db:
        condition: service_healthy
    networks:
      - valeo-internal
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  superglue-db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: superglue
      POSTGRES_USER: "${SG_DB_USER}"
      POSTGRES_PASSWORD: "${SG_DB_PASS}"
    volumes:
      - superglue-pgdata:/var/lib/postgresql/data
    networks:
      - valeo-internal
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${SG_DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  superglue-minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: "${SG_MINIO_USER}"
      MINIO_ROOT_PASSWORD: "${SG_MINIO_PASS}"
    volumes:
      - superglue-minio-data:/data
    networks:
      - valeo-internal
    # Kein externer Port — nur intern erreichbar

volumes:
  superglue-pgdata:
  superglue-minio-data:

networks:
  valeo-internal:
    # Superglue hat keinen direkten Internetzugang.
    # Egress wird über Proxy/Network-Policy gesteuert.
```

### 7.3 Warum eigenständiger Container statt tieferer Integration

| Kriterium | Eigenständig (empfohlen) | Tief integriert |
|-----------|--------------------------|-----------------|
| **Update-Zyklus** | Unabhängig — `docker pull` genügt | Gekoppelt an VALEO-Release |
| **Lizenz-Isolation** | FSL-1.1 bleibt in eigenem Container, kein Source-Merge | Lizenz-Kontamination möglich |
| **Fehler-Isolation** | Superglue-Crash betrifft nur Integrationen, nicht ERP-Kern | Shared-Process-Risk |
| **Ressourcen** | Eigene CPU/RAM-Limits | Konkurriert mit VALEO-Backend |
| **Security Boundary** | Eigene Network Policy, eigene DB, eigene Credentials | Shared Attack Surface |
| **Debugging** | Eigene Logs, eigenes Health-Endpoint | Vermischte Logs |

### 7.4 Netzwerk-Architektur

```
┌─────────────────────────────────────────────────────────────┐
│  valeo-internal network                                      │
│                                                              │
│  ┌──────────┐    GraphQL (3011)    ┌──────────────────┐     │
│  │  VALEO   │ ──────────────────→  │    superglue     │     │
│  │ Backend  │    REST (3012)       │  (Black Box)     │     │
│  │ (8000)   │ ──────────────────→  │                  │     │
│  └──────────┘                      └────────┬─────────┘     │
│       │                                     │               │
│       │                              ┌──────┴──────┐        │
│       │                              │ superglue-db│        │
│       │                              │ (pg:5432)   │        │
│  ┌────┴─────┐                        └─────────────┘        │
│  │ valeo-db │                                               │
│  │ (pg:5432)│    ← getrennte Datenbanken!                   │
│  └──────────┘                                               │
│                                                              │
│  Egress: nur über Proxy / Network Policy                     │
└─────────────────────────────────────────────────────────────┘

Extern erreichbar (via Reverse Proxy / Traefik):
  - VALEO Frontend:     Port 3001 → Endbenutzer
  - VALEO Backend API:  Port 8000 → Endbenutzer + Agenten
  - Superglue Dashboard: Port 3010 → nur Admin (IP-Whitelist / VPN)
  - Superglue GraphQL:   Port 3011 → nur VALEO Backend (nicht extern!)
  - Superglue REST:      Port 3012 → nur VALEO Backend (nicht extern!)
```

---

## 8. VALEO Adapter-Layer — Ist-Stand und Zielstruktur

### 8.1 Bereits implementiert (Stand 2026-04-04)

Die gesamte Grundstruktur ist produktionsreif vorhanden:

```
app/integrations/
├── ports/
│   ├── document_port.py           ✅ DocumentPort ABC + DocumentMetadata
│   └── partner_adapter_port.py    ✅ PartnerAdapterPort ABC + PartnerPreview
├── contracts/
│   ├── types.py                   ✅ IntegrationProviderKey, ExecutionMode, TargetKind,
│   │                                 AuthModel, ResultStatus, SuperglueToolRecord
│   └── result_envelope.py         ✅ ExternalResultEnvelope + ExternalResultError
│                                     (tenant_id, correlation_id, cost_cents, schema_version)
├── adapters/superglue/
│   ├── client.py                  ✅ SuperglueClient (REST + GraphQL, Circuit Breaker,
│   │                                 Outbound Security via validate_outbound_http_target,
│   │                                 Retry, SUPERGLUE_ALLOWED_HOSTS/DOMAINS)
│   ├── tool_sync.py               ✅ GraphQL-Katalog-Sync → SuperglueToolRecord,
│   │                                 Snapshot-Persistenz, Health/Status/Config-Summary
│   ├── document_adapter.py        ✅ SuperglueDocumentAdapter implements DocumentPort
│   └── edi_adapter.py             ✅ SupergluePartnerPreviewAdapter implements PartnerAdapterPort
├── services/
│   ├── superglue_execution_service.py  ✅ Tool-Execution → ExternalResultEnvelope,
│   │                                      Quarantine bei Fehler, Security-Observer-Logging
│   ├── superglue_capability_service.py ✅ Bridge Neuro Broker → Superglue (can_handle + execute_step)
│   ├── superglue_secret_resolver.py    ✅ Tenant-spezifische Auth-Token-Aufloesung
│   │                                      (SUPERGLUE__TENANT__{id}__AUTH_TOKEN Hierarchie)
│   ├── superglue_quarantine.py         ✅ Append-only JSONL Quarantine-Log
│   └── integration_circuit_breaker.py  ✅ In-Memory Circuit Breaker (closed/open/half_open)
```

**API-Endpoints** (`app/api/v1/endpoints/external_agent_integrations.py`):
- `GET  /agent/integrations` — Gesamtkatalog
- `GET  /agent/integrations/providers` — Provider-Liste
- `GET  /agent/integrations/providers/superglue/tools` — Gemappte Tools
- `GET  /agent/integrations/providers/superglue/sync-status` — Sync-Status
- `GET  /agent/integrations/providers/superglue/health` — Health-Check
- `GET  /agent/integrations/providers/superglue/config-summary` — Konfiguration
- `POST /agent/integrations/providers/superglue/sync-status/refresh` — Snapshot aktualisieren
- `GET  /agent/integrations/providers/superglue/quarantine` — Quarantine-Eintraege

**Config** (`app/core/config.py`):
- `SUPERGLUE_ENABLED`, `SUPERGLUE_SYNC_ENABLED`, `SUPERGLUE_EXECUTION_ENABLED` — 3-Stufen Feature Gate
- `SUPERGLUE_BASE_URL`, `SUPERGLUE_GRAPHQL_URL`, `SUPERGLUE_REST_URL`, `SUPERGLUE_DASHBOARD_URL`
- `SUPERGLUE_AUTH_TOKEN`, `SUPERGLUE_REQUIRE_TENANT_SECRETS`
- `SUPERGLUE_ALLOWED_HOSTS`, `SUPERGLUE_ALLOWED_DOMAINS` — Egress-Allowlists
- `SUPERGLUE_TIMEOUT_SECONDS`, `SUPERGLUE_SYNC_STATE_PATH`, `SUPERGLUE_QUARANTINE_LOG_PATH`

**Tests** (10 Testdateien):
- `test_superglue_client.py`, `test_superglue_contracts.py`, `test_superglue_tool_sync.py`
- `test_superglue_document_adapter.py`, `test_superglue_partner_preview.py`
- `test_superglue_secret_resolver.py`, `test_superglue_broker_integration.py`
- `test_superglue_refresh_and_quarantine.py`
- `test_process_kernel_wave86_external_integrations.py`
- `test_process_kernel_wave88_external_agent_integrations.py`

### 8.2 Umsetzungsstand der Risiko-Korrekturen

| Korrektur | Status | Nachweis |
|-----------|--------|----------|
| Kein eigener Orchestrator | ✅ Umgesetzt | `SuperglueCapabilityService` ist Bridge, kein Orchestrator. Aufrufe laufen über Neuro Broker. |
| Kein eigener Tool-Katalog | ✅ Umgesetzt | `tool_sync.py` synchronisiert in `SuperglueToolRecord`, integriert über `ExternalAgentIntegrationManifest`. |
| Outbound Security | ✅ Umgesetzt | `client.py` nutzt `validate_outbound_http_target_against_allowlists()` mit `SUPERGLUE_ALLOWED_HOSTS/DOMAINS`. |
| Tenant-Isolation | ✅ Umgesetzt | `superglue_secret_resolver.py` liest tenant-spezifische Tokens (`SUPERGLUE__TENANT__{id}__AUTH_TOKEN`). Prod erzwingt `SUPERGLUE_REQUIRE_TENANT_SECRETS=true`. |
| Circuit Breaker | ✅ Umgesetzt | `IntegrationCircuitBreaker` (closed/open/half_open) im `SuperglueClient`. |
| Cost Tracking | ✅ Umgesetzt | `ExternalResultEnvelope.cost_cents` Feld vorhanden. |
| Schema Versioning | ✅ Umgesetzt | `schema_version` in `SuperglueToolRecord`, `ExternalResultEnvelope` und allen Status-Modellen. |
| Quarantine/DLQ | ✅ Umgesetzt | `superglue_quarantine.py` — Append-only JSONL-Log mit Summary-API. |
| Security Observability | ✅ Umgesetzt | `security_observer.record_event()` bei jeder Execution (success + degraded). |

### 8.3 Verbleibende Lücken (Zielstruktur)

```
app/integrations/
├── ports/
│   └── external_api_port.py       ❌ FEHLT — Generischer typed API-Call Port
├── adapters/
│   └── native/                    ❌ FEHLT — Bestehende Direktadapter (Paperless, BrightSky,
│                                     Twilio) noch nicht als Port-Implementierungen refactored
```

| Lücke | Priorität | Empfehlung |
|-------|-----------|------------|
| `external_api_port.py` | Mittel | Bei erstem generischen API-Anwendungsfall (z.B. BayWa) einführen |
| Native Adapter als Port-Implementierungen | Niedrig | Paperless, BrightSky, Twilio nur refactoren wenn konkret benötigt |
| Event-Integration (Outbox) | Mittel | `SuperglueExecutionService` Ergebnisse als `IntegrationEvent` über Outbox publizieren |
| Docker-Compose Erweiterung | Hoch | Superglue-Container + DB + MinIO aufsetzen (siehe Abschnitt 7.2) |

---

## 9. Funktionserhalt von superglue nach Risiko-Korrekturen

**Zentrale Antwort: Ja, alle 4 Risiko-Korrekturen erhalten superglue's Funktionalität vollständig.**

| Korrektur | Was ändert sich bei superglue? | Funktionalität erhalten? |
|-----------|-------------------------------|--------------------------|
| Kein eigener Orchestrator | Nichts. VALEO ruft superglue's GraphQL/REST-API auf. Superglue's interne Worker Pools, Retry, Transform-Pipeline bleiben unverändert. | Ja |
| Kein eigener Tool-Katalog | Nichts. VALEO liest superglue's Katalog per GraphQL und spiegelt ihn ins eigene Manifest. Superglue verwaltet seine Tools weiter intern. | Ja |
| Outbound Security / Egress | Docker Network Policy begrenzt, welche externen Hosts superglue erreichen darf. Kein Code-Eingriff in superglue. Operations-Konfiguration. | Ja |
| Tenant-Isolation | VALEO-Adapter injiziert tenant-spezifische Credentials in jeden Call. Superglue sieht verschiedene API-Keys pro Tenant — funktioniert wie Multi-User nativ. | Ja |

**Superglue wird als unmodifiziertes Docker-Image (`superglueai/superglue:latest`) betrieben.** Alle Anpassungen liegen im VALEO Adapter-Layer und in der Docker/Network-Konfiguration. Kein Fork nötig.

### 9.1 Implementierungsnachweis

Alle Korrekturen sind bereits im Code umgesetzt (siehe Abschnitt 8.2). Die VALEO-seitige Integration greift an keiner Stelle in superglue's Source Code ein:

- **`SuperglueClient`** nutzt superglue's Standard-REST/GraphQL-Endpunkte (`/health`, `/api/tools/{id}/execute`, GraphQL `tools` Query)
- **`tool_sync.py`** liest den Katalog per GraphQL und mappt in VALEO's `SuperglueToolRecord` — superglue's internes Tool-Management bleibt unberührt
- **`superglue_secret_resolver.py`** löst Credentials pro Tenant auf und injiziert sie als Bearer-Token — superglue's eigenes Auth-Modell bleibt erhalten
- **Outbound-Validierung** passiert im VALEO-Client vor dem HTTP-Call — superglue sieht nur den validierten Request

---

## 10. Rollout-Phasen

### Phase 1: Controlled Edge (Wochen 1–4)
- Superglue Docker-Container aufsetzen (docker-compose Erweiterung)
- `app/integrations/ports/` und `adapters/superglue/client.py` implementieren
- Erste Anbindung: Ein Nicht-Paperless-DMS (z.B. SharePoint) über superglue
- Execution Mode: nur `read`
- Monitoring: Health-Check, Latenz-Logging

### Phase 2: HITL Actions (Wochen 5–8)
- EDI-Partner-Anbindung über superglue (EDIFACT abstrahiert)
- Execution Modes: `read` + `suggest` + `simulate`
- Tool-Sync: superglue Tools → VALEO Agent Manifest
- NeuroASSIST `operations_exception_assistant` kann superglue-Tools als Capability nutzen
- Human-in-the-Loop über `approval_gate`

### Phase 3: Controlled Execution (Wochen 9–12)
- Execution Mode: `execute` (mit Policy Gate + Audit Trail)
- Circuit Breaker + Cost Tracking aktiv
- Event-Integration: Ergebnisse als `IntegrationEvent` über Outbox-Publisher
- Admin-Link in VALEO (`/admin/integrations` → superglue Dashboard)
- Zweite/dritte Anbindung: z.B. BayWa-Schnittstelle, FMIS-Connector

---

## 11. Offene Entscheidungen

| # | Frage | Empfehlung | Entscheider |
|---|-------|------------|-------------|
| 1 | LLM-Provider für superglue Transform-Pipeline | Anthropic Claude Sonnet 4.6 (konsistent mit VALEO) | Architektur |
| 2 | Superglue Enterprise vs. Community Edition | Community zunächst ausreichend (kein Cron, kein User-Mgmt nötig in Phase 1–2) | Produkt |
| 3 | MinIO vs. bestehender S3/Blob-Storage | MinIO für superglue-interne Nutzung; VALEO-Dateien bleiben in Paperless | Ops |
| 4 | Superglue-Credential-Vault Integration | Eigener `ENCRYPTION_KEY` zunächst; später ggf. HashiCorp Vault | Security |
| 5 | Monitoring-Integration | Superglue-Logs nach Grafana Loki; Health in bestehende Alerts | Ops |

---

## 12. Anti-Patterns (aus dem Vorschlag übernommen + ergänzt)

1. **Kein superglue-Call ohne Adapter Contract** — auch nicht für „schnelle" Anbindungen
2. **Keine Business-Logik in superglue Transforms** — Transforms nur für Datenformat-Konvertierung
3. **Kein direkter superglue-Zugriff aus dem Frontend** — immer über VALEO Backend
4. **Kein Shared-DB-Zugriff** — superglue und VALEO haben getrennte Datenbanken
5. **Kein Chat-Channel-Merge** — superglue-Chat nur für Admins, NeuroASSIST für Fachbenutzer
6. **Kein superglue-Fork** — unmodifiziertes Image, alle Anpassungen im VALEO Adapter-Layer
7. **Keine superglue-Abhängigkeit im kritischen Pfad** — ERP-Kernprozesse (Annahme, Settlement, Faktura) dürfen nicht an superglue-Verfügbarkeit gebunden sein

---

## Referenzen

- [ADR-014 Integrationsgrenzen](../adr/adr-014-integrationsgrenzen-api-edi-mcp-partneradapter.md)
- [ADR-007 Agent-Tool-Contract-Governance](../adr/adr-007-agent-tool-contract-governance.md)
- [NeuroASSIST Target Architecture](neuroassist-target-architecture.md)
- [Target State Landhandel ERP](target-state-landhandel-erp.md)
- [superglue GitHub](https://github.com/superglue-ai/superglue)
- [superglue Lizenz: FSL-1.1-Apache-2.0](https://github.com/superglue-ai/superglue/blob/main/LICENSE)
