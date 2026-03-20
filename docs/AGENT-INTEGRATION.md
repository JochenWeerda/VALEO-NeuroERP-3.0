# Agenten-Integration - VALEO NeuroERP

**Zweck:** `Referenzdokument` fuer externe Agenten, API-Anbindung und Integrationspfade. Nicht der operative Lieferstand.

Anleitung fuer externe Agenten wie Claude, Cursor oder Custom Agents, die VALEO NeuroERP ueber REST-APIs und agentenfaehige Contracts anbinden wollen.

## Einordnung

Diese Datei ist eine `abgeleitete Sicht` auf Integrationspfade fuer Agenten. Verbindlicher Delivery- und Architekturstand liegt in [STATUS.md](architecture/process-kernel/STATUS.md), [Architecture Index](architecture/index.md) und den jeweiligen ADRs.

## Uebersicht

VALEO NeuroERP ist ein Multi-Tenant-ERP-System fuer Agrargenossenschaften und den Landhandel. Die API bietet:

- REST unter `/api/v1/`
- agentennahe Integrationspfade ueber Manifest- und Contract-Dokumente
- Multi-Tenancy ueber `X-Tenant-ID`
- OIDC-basierte Authentifizierung

## OpenAPI-Spezifikation

| URL | Beschreibung |
|-----|--------------|
| `{BASE}/api/v1/openapi.json` | OpenAPI 3.x JSON |
| `{BASE}/api/v1/admin/agent-manifest` | Maschinenlesbares Agent-Manifest |
| `{BASE}/api/v1/agent/tool-contracts` | Externes MCP/OpenAPI-Tool-Manifest |
| `{BASE}/api/v1/agent/tool-contracts/mcp` | MCP ToolDefinition-Liste fuer externe Agenten |
| `{BASE}/api/v1/agent/tool-contracts/openapi` | OpenAPI-verknuepfte Tool-Contracts |
| `{BASE}/api/v1/agent/integrations` | Externer Provider-/Use-Case-Katalog fuer Agenten |
| `{BASE}/api/v1/agent/integrations/providers` | Provider-Catalog mit Auth-/Install-Informationen |
| `{BASE}/api/v1/agent/integrations/use-cases` | 11 installierbare Agent-Use-Cases mit Domain-/Approval-Kontext |
| `{BASE}/api/v1/agent/integrations/use-cases/{use_case_id}/install-pack` | Install-Pack fuer einen konkreten Use Case |
| `{BASE}/docs` | Swagger UI |
| `{BASE}/redoc` | ReDoc |

## Authentifizierung

### Header

```text
Authorization: Bearer <access_token>
X-Tenant-ID: <tenant-uuid>
Content-Type: application/json
```

### Token-Beschaffung

- OIDC: Authorization Code oder Client Credentials gegen den konfigurierten Issuer
- Dev-Modus: optional `API_DEV_TOKEN` fuer lokale Entwicklung

## Wichtige Endpoints

| Bereich | Beispiel-Pfad | Beschreibung |
|---------|---------------|--------------|
| Analytics | `/api/v1/analytics/benchmark` | Branchenbenchmark und KPIs |
| CRM | `/api/v1/crm/...` | Kontakte, Leads, Kampagnen |
| Einkauf | `/api/v1/einkauf/...` | Bestellungen und Lieferanten |
| FIBU | `/api/v1/fibu/...` | Buchungen, Konten, offene Posten |
| Nachhaltigkeit | `/api/v1/sustainability/...` | ESG-Report und CO2e |
| Admin | `/api/v1/admin/data-quality/...` | Datenqualitaetspruefung |

## Externe Agenten

Der produktive Integrationslayer unterscheidet jetzt zwischen:

- OpenAPI-Clients fuer typed SDKs und klassische Integrationen
- MCP-Clients fuer toolbasierte Agenten
- Slack- und Teams-Apps fuer operatives Arbeiten im Chatkanal
- externe Agent-Use-Cases mit explizitem Install-Pack
- 23 produktiven Tools mit konsistenten Manifest-, MCP- und OpenAPI-Views

### Provider-Katalog

| Provider | Auth-Modell | Hinweis |
|----------|-------------|--------|
| OpenAPI Client | Bearer + `X-Tenant-ID` | Typisierte SDKs und klassische Integrationen |
| MCP Client | Bearer + `X-Tenant-ID` | Tool-basierte Agenten mit Contract-Views |
| Slack App | Signing Secret + Bot Token | Channel-/DM-Arbeit fuer Human-in-the-Loop |
| Microsoft Teams App | Webhook Secret / OAuth | Tenant- und kanalfaehige Chat-Integration |
| Custom Agent SDK | OIDC Bearer + `X-Tenant-ID` | LangGraph, eigene Bots, Agent Runtimes |
| Automation Platform | API Key / OAuth2 | Make, Zapier, Power Automate und aehnliche Tools |

### Installierbare Use Cases

Der Katalog bietet 11 installierbare Use Cases mit Domain-, Approval- und Entry-Point-Kontext, darunter:

- Knowledge Lookup
- Process Action Execution
- Approval Decision Support
- Finance Control Read
- Bulk Batch Runner
- Document Extraction
- Supply Chain ETA Monitoring
- Complaint Case Orchestration
- Workflow Sandbox Preview
- Dashboard Read-Model Consumer
- Background Job Orchestration

Der Katalog liefert fuer jeden Use Case:

- Domain-Zuordnung
- Auth-Modell
- Approval-Anforderungen
- relevante Entry Points
- Tool-Contract-Referenzen
- Install-Schritte fuer den produktiven Anschluss
- Die Tool-Contracts selbst tragen Domain-, Approval- und Auth-Metadaten als konsistente View ueber alle Manifest-Endpoints hinweg

## Referenzen

- [Architecture Index](architecture/index.md)
- [Process Kernel Status](architecture/process-kernel/STATUS.md)
- [AI Vision](AI-VISION.md)
