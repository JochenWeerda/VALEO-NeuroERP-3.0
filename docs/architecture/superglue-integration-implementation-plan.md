# Superglue Integration - Implementierungsplan

**Status:** in Umsetzung, Basispfade INT-SG-001 bis INT-SG-066 umgesetzt
**Datum:** 2026-04-06
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

### 2.1 Upstream-First-Regel

Fuer alle offenen Superglue-Folge-Slices ab `INT-SG-043` gilt verbindlich:

1. Upstream zuerst uebernehmen, nicht lokal nachbauen.
2. VALEO ergaenzt Superglue nur um Tenant-Isolation, Secret-/Vault-Resolution, Broker-/Approval-/Policy-Gates, Audit, Monitoring und Admin-Surface.
3. Wenn Upstream bereits API, Payload-Shape, Run-Semantik, Self-Host-Konvention oder Datenmodell liefert, wird dieser Pfad 1:1 oder als duenne Wrapper-Schicht uebernommen.
4. Neue VALEO-Strukturen sind nur zulaessig, wenn sie fachlich oder governance-seitig zwingend VALEO-spezifisch sind.
5. Keine parallele Re-Implementierung von Tool-CRUD, Run-Status-Logik, System-/Credential-Modellen oder Self-Host-/Runtime-Konventionen.

Merksatz:

- Superglue liefert Integrationsfunktionalitaet.
- VALEO liefert Governance, Tenanting und Fachkontext.

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

Aktueller Stand 2026-04-03:

- `INT-SG-001` bis `INT-SG-008` sind als Basis-MVP im Repo umgesetzt.
- Offen bleiben produktive Connector-Konfiguration, tenant-spezifische Secret-Bestueckung und ein erster echter Live-Connector.

Folgewelle 2026-04-04:

- `INT-SG-009` bis `INT-SG-014` sind als Folgewelle umgesetzt: Sync-Snapshot, Config-Summary, Quarantaene, Audit-/Security-Bridge, zweiter Preview-Adapter und Admin-UX.
- `INT-SG-015` bis `INT-SG-020` sind umgesetzt: Execution-Guardrails, Sync-History, Resolve-Pfad fuer Quarantaene, Execution-Journal, dritter read-only Pilotadapter und Admin-UX-Nachzug.
- `INT-SG-021` ist umgesetzt: Compose-Stack fuer Superglue mit eigener DB, MinIO, Init-Job, Volumes und Healthchecks.
- `INT-SG-022` ist umgesetzt: Reverse-Proxy-Overlay mit TLS-Endpunkten, internen Service-Ports und Header-Hardening.
- `INT-SG-023` bis `INT-SG-028` sind umgesetzt: Kubernetes-Basis, Helm-Overlay, NetworkPolicy/Ingress, Backup/Restore, CI-Validierung und wiederholbare Ops-Scripts.
- `INT-SG-029` bis `INT-SG-034` sind umgesetzt: ArgoCD, Secret-/Certificate-CRDs, Prometheus/Grafana, dedizierter Deploy-Workflow und Bootstrap der tenant-spezifischen Ops-Konfiguration.
- `INT-SG-035` bis `INT-SG-040` sind umgesetzt: aktueller Self-Host-Runtime-Contract, `/v1`-REST- und Run-Mapping, read-only Tool-Bootstrap, lokaler Runtime-Smoke gegen den echten Upstream-Container und Zielstruktur-/Doku-Alignment.
- `INT-SG-041` ist umgesetzt: kanonische Pilot-Tools werden per REST reproduzierbar provisioniert, `GET /v1/tools` liefert im frischen Stack echte Eintraege, und ein echter `POST /v1/tools/{toolId}/run`-Smoke ist gegen den lokalen Upstream-Container nachgewiesen.
- `INT-SG-042` ist umgesetzt: der lokale In-App-Pfad ueber `SuperglueClient` kann fuer Dev-Smokes jetzt explizit loopback-freigegeben werden, ohne die produktive SSRF-/Egress-Policy fuer interne Hosts oder private Netze aufzuweichen.
- `INT-SG-043` bis `INT-SG-048` sind umgesetzt: tenant-spezifischer Connector-Bootstrap, connector-scoped Secret-Resolution, tenant-spezifische Tool-/Lifecycle-Summaries, zentral normalisierte Run-Ergebnisse sowie tenant-gebundene DMS- und Partner-EDI-Adapter sind im VALEO-Superglue-Pfad integriert.
- `INT-SG-049` bis `INT-SG-060` sind umgesetzt: CRM-/Masterdata-Read, Artifact-/Idempotenz-/Retry-Pfade, Admin-/Monitoring-/CI-Surfaces sowie Procurement-, Finance-, Logistics-, Agribusiness-, Service- und Analytics-Rollouts liegen jetzt als thin-wrapper Connector-Familien im VALEO-Superglue-Pfad vor.
- `INT-SG-061` ist umgesetzt: tenant-spezifische Live-Readiness surfact fehlende Credentials, Platzhalter-Zielsysteme sowie environment-spezifische Alerting-/Retention-Policies jetzt direkt als API- und Admin-Sicht.
- `INT-SG-062` ist umgesetzt: ein expliziter Tenant-Onboarding-Pack exportiert jetzt Secret-Key-Kandidaten, Zielsystem-Felder und Policy-Werte fuer Ops je Environment.
- `INT-SG-063` bis `INT-SG-066` sind umgesetzt: CLI-/Shell-Exports, ENV-/Vault-Templates, CI-Validierung und direkte Admin-Downloads schliessen die letzten implementierbaren Superglue-Ops-Pfade.

