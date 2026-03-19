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

## Referenzen

- [Architecture Index](architecture/index.md)
- [Process Kernel Status](architecture/process-kernel/STATUS.md)
- [AI Vision](AI-VISION.md)
