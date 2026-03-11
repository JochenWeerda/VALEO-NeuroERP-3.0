# Agenten-Integration – VALEO NeuroERP

Anleitung für externe Agenten (Perplexity, Claude, Cursor, Custom Agents), die VALEO NeuroERP über REST-APIs anbinden wollen.

## Übersicht

VALEO NeuroERP ist ein Multi-Tenant-ERP-System für Agrargenossenschaften und den Landhandel. Die API bietet:

- **REST unter `/api/v1/`** – OpenAPI 3.x kompatibel
- **MCP-BFF unter `/api/mcp/`** – Model Context Protocol für Copilot-Frontend
- **Multi-Tenancy** – `X-Tenant-ID` Header
- **OIDC** – Bearer-Token (Keycloak, Azure AD, Auth0)

## OpenAPI-Spezifikation

| URL | Beschreibung |
|-----|--------------|
| `{BASE}/api/v1/openapi.json` | OpenAPI 3.x JSON |
| `{BASE}/api/v1/admin/agent-manifest` | Maschinenlesbares Agent-Manifest |
| `{BASE}/docs` | Swagger UI |
| `{BASE}/redoc` | ReDoc |

**Beispiel-Base:**  
- Lokal: `http://localhost:8000`  
- Vite-Proxy: Frontend unter Port 3001, `/api/v1` → Backend 8000

## Authentifizierung

### Header

```
Authorization: Bearer <access_token>
X-Tenant-ID: <tenant-uuid>
Content-Type: application/json
```

### Token-Beschaffung

- **OIDC**: Standard OAuth2/OIDC-Flow (Authorization Code, Client Credentials) gegen den konfigurierten Issuer
- **Dev-Modus**: Optional `API_DEV_TOKEN` für lokale Entwicklung

### API-Keys für Agenten

*In Planung (Hauptstrang):* Dedizierte API-Keys oder OAuth2-Client-Credentials für externe Agenten (Perplexity, etc.). Aktuell nutzen Agenten dasselbe OIDC-Setup wie das Frontend.

## Wichtige Endpoints (Beispiele)

| Bereich | Beispiel-Pfad | Beschreibung |
|---------|---------------|--------------|
| Analytics | `/api/v1/analytics/benchmark` | Branchenbenchmark, KPIs |
| CRM | `/api/v1/crm/...` | Kontakte, Leads, Kampagnen |
| Einkauf | `/api/v1/einkauf/...` | Bestellungen, Lieferanten |
| FIBU | `/api/v1/fibu/...` | Buchungen, Konten, OP |
| Nachhaltigkeit | `/api/v1/sustainability/...` | ESG-Report, CO2e |
| Admin | `/api/v1/admin/data-quality/...` | Datenqualitätsprüfung |

## Agent Manifest

Für externe Agenten gibt es zusätzlich einen kompakten, maschinenlesbaren Einstiegspunkt:

- `GET /api/v1/admin/agent-manifest`

Enthalten sind:

- Auth-Schema und Pflicht-Header
- zentrale Links (OpenAPI, Swagger, ReDoc)
- Beispiel-Endpunkte für REST und MCP
- Integrationshinweise für Codegen und Tool-Runtimes

## MCP-BFF (Model Context Protocol)

Für den integrierten Ask-VALEO-Copilot:

- `POST /api/mcp/{service}/{action}`  
- Payload: JSON-Body  
- Headers: wie oben (Bearer, X-Tenant-ID)

Beispiel-Services: `analytics`, `copilot`.

## Use-Cases für externe Agenten

1. **Perplexity/Claude**: „Zeige mir den ESG-Report für 2025“ → `/api/v1/sustainability/esg-report?year=2025`
2. **Bestandsabfrage**: Lagerbestände, Artikel → `/api/v1/inventory/...`
3. **KPI-Dashboard**: Benchmark, Umsatz → `/api/v1/analytics/...`
4. **CRM**: Kontakte, Kampagnen-Status → `/api/v1/crm/...`

## Einschränkungen

- **Tenant-Isolation**: Jede Anfrage muss `X-Tenant-ID` enthalten; Zugriff nur auf Daten des Mandanten
- **Berechtigungen**: RBAC wird pro Endpoint angewendet
- **Rate-Limiting**: (Hauptstrang) – noch nicht produktiv

## Weiterführende Links

- [CLAUDE.md](../CLAUDE.md) – Technischer Überblick
- [MASKEN.md](MASKEN.md) – Masken-Standards
- Steuerungsdokument: `docs/roadmap/status/2026-03-06-arbeitsaufteilung-codex-hauptstrang.md`