Folge-Rollout ab `INT-SG-043`:

- **Phase 1 - Produktionsfaehiger Kern:** `INT-SG-043` bis `INT-SG-046`
- **Phase 2 - Echte Referenz-Connectoren:** `INT-SG-047` bis `INT-SG-050`
- **Phase 3 - Governance fuer reale Write-Pfade:** `INT-SG-051` bis `INT-SG-053`
- **Phase 4 - Admin- und Betriebsreife:** `INT-SG-054` bis `INT-SG-056`
- **Phase 5 - Optionaler breiter Domänen-Rollout:** `INT-SG-057` bis `INT-SG-060`

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

### INT-SG-007 - Tenant-Secret-Resolution

Ziel:

- tenant-spezifische Credential-Aufloesung fuer Superglue
- kein Shared Token im produktiven Multi-Tenant-Betrieb

Dateibesitz:

- `app/integrations/services/superglue_secret_resolver.py`
- `app/services/secrets_vault.py`
- `app/core/config.py`

### INT-SG-008 - Sync- und Health-Observability

Ziel:

- Sync-Status und Provider-Health fuer Superglue surfacen
- Admin-Sicht auf Tool-Sync, letzte Fehler und Dashboard-Link

Dateibesitz:

- `app/integrations/adapters/superglue/tool_sync.py`
- `app/api/v1/endpoints/external_agent_integrations.py`
- optional Admin-Frontend fuer Statusanzeige

### INT-SG-009 - Sync-Snapshot-Persistenz und Refresh

Ziel:

- letzten Sync-Stand ausserhalb des Prozessspeichers halten
- manuellen Refresh-Trigger fuer Admins anbieten

Dateibesitz:

- `app/integrations/adapters/superglue/tool_sync.py`
- `app/api/v1/endpoints/external_agent_integrations.py`
- `app/core/config.py`

### INT-SG-010 - Config-Summary und Admin-Aktionspfad

Ziel:

- lesbare, maskierte Superglue-Konfigurationssicht
- Admin-Seite fuer Refresh/Status/naechste Schritte erweitern

Dateibesitz:

- `app/api/v1/endpoints/external_agent_integrations.py`
- `packages/frontend-web/src/pages/admin/agenten-integration.tsx`
- Frontend-Test

### INT-SG-011 - Superglue-Quarantaene

Ziel:

- degradierte/fallbackende Superglue-Aufrufe als Quarantaene-Eintraege festhalten
- Admin-Sicht auf letzte Faelle

Dateibesitz:

- `app/integrations/services/superglue_quarantine.py`
- `app/integrations/services/superglue_execution_service.py`
- `app/api/v1/endpoints/external_agent_integrations.py`

### INT-SG-012 - Audit-/Security-Bridge

Ziel:

- Superglue-Execution an Security-Observability und Audit-Metadaten anbinden

Dateibesitz:

- `app/integrations/services/superglue_execution_service.py`
- `app/services/security_observability.py`
- optional Audit-Bridge-Nutzung

### INT-SG-013 - Zweiter read-only Pilotadapter

Ziel:

- zweiten read-only Port fuer Partner-/Legacy-Preview liefern

Dateibesitz:

- `app/integrations/ports/partner_adapter_port.py`
- `app/integrations/adapters/superglue/edi_adapter.py`
- Tests

### INT-SG-014 - Admin-UX fuer Superglue-Operationen

Ziel:

- Refresh, Config-Hinweise und Quarantaene in der Admin-Seite surfacen

Dateibesitz:

- `packages/frontend-web/src/pages/admin/agenten-integration.tsx`
- `packages/frontend-web/src/__tests__/pages/admin/agenten-integration.test.tsx`

### INT-SG-015 - Execution-Guardrails gegen Tool-/Mode-Drift

Ziel:

- nur gemappte Superglue-Tools ausfuehren
- Execution-Modes pro Tool hart validieren
- keine freie Tool-ID-/Mode-Kombination aus Planpayloads

Dateibesitz:

- `app/integrations/adapters/superglue/tool_sync.py`
- `app/integrations/services/superglue_execution_service.py`
- `app/integrations/services/superglue_capability_service.py`
- `tests/test_superglue_execution_guardrails.py`

### INT-SG-016 - Sync-History und letzte Refreshes

