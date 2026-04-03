# Superglue Integration - Implementierungsplan

**Status:** Planungsgrundlage / umsetzungsnah
**Datum:** 2026-04-03
**Baut auf:** [superglue-integration-bewertung.md](./superglue-integration-bewertung.md), [ADR-014](../adr/adr-014-integrationsgrenzen-api-edi-mcp-partneradapter.md), [ADR-007](../adr/adr-007-agent-tool-contract-governance.md)

## 1. Ziel

Superglue wird als isolierter Integrationsdienst hinter der VALEO Integration Boundary betrieben. Es uebernimmt externe Konnektivitaet, Mapping und Tool-Execution gegen Fremdsysteme. VALEO behaelt die Hoheit ueber:

- Business-Logik
- Command-/Action-Boundary
- Policy / Approval / HITL
- Tenant-Isolation
- Audit / Security / Observability

Superglue ist damit:

- **kein** zweiter Orchestrator
- **keine** zweite Tool-Registry
- **kein** direkter Frontend-Backend-Ersatz
- **kein** Speicherort fuer fachliche Geschaeftslogik

## 2. Leitprinzipien

1. Ein Integrationspfad, ein Owner, eine Source of Truth.
2. Alle produktiven Superglue-Aufrufe laufen durch einen VALEO-Adapter-Layer.
3. Alle produktiven Aufrufe tragen `tenant_id`, `correlation_id`, `schema_version`.
4. Externe Execution-Modi folgen der vorhandenen Governance:
   - `read`
   - `suggest`
   - `simulate`
   - `execute`
5. `execute` ist nie ein Direktpfad, sondern laeuft durch bestehende Approval-/Policy-/Audit-Gates.
6. Keine Typduplikate zwischen `core`, `api`, `agents`, `integrations`.

## 3. Architekturgrenzen

### 3.1 Was in VALEO bleibt

- Agent-/Tool-Governance
- Command Boundary
- Process-/Stage-Orchestrierung
- Security / SSRF / Tenant-Isolation
- Audit und Decision Trace
- Outbox / Events / Read Models

### 3.2 Was Superglue uebernimmt

- Konnektivitaet zu Fremdsystemen
- Connector-/Tool-Konfiguration
- Datenformat-Konvertierung
- interne Retry-/Worker-Mechanik
- Drift Detection gegen externe APIs

### 3.3 Was explizit verboten ist

- Business-Logik in Superglue-Transforms
- direkte Frontend-Aufrufe an Superglue
- Shared DB zwischen VALEO und Superglue
- zweite produktive Tool-Registry ausserhalb der bestehenden Manifeste
- Umgehung von `outbound_security.py`

## 4. Benennungen und Source of Truth

### 4.1 Provider-Key

Verbindlich:

- `provider_key = "superglue"`

Nicht verwenden:

- `super_glue`
- `sg`
- `superglue_ai`
- `integration_platform`

### 4.2 Settings / Environment Variablen

Verbindlich nur ein Praefix:

- `SUPERGLUE_`

Nicht parallel einfuehren:

- `SG_*`
- `INTEGRATION_SUPERGLUE_*`

Empfohlene Settings in `app/core/config.py`:

- `SUPERGLUE_ENABLED: bool = False`
- `SUPERGLUE_BASE_URL: Optional[str] = None`
- `SUPERGLUE_GRAPHQL_URL: Optional[str] = None`
- `SUPERGLUE_REST_URL: Optional[str] = None`
- `SUPERGLUE_DASHBOARD_URL: Optional[str] = None`
- `SUPERGLUE_AUTH_TOKEN: Optional[str] = None`
- `SUPERGLUE_TIMEOUT_SECONDS: float = 10.0`
- `SUPERGLUE_PROVIDER_KEY: str = "superglue"`
- `SUPERGLUE_ALLOWED_HOSTS: List[str] = []`
- `SUPERGLUE_ALLOWED_DOMAINS: List[str] = []`
- `SUPERGLUE_SYNC_ENABLED: bool = False`
- `SUPERGLUE_EXECUTION_ENABLED: bool = False`

### 4.3 Typquellen

Neue Typen werden genau einmal definiert:

- `app/integrations/contracts/types.py`
- `app/integrations/contracts/result_envelope.py`

Dort hinein:

- `IntegrationProviderKey`
- `IntegrationExecutionMode`
- `IntegrationTargetKind`
- `IntegrationAuthModel`
- `SuperglueToolRecord`
- `ExternalResultEnvelope`

Nicht erneut definieren in:

- `app/core/external_agent_catalog.py`
- `app/services/neuro_tool_execution.py`
- `app/api/v1/endpoints/*`
- Frontend-API-Clients

### 4.4 Dateinamen

Verbindliche Zielstruktur:

```text
app/
  integrations/
    contracts/
      __init__.py
      types.py
      result_envelope.py
    ports/
      __init__.py
      document_port.py
      partner_edi_port.py
      external_api_port.py
    adapters/
      __init__.py
      native/
        __init__.py
      superglue/
        __init__.py
        client.py
        tool_sync.py
        document_adapter.py
        edi_adapter.py
    services/
      __init__.py
      superglue_execution_service.py
      superglue_capability_service.py
      integration_circuit_breaker.py
```

Nicht einfuehren:

- `integration-orchestrator.py`
- `superglue_registry.py`
- `superglue_manifest.py`
- `superglue_types.py` an mehreren Stellen

## 5. Integrationsfluss

### 5.1 Read / Suggest / Simulate

```text
Neuro Tool Broker / Command Boundary
  -> VALEO Superglue Capability Service
  -> VALEO Superglue Client
  -> Superglue GraphQL/REST
  -> ExternalResultEnvelope
  -> Audit / Monitoring / optional Event
```

### 5.2 Execute

```text
Neuro Tool Broker
  -> Policy / Approval / Verification
  -> Superglue Execution Service
  -> Superglue Client
  -> ExternalResultEnvelope
  -> Audit + Outbox/Event + Security Observability
```

## 6. Manifest- und Registry-Regeln

### 6.1 Bestehende Artefakte bleiben

- `ExternalAgentIntegrationManifest` in `app/core/external_agent_catalog.py`
- `AgentCommandManifest` in `app/core/agent_command_manifest.py`
- vorhandene Tool-/Contract-Manifestpfade

### 6.2 Superglue-Tools

Superglue-Tools werden nicht in einer neuen Registry gepflegt. Stattdessen:

1. `tool_sync.py` liest den Superglue-Katalog.
2. Relevante Tools werden auf VALEO-Sicht gemappt.
3. Die Provider-Sicht bleibt in `external_agent_catalog.py`.
4. Produktive Execution laeuft ueber VALEO-Contracts, nicht ueber rohe Superglue-Toolnamen.

### 6.3 Drift vermeiden

Ein Sync-Datensatz pro Tool:

- `provider_key`
- `external_tool_id`
- `external_tool_version`
- `valeo_contract_id`
- `schema_version`
- `last_synced_at`

## 7. Security-, Tenant- und Audit-Regeln

### 7.1 SSRF / Egress

Jeder Superglue-Zielhost wird vor Nutzung ueber `validate_outbound_http_target()` geprueft. Zusätzlich:

- Container-Egress via Network Policy / Proxy begrenzen
- keine freien Dashboard-/Connector-Ziele ohne Allowlist

### 7.2 Tenant-Isolation

Pflichtfelder in jedem produktiven Contract:

- `tenant_id`
- `correlation_id`
- `requesting_user_id` oder `actor_id`

Pflichtregeln:

- keine Shared Credentials fuer produktive Tenant-Daten
- Credential-Aufloesung pro Tenant
- `tenant_id` auch im Result Envelope

### 7.3 Audit

Jeder produktive Call erzeugt:

- Request-Metadaten
- Ausfuehrungsmodus
- Provider-Key
- External Result Envelope
- Fehlerklasse / Retry-Status
- Kostenmetrik

## 8. Reibpunkte und Gegenmassnahmen

