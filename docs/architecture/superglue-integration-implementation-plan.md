# Superglue Integration - Implementierungsplan

**Status:** in Umsetzung, Basispfade INT-SG-001 bis INT-SG-028 umgesetzt
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

Aktueller Stand 2026-04-03:

- `INT-SG-001` bis `INT-SG-008` sind als Basis-MVP im Repo umgesetzt.
- Offen bleiben produktive Connector-Konfiguration, tenant-spezifische Secret-Bestueckung und ein erster echter Live-Connector.

Folgewelle 2026-04-04:

- `INT-SG-009` bis `INT-SG-014` sind als Folgewelle umgesetzt: Sync-Snapshot, Config-Summary, Quarantaene, Audit-/Security-Bridge, zweiter Preview-Adapter und Admin-UX.
- `INT-SG-015` bis `INT-SG-020` sind umgesetzt: Execution-Guardrails, Sync-History, Resolve-Pfad fuer Quarantaene, Execution-Journal, dritter read-only Pilotadapter und Admin-UX-Nachzug.
- `INT-SG-021` ist umgesetzt: Compose-Stack fuer Superglue mit eigener DB, MinIO, Init-Job, Volumes und Healthchecks.
- `INT-SG-022` ist umgesetzt: Reverse-Proxy-Overlay mit TLS-Endpunkten, internen Service-Ports und Header-Hardening.
- `INT-SG-023` bis `INT-SG-028` sind umgesetzt: Kubernetes-Basis, Helm-Overlay, NetworkPolicy/Ingress, Backup/Restore, CI-Validierung und wiederholbare Ops-Scripts.
- `INT-SG-029` bis `INT-SG-034` bilden die produktionsnahe Control-Plane-Welle: ArgoCD, Secret-/Certificate-CRDs, Prometheus/Grafana, dedizierter Deploy-Workflow und Bootstrap der tenant-spezifischen Ops-Konfiguration.

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