Ziel:

- Refresh-Historie append-only festhalten
- letzte Sync-Laeufe im Admin-/API-Pfad surfacen

Dateibesitz:

- `app/integrations/adapters/superglue/tool_sync.py`
- `app/api/v1/endpoints/external_agent_integrations.py`
- `tests/test_superglue_refresh_and_quarantine.py`

### INT-SG-017 - Quarantaene Resolve / Ack

Ziel:

- Quarantaene-Eintraege nach Review als erledigt markieren
- offene vs. erledigte Faelle trennen

Dateibesitz:

- `app/integrations/services/superglue_quarantine.py`
- `app/api/v1/endpoints/external_agent_integrations.py`
- Frontend-Admin-Seite + Tests

### INT-SG-018 - Execution-Journal / Operations-Trail

Ziel:

- erfolgreiche und degradierte Superglue-Executions append-only protokollieren
- kompakte Summary fuer Ops/Admin bereitstellen

Dateibesitz:

- `app/integrations/services/superglue_execution_service.py`
- neuer Journal-Service unter `app/integrations/services/`
- API-/Admin-Summary

### INT-SG-019 - Dritter read-only Pilotadapter

Ziel:

- dritten read-only Port fuer externes Stammdaten-/CRM-Preview liefern
- denselben Standardpfad wie die bisherigen Pilotadapter nutzen

Dateibesitz:

- `app/integrations/ports/customer_profile_port.py`
- `app/integrations/adapters/superglue/customer_profile_adapter.py`
- Tests

### INT-SG-020 - Admin-UX Nachzug fuer History / Journal / Resolve

Ziel:

- Sync-History, Journal-Summary und Resolve-Aktion im Admin-Frontend surfacen
- keine direkte Connector-Bedienung, nur kontrollierte Ops-Funktionen

Dateibesitz:

- `packages/frontend-web/src/pages/admin/agenten-integration.tsx`
- `packages/frontend-web/src/__tests__/pages/admin/agenten-integration.test.tsx`

### INT-SG-021 - Compose-Stack fuer Superglue Ops

Ziel:

- separaten Superglue-Stack mit Postgres und MinIO belastbar bereitstellen
- Healthchecks, Volumes, internes Netz und Bucket-Init mitliefern
- keine harten Secrets in Compose selbst

Dateibesitz:

- `docker-compose.integration.yml`
- zugehoerige Ops-Doku unter `docs/workflows/` und `docs/cards/`

### INT-SG-022 - Edge-/Proxy-Overlay fuer Staging und Prod

Ziel:

- Reverse Proxy vor den Superglue-Stack setzen
- direkte extern veroeffentlichte Service-Ports im Overlay schliessen
- TLS-, Header- und Admin-Zugriffspfade sauber modellieren

Dateibesitz:

- `docker-compose.integration.edge.yml`
- `ops/superglue/Caddyfile`
- zugehoerige Doku unter `docs/workflows/` und `docs/cards/`

### INT-SG-023 - Kubernetes Basis-Manifeste

Ziel:

- denselben Superglue-Stack neben Compose auch als Cluster-Basis modellieren
- Services, Persistenz und Secret-/Config-Verkabelung sauber trennen
- keine zweite Naming-Welt neben `SUPERGLUE_*`

Dateibesitz:

- `k8s/superglue/**`
- zugehoerige Doku unter `docs/workflows/` und `docs/cards/`

### INT-SG-024 - Helm-Overlay im bestehenden Chart

Ziel:

- Superglue als optionale Komponente im bestehenden `valeo-erp`-Chart rendern
- vorhandene Label-, SecretRef- und Ressourcenmuster wiederverwenden
- keine zweite Chart-Welt nur fuer Superglue aufbauen

Dateibesitz:

- `k8s/helm/valeo-erp/values.yaml`
- `k8s/helm/valeo-erp/templates/superglue-*.yaml`
- zugehoerige Doku unter `docs/workflows/` und `docs/cards/`

### INT-SG-025 - NetworkPolicy und Ingress im K8s-Pfad

Ziel:

- interne und externe Superglue-Verkehrswege im Cluster begrenzen
- TLS-/Host-Pfade fuer API und MinIO-Konsole kontrolliert modellieren
- Compose- und K8s-Edge-Konventionen angleichen

Dateibesitz:

- `k8s/superglue/networkpolicy.yaml`
- `k8s/superglue/ingress.yaml`
- `k8s/helm/valeo-erp/templates/superglue-networkpolicy.yaml`
- `k8s/helm/valeo-erp/templates/superglue-ingress.yaml`
- zugehoerige Doku unter `docs/workflows/` und `docs/cards/`

### INT-SG-026 - Backup/Restore-Ops fuer DB und MinIO

Ziel:

- Postgres-Dump, Artefakt-Sync und Restore-Test fuer Superglue standardisieren
- Cron-/Job-Pfade in Helm und lokale Ops-Scripts angleichen
- Restore explizit pruefbar machen statt nur Backup-Dateien zu erzeugen