| Reibpunkt | Risiko | Gegenmassnahme |
|-----------|--------|----------------|
| Doppel-Orchestrierung | unklare Verantwortung zwischen Neuro und Superglue | kein eigener Orchestrator, nur Capability-/Execution-Service |
| Typdrift | gleiche Begriffe mit abweichender Semantik | alle Integrations-Typen zentral in `contracts/` |
| Doppel-Katalog | Superglue-Registry driftet gegen VALEO-Manifest | nur Sync, keine zweite Registry |
| SSRF-Bypass | Superglue umgeht zentrale Egress-Regel | Adapter + Network Policy |
| Tenant-Leakage | cross-tenant Credentials oder Responses | Tenant-Pflichtfelder, per-tenant Secret-Aufloesung |
| Audit-Luecke | externe Actions nicht nachvollziehbar | Result Envelope + Audit Bridge |
| Frontend-Bypass | Admin/Fach-UI spricht Superglue direkt an | nur Backend-Link / Backend-Proxy |
| Business-Logik-Drift | Mapping-Logik wandert in Superglue | Transforms nur technisch, nie fachlich |

## 9. Rollout-Reihenfolge

### INT-SG-001 - Contract- und Settings-Basis

Ziel:

- zentrale Typen
- Ergebnis-Envelope
- Superglue-Settings

Dateibesitz:

- `app/integrations/contracts/**`
- `app/core/config.py`

### INT-SG-002 - Superglue Client + Egress Guard

Ziel:

- reiner Transportclient
- URL-/Host-Validation
- Timeout/Retry-Basis

Dateibesitz:

- `app/integrations/adapters/superglue/client.py`
- `app/core/outbound_security.py`
- `app/integrations/services/integration_circuit_breaker.py`

### INT-SG-003 - Provider-/Manifest-Sync

Ziel:

- `provider_key="superglue"` in bestehender Provider-Sicht
- Tool-Sync in VALEO-Manifestwelt

Dateibesitz:

- `app/integrations/adapters/superglue/tool_sync.py`
- `app/core/external_agent_catalog.py`
- `app/api/v1/endpoints/external_agent_integrations.py`

### INT-SG-004 - Neuro Broker / Execution Integration

Ziel:

- Superglue als Provider im bestehenden Tool-Broker
- keine Parallel-Orchestrierung

Dateibesitz:

- `app/integrations/services/superglue_execution_service.py`
- `app/integrations/services/superglue_capability_service.py`
- `app/services/neuro_tool_broker.py`
- `app/services/neuro_tool_execution.py`

### INT-SG-005 - Deployment / Ops / Admin-Link

Ziel:

- docker-compose-Erweiterung
- abgesicherte Dashboard-Erreichbarkeit
- Admin-Link statt Embedding

Dateibesitz:

- `docker-compose*.yml`
- Admin-Doku
- optional Admin-Frontend-Link

### INT-SG-006 - Erste reale Fachanbindung

Ziel:

- eine kontrollierte Pilotintegration

Empfehlung Reihenfolge:

1. DMS ausserhalb Paperless
2. einfacher Legacy-/Partneradapter
3. erst danach agentische Execution gegen produktive Systeme

## 10. Nicht-Ziele fuer Phase 1

- kein Superglue-Fork
- kein Chat-Merge mit NeuroASSIST
- kein iframe im VALEO-Frontend
- keine direkte produktive Write-Integration ohne Approval-/Policy-Gates
- keine gemeinsame DB

## 11. Abnahme fuer den Gesamtpfad

Die Integration gilt erst dann als sauber vorbereitet, wenn:

- alle Typen zentralisiert sind
- Settings ohne Dopplung eingefuehrt sind
- Provider-/Manifest-Sicht nicht driftet
- SSRF-/Tenant-/Audit-Regeln im Adapter-Layer erzwungen werden
- mindestens eine Pilotanbindung durch denselben Standardpfad laeuft

## 12. Verweise

- [Superglue Integrationsbewertung](./superglue-integration-bewertung.md)
- [ADR-014 Integrationsgrenzen](../adr/adr-014-integrationsgrenzen-api-edi-mcp-partneradapter.md)
- [ADR-007 Agent-Tool-Contract-Governance](../adr/adr-007-agent-tool-contract-governance.md)
- [AGENT-INTEGRATION.md](../AGENT-INTEGRATION.md)