Dateibesitz:

- `k8s/helm/valeo-erp/templates/superglue-backup-*.yaml`
- `scripts/superglue/*.ps1`
- `scripts/superglue/*.sh`
- zugehoerige Doku unter `docs/workflows/` und `docs/cards/`

### INT-SG-027 - CI-Validierung fuer Infra-Pfade

Ziel:

- Compose-, K8s- und Helm-Renderpfade automatisiert pruefen
- Basis-Smokes fuer Ops-Scripts und Rendering in GitHub Actions verankern
- Drift zwischen lokaler Doku und deploybarer Konfiguration frueh erkennen

Dateibesitz:

- `.github/workflows/superglue-infra.yml`
- `scripts/superglue/*.ps1`
- `scripts/superglue/*.sh`
- zugehoerige Doku unter `docs/workflows/` und `docs/cards/`

### INT-SG-028 - Ops-Scripts und Runbook

Ziel:

- wiederholbare Start-, Deploy-, Smoke- und Drift-Checks fuer Superglue liefern
- Compose- und K8s-Pfade unter einem kleinen Script-Set dokumentieren
- keine manuellen Schrittlisten ohne automatisierbaren Gegenpfad offen lassen

Dateibesitz:

- `scripts/superglue/**`
- zugehoerige Doku unter `docs/workflows/` und `docs/cards/`

### INT-SG-029 - ArgoCD Application

Ziel:

- Superglue in den bestehenden GitOps-Pfad ziehen
- separates App-of-Apps-Artefakt statt manuellem `kubectl apply`

Dateibesitz:

- `k8s/argocd/apps/superglue-platform.yaml`
- `k8s/argocd/apps/kustomization.yaml`
- zugehoerige Doku unter `docs/workflows/` und `docs/cards/`

### INT-SG-030 - Secret- und Certificate-CRDs

Ziel:

- produktive Secret- und Zertifikatsquellen im K8s-Pfad modellieren
- `ExternalSecret`/`Certificate` nicht nur im Runbook erwaehnen, sondern als Artefakt ablegen

Dateibesitz:

- `k8s/superglue/external-secret.yaml`
- `k8s/superglue/certificate.yaml`
- `k8s/helm/valeo-erp/templates/superglue-external-secret.yaml`
- `k8s/helm/valeo-erp/templates/superglue-certificate.yaml`
- zugehoerige Doku unter `docs/workflows/` und `docs/cards/`

### INT-SG-031 - ServiceMonitor und Alerts

Ziel:

- Superglue-Metriken an bestehende Prometheus-Konventionen anbinden
- konkrete Alert-Regeln fuer Health, Sync und Quarantaene modellieren

Dateibesitz:

- `k8s/superglue/servicemonitor.yaml`
- `k8s/helm/valeo-erp/templates/superglue-servicemonitor.yaml`
- `k8s/helm/valeo-erp/templates/prometheus-alerts.yaml`
- zugehoerige Doku unter `docs/workflows/` und `docs/cards/`

### INT-SG-032 - Grafana Dashboard

Ziel:

- Superglue-Ops als standardisiertes Dashboard mit Health, Journal, Sync und Quarantaene surfacen
- Dashboard-Datei und Cluster-Einspielpfad sauber trennen

Dateibesitz:

- `ops/superglue/grafana-dashboard.json`
- `k8s/helm/valeo-erp/templates/superglue-dashboard-configmap.yaml`
- zugehoerige Doku unter `docs/workflows/` und `docs/cards/`

### INT-SG-033 - GitHub Deploy Workflow

Ziel:

- Superglue-Infra nicht nur rendern, sondern kontrolliert deploybar machen
- Staging/Main-Pfade und Artefakte trennen

Dateibesitz:

- `.github/workflows/superglue-deploy.yml`
- `scripts/superglue/*.ps1`
- `scripts/superglue/*.sh`
- zugehoerige Doku unter `docs/workflows/` und `docs/cards/`

### INT-SG-034 - Bootstrap und Secret-Mapping

Ziel:

- tenant-spezifisches Secret-/Host-Mapping fuer Produktion explizit machen
- Bootstrap nicht als freie Handarbeit, sondern als Script + Doku liefern

Dateibesitz:

- `scripts/superglue/bootstrap-secrets.*`
- zugehoerige Doku unter `docs/workflows/` und `docs/cards/`

### INT-SG-035 - Upstream Runtime-Contract fuer Self-Host

Ziel:

- Compose-, K8s- und Helm-Pfad auf den aktuellen Upstream-Port-/Env-/Storage-Contract ziehen
- lokale Runtime-Fallen fuer Self-Host explizit modellieren

Dateibesitz:

- `docker-compose.integration.yml`
- `docker-compose.integration.edge.yml`
- `k8s/superglue/**`
- `k8s/helm/valeo-erp/templates/superglue-*.yaml`
- `k8s/helm/valeo-erp/values.yaml`
- `scripts/superglue/**`

### INT-SG-036 - REST- und Health-Mapping auf `/v1`

Ziel:

- Tool-Sync und Health auf den aktuellen REST-Vertrag umstellen
- alte GraphQL-/Health-Annahmen aus dem produktiven Pfad entfernen

Dateibesitz:

- `app/integrations/adapters/superglue/tool_sync.py`
- `tests/test_superglue_tool_sync.py`
- `tests/test_process_kernel_wave88_external_agent_integrations.py`

### INT-SG-037 - Tool-Execution und Run-Tracking

Ziel:

- produktive Tool-Execution auf `/v1/tools/{toolId}/run` ziehen
- Run-Status, Journal und Audit-Envelope auf denselben Vertrag harmonisieren

Dateibesitz:

- `app/integrations/services/superglue_execution_service.py`
- `app/integrations/services/superglue_execution_journal.py`
- `app/integrations/services/superglue_capability_service.py`
- `tests/test_superglue_execution_guardrails.py`
- `tests/test_superglue_broker_integration.py`

### INT-SG-038 - Bootstrap, Secret-Mapping und Pilotadapter

Ziel:

- read-only Pilotadapter auf echte Tool-Run-Pfade ziehen
- Bootstrap und Zielstruktur um die fehlenden Upstream-Pflichtpfade ergaenzen

Dateibesitz:

- `app/integrations/adapters/superglue/*.py`
- `app/integrations/ports/**`
- `scripts/superglue/bootstrap-secrets.*`
- `tests/test_superglue_document_adapter.py`
- `tests/test_superglue_partner_preview.py`
- `tests/test_superglue_customer_profile_adapter.py`

### INT-SG-039 - Live-Smoke gegen echten Upstream-Container

Ziel:

- den Compose-Pfad nicht nur rendern, sondern gegen einen real gestarteten Upstream-Container pruefen
- erkannte Runtime-Blocker im selben Slice schliessen

Dateibesitz:

- `docker-compose.integration.yml`
- `scripts/superglue/start-compose.*`
- `scripts/superglue/smoke-check.*`
- `docs/workflows/int-sg-039-superglue-runtime-smoke.md`
- `docs/cards/neuro-core/INT-SG-039-superglue-runtime-smoke.md`

### INT-SG-040 - Zielstruktur- und Doku-Alignment

Ziel:

- Soll-/Ist-Zielstruktur fuer `app/integrations/**` abschliessen
- Workboard, Architekturplan und bekannte Restluecken auf denselben Stand ziehen

Dateibesitz:

- `app/integrations/**`
- `docs/agent-ops/active-workboard.md`
- `docs/architecture/superglue-integration-implementation-plan.md`
- `docs/project-context/open-gaps-and-known-issues.md`
- `docs/workflows/int-sg-040-superglue-target-structure.md`
- `docs/cards/neuro-core/INT-SG-040-superglue-target-structure.md`

### INT-SG-041 - Tool-Provisioning und echter Run-Smoke

Ziel:

- den leeren Upstream-Katalog in einen reproduzierbar provisionierten Pilotpfad ueberfuehren
- einen echten Tool-Run gegen den aktuellen Self-Host-Container nachweisen
- lokale Start-Smokes gegen Health-Readiness robuster machen

Dateibesitz:

- `app/integrations/adapters/superglue/client.py`
- `app/integrations/adapters/superglue/tool_sync.py`
- `app/integrations/services/superglue_tool_provisioning.py`
- `app/api/v1/endpoints/external_agent_integrations.py`
- `scripts/superglue/smoke-check.*`
- `tests/test_superglue_client.py`
- `tests/test_superglue_tool_provisioning.py`
- `tests/test_superglue_refresh_and_quarantine.py`
- `tests/test_process_kernel_wave88_external_agent_integrations.py`
- `docs/workflows/int-sg-041-superglue-tool-provisioning.md`
- `docs/cards/neuro-core/INT-SG-041-superglue-tool-provisioning.md`

### INT-SG-042 - Guarded Dev-Egress fuer lokalen SuperglueClient

Ziel:

- lokalen Dev-Smoke ueber den echten `SuperglueClient` ermoeglichen
- dabei nur Loopback explizit und default-off freigeben
- zentrale SSRF-/Egress-Regeln fuer `.internal`, `.local` und private Netze unangetastet lassen

Dateibesitz:

- `app/core/config.py`
- `app/core/outbound_security.py`
- `app/integrations/adapters/superglue/client.py`
- `app/integrations/adapters/superglue/tool_sync.py`
- `tests/test_security_outbound_policy.py`
- `tests/test_superglue_client.py`
- `tests/test_superglue_contracts.py`
- `docs/workflows/int-sg-042-superglue-dev-egress.md`
- `docs/cards/neuro-core/INT-SG-042-superglue-dev-egress.md`

### INT-SG-043 - Tenant-/System-Bootstrap fuer echte Connectoren

Status:

- umgesetzt am 2026-04-06

Ziel:

- Systems, Credentials und Tool-Definitionen pro Tenant reproduzierbar gegen den laufenden Superglue-Server provisionieren
- lokalen Pilot-Bootstrap in einen produktiven Tenant-Bootstrap ueberfuehren

Dateibesitz:

- `app/integrations/services/**`
- `app/api/v1/endpoints/external_agent_integrations.py`
- `scripts/superglue/**`
- `tests/test_superglue_*`

Abnahme:

- mindestens ein Tenant kann Systems, Credentials und Tools deterministisch bootstrapen
- kein Shared-Credential-Pfad fuer produktive Tenant-Daten

### INT-SG-044 - Produktiver Secret-/Credential-Resolver

Status:

- umgesetzt am 2026-04-06

Ziel:

- tenant-spezifische Credential-Aufloesung in den Laufzeitpfad ziehen
- fehlende oder invalide Secrets kontrolliert degradieren

Dateibesitz:

- `app/integrations/services/superglue_secret_resolver.py`
- `app/services/secrets_vault.py`
- `app/core/config.py`
- `tests/test_superglue_*`

Abnahme:

- produktive Connector-Aufrufe nutzen tenant-spezifische Secrets
- kein stiller Fallback auf globale Shared-Credentials

### INT-SG-045 - Tool-Lifecycle-Management und Drift-Control

Status:

- umgesetzt am 2026-04-06

Ziel:

- Create/Update/Archive fuer echte Superglue-Tools standardisieren
- Drift und Versionen in der VALEO-Admin-Sicht nachvollziehbar machen

Dateibesitz:

- `app/integrations/adapters/superglue/tool_sync.py`
- `app/integrations/services/superglue_tool_provisioning.py`
- `app/api/v1/endpoints/external_agent_integrations.py`
- `tests/test_superglue_tool_*`

Abnahme:

- Tool-Versionen, Delta und Archive-Status sind sichtbar
- VALEO-Contract-Mapping bleibt trotz Upstream-Aenderungen stabil

### INT-SG-046 - Run-Result-Normalisierung

Status:

- umgesetzt am 2026-04-06

Ziel:

- echte Connector-Responses und Fehler in stabile VALEO-Envelopes ueberfuehren
- Result- und Error-Semantik ueber alle Superglue-Connectoren angleichen

Dateibesitz:

- `app/integrations/contracts/**`
- `app/integrations/services/superglue_execution_service.py`
- `app/integrations/services/superglue_execution_journal.py`
- `tests/test_superglue_execution_*`

Abnahme:

- `read`, `suggest`, `simulate` und `execute` liefern denselben Envelope-Standard
- Fehlerklassen, Retry-Hinweise und Audit-Metadaten sind connector-unabhaengig

### INT-SG-047 - DMS-Connector produktiv

Status:

- umgesetzt am 2026-04-06

Ziel:

- Document-Preview durch echten DMS-Read-/Search-/Reference-Pfad ersetzen

Dateibesitz:

- `app/integrations/adapters/superglue/document_adapter.py`
- `app/integrations/ports/document_port.py`
- `tests/test_superglue_document_adapter.py`

Abnahme:

- VALEO kann echte Dokumente suchen und referenzieren
- File-Reference-/Metadata-Pfad ist tenant-sicher

### INT-SG-048 - Partner-EDI-Connector produktiv

Status:

- umgesetzt am 2026-04-06

Ziel:

- Partner-/EDI-Preview durch echten Simulations- und Mappingpfad ersetzen

Dateibesitz:

- `app/integrations/adapters/superglue/edi_adapter.py`
- `app/integrations/ports/partner_edi_port.py`
- `tests/test_superglue_partner_preview.py`

Abnahme:

- mindestens ein realer Partnerflow kann simuliert und validiert werden
- Partner-spezifische Fehler und Mapping-Hinweise sind versioniert surfacbar

### INT-SG-049 - CRM-/Masterdata-Connector produktiv

Status:

- umgesetzt am 2026-04-06

Ziel:

- externen Customer-/Masterdata-Read statt Preview liefern

Dateibesitz:

- `app/integrations/adapters/superglue/customer_profile_adapter.py`
- `app/integrations/ports/customer_profile_port.py`
- `tests/test_superglue_customer_profile_adapter.py`

Abnahme:

- CRM-/Stammdaten-Read laeuft ueber echten Connector
- Datenschutz- und Tenant-Feldmapping sind abgesichert

### INT-SG-050 - File-Reference-/Artifact-Pfad produktiv

Status:

- umgesetzt am 2026-04-06

Ziel:

- echte Run-Artefakte, Uploads und Dateireferenzen in VALEO nutzbar machen

Dateibesitz:

- `app/integrations/services/superglue_execution_service.py`
- `docker-compose.integration.yml`
- `k8s/superglue/**`
- `tests/test_superglue_*`

Abnahme:

- echte Dateiartefakte koennen referenziert und auditiert werden
- Zugriffsschutz und Lebenszyklus fuer Artefakte sind dokumentiert

### INT-SG-051 - Execute-Gates fuer reale Connector-Writes

Status:

- umgesetzt am 2026-04-06

Ziel:

- reale Write-Connectoren hart an Approval, Policy und Audit binden

Dateibesitz:

- `app/services/neuro_tool_broker.py`
- `app/services/neuro_tool_execution.py`
- `app/integrations/services/superglue_execution_service.py`
- `tests/test_superglue_broker_integration.py`

Abnahme:

- kein Write-Pfad umgeht Approval-/Policy-Gates
- Write-Runs erscheinen belastbar in Audit und Decision-Trace

### INT-SG-052 - Idempotenz, Replay und Correlation-Hardening

Status:

- umgesetzt am 2026-04-06

Ziel:

- doppelte externe Writes und unsaubere Retries verhindern

Dateibesitz:

- `app/integrations/services/superglue_execution_service.py`
- `app/integrations/services/superglue_execution_journal.py`
- `tests/test_superglue_execution_*`

Abnahme:

- identische Correlation-/Replay-Faelle werden sicher behandelt
- Retry fuehrt nicht zu fachlichen Dubletten

### INT-SG-053 - Quarantaene, Retry und Dead-letter fuer echte Connectorfehler

Status:

- umgesetzt am 2026-04-06

Ziel:

- betriebsfaehige Fehlerpfade fuer reale externe Ausfaelle schliessen

Dateibesitz:

- `app/integrations/services/superglue_quarantine.py`
- `app/integrations/services/superglue_execution_service.py`
- `tests/test_superglue_refresh_and_quarantine.py`

Abnahme:

- degradierte Runs landen nachvollziehbar in Quarantaene
- Retry-/Resolve-Entscheidungen sind ohne Fachduplikate moeglich

### INT-SG-054 - Admin-Surface fuer Systems, Credentials, Tools und Drift

Status:

- umgesetzt am 2026-04-06

Ziel:

- Superglue-Operations nicht nur technisch, sondern betreibbar surfacen

Dateibesitz:

- `app/api/v1/endpoints/external_agent_integrations.py`
- `packages/frontend-web/src/pages/admin/**`
- `tests/test_process_kernel_wave88_external_agent_integrations.py`

Abnahme:

- Betreiber sehen Bootstrap, Drift, letzte Runs und Quarantaene in einer konsistenten Admin-Sicht
- keine Secret-Exposition und keine direkte Fachbedienung im UI

### INT-SG-055 - Monitoring, Kosten und Alerting pro Connector/Tenant

Status:

- umgesetzt am 2026-04-06

Ziel:

- technische Health-Sicht um Nutzung, Fehlerquote, Latenz und Kosten erweitern

Dateibesitz:

- `app/integrations/services/**`
- `k8s/helm/valeo-erp/templates/**`
- `ops/superglue/**`

Abnahme:

- Monitoring zeigt Connector-, Tool- und Tenant-Sicht
- Alerting deckt Health, Fehlerquote und Kostenanomalien ab

### INT-SG-056 - Staging-/CI-Smoke mit echtem Dev-Connector

Status:

- umgesetzt am 2026-04-06

Ziel:

- lokalen Dev-Smoke in einen reproduzierbaren CI-/Staging-Pfad ueberfuehren

Dateibesitz:

- `.github/workflows/**`
- `scripts/superglue/**`
- `tests/test_superglue_*`

Abnahme:

- mindestens ein echter Connector-Smoke laeuft automatisiert vor Deploy
- Test-Credentials und externe Systeme sind sauber isoliert

### INT-SG-057 - Procurement-/Lieferanten-Connectoren ausrollen

Status:

- umgesetzt am 2026-04-06

Ziel:

- ersten echten P2P-/Supplier-Nutzen produktiv ueber Superglue liefern

Dateibesitz:

- `app/integrations/adapters/superglue/**`
- `app/services/command_handlers_procurement.py`

Abnahme:

- mindestens ein produktiver Procurement-/Supplier-Flow nutzt Superglue
- Einkaufslogik bleibt in VALEO, nicht in Transforms

### INT-SG-058 - Finance-/Steuer-/Export-Connectoren ausrollen

Status:

- umgesetzt am 2026-04-06

Ziel:

- ersten echten Finance-/Export-Nutzen produktiv ueber Superglue liefern

Dateibesitz:

- `app/api/v1/endpoints/finance_*.py`
- `app/api/v1/endpoints/export_service.py`
- `app/integrations/adapters/superglue/**`

Abnahme:

- mindestens ein Finance-/Export-Flow nutzt echten Connector
- Auditierbarkeit fuer regulatorische Exporte bleibt intakt

### INT-SG-059 - Logistics-/Warehouse-/Carrier-Connectoren ausrollen

Status:

- umgesetzt am 2026-04-06

Ziel:

- Transport-, Versand- oder Lageranbindungen ueber denselben Standardpfad aufbauen

Dateibesitz:

- `app/api/v1/endpoints/warehouses*.py`
- `app/integrations/adapters/superglue/**`

Abnahme:

- mindestens ein Logistics-/Carrier-Flow ist produktiv angebunden
- zustandsbehaftete Label-/Carrier-Pfade bleiben write-sicher

### INT-SG-060 - Optionaler breiter Rollout auf Agrar, Service und Analytics

Status:

- umgesetzt am 2026-04-06

Ziel:

- priorisierte Zusatzdomänen nach demselben Connector-Standard erschliessen

Dateibesitz:

- `app/integrations/adapters/superglue/**`
- `packages/frontend-web/src/pages/**`

Abnahme:

- Zusatzdomänen folgen dem etablierten Standardpfad statt Einzellösungen
- Start erst nach mindestens drei produktiven Referenz-Connectoren und Betriebsreife

### INT-SG-061 - Live-Readiness fuer Credentials, Onboarding und Policies surfacen

Status:

- umgesetzt am 2026-04-06

Ziel:

- die verbleibenden operativen Restluecken nach dem Code-Rollout explizit als API-/Admin-Sicht surfacen

Dateibesitz:

- `app/core/config.py`
- `app/integrations/services/superglue_connector_registry.py`
- `app/integrations/services/superglue_live_readiness.py`
- `app/api/v1/endpoints/external_agent_integrations.py`
- `packages/frontend-web/src/pages/admin/agenten-integration.tsx`

Abnahme:

- Admin und API zeigen pro Tenant fehlende Credentials, Platzhalter-Zielsysteme und Execute-Blocker
- Alerting-/Retention-Werte sind je Environment explizit sichtbar statt nur implizit in Ops-Dokumenten

### INT-SG-062 - Tenant-Onboarding-Pack fuer Ops exportieren

Status:

- umgesetzt am 2026-04-06

Ziel:

- aus der Live-Readiness einen konkreten Ops-Export fuer Tenant-Aktivierung bauen

Dateibesitz:

- `app/integrations/services/superglue_onboarding_pack.py`
- `app/api/v1/endpoints/external_agent_integrations.py`
- `packages/frontend-web/src/pages/admin/agenten-integration.tsx`

Abnahme:

- API liefert Secret-Key-Kandidaten, Zielsystem-Felder und Policy-Werte je Tenant
- Admin-Surface zeigt den Onboarding-Pack fuer Ops lesbar an

### INT-SG-063 - Onboarding-Pack als CLI-/Script-Export bereitstellen

Status:

- umgesetzt am 2026-04-06

Ziel:

- den bestehenden Tenant-Onboarding-Pack ohne UI direkt als Skript-/CLI-Artefakt exportieren

Dateibesitz:

- `scripts/superglue/export-onboarding-pack.*`
- `app/integrations/services/superglue_onboarding_templates.py`

Abnahme:

- JSON-Export ist fuer einen Tenant direkt per Script renderbar
- PowerShell- und Bash-Pfad nutzen denselben Python-Renderer

### INT-SG-064 - Env-/Vault-Template aus Onboarding-Pack rendern

Status:

- umgesetzt am 2026-04-06

Ziel:

- aus demselben Onboarding-Pack direkt verwertbare Template-Artefakte fuer Ops erzeugen

Dateibesitz:

- `app/integrations/services/superglue_onboarding_templates.py`
- `scripts/superglue/export-onboarding-pack.*`

Abnahme:

- `.env`-Template und Vault-Mapping lassen sich ohne zweite Modellierung rendern
- Templates enthalten nur Key-Kandidaten und Policy-Werte, keine Live-Secrets

### INT-SG-065 - Onboarding-Skripte in CI validieren

Status:

- umgesetzt am 2026-04-06

Ziel:

- die neuen Onboarding-Artefakte automatisiert auf Renderbarkeit pruefen

Dateibesitz:

- `.github/workflows/superglue-infra.yml`
- `scripts/superglue/export-onboarding-pack.*`

Abnahme:

- CI rendert JSON-, ENV- und Vault-Artefakt fuer einen Beispiel-Tenant
- no-silent-drift im Ops-Pfad fuer neue Exportformate

### INT-SG-066 - Admin-Download fuer Onboarding-Artefakte surfacen

Status:

- umgesetzt am 2026-04-06

Ziel:

- Ops soll dieselben Artefakte direkt aus der Admin-Seite herunterladen koennen

Dateibesitz:

- `packages/frontend-web/src/pages/admin/agenten-integration.tsx`
- `packages/frontend-web/src/__tests__/pages/admin/agenten-integration.test.tsx`

Abnahme:

- Admin bietet direkte Downloads fuer Onboarding JSON, ENV Template und Vault Template
- Downloads werden aus demselben Pack/Renderer-Pfad abgeleitet

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
