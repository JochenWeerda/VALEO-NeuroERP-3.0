# ADR-039 — Repo-Layout und Root-Konsolidierung

**Status:** Accepted
**Datum:** 2026-07-06
**Bezieht sich auf:** Production-Readiness-Audit 2026-07-02 (ARCH-F1, SPEC-P1-07, Prompt A9)

## Kontext

Im Repository-Root koexistierten 39 getrackte Verzeichnisse, darunter historische
Experimente (`swarm/`, `ols/`, `mains/`), abgeschlossene Migrationsprojekte
(`l3-migration-toolkit/`, `guacamole-l3-migration/`), Einzeldatei-Ordner (`memory/`,
`qa/`, `planning/`, `specs/`, `knowledge-base/`) und ein **paralleles
TypeScript-Backend** (`domains/` mit analytics/finance/integration/inventory/shared),
das laut Tracker nie produktiv verdrahtet war, aber zwei eigene CI-Workflows besass.
Fuer Entwickler und Agenten war nicht deterministisch, wo Code hingehoert (Audit-Befund
ARCH-F1).

## Entscheidung

### 1. `domains/` (paralleles TS-Backend): **archiviert**

Gemaess strategischer Positionierung (kein Microservice-Split, Canonical Domain Model
im Python-Backend als Quelle) wird `domains/` nicht produktiv verdrahtet, sondern nach
`docs/_internal/archive/domains-ts-backend/` verschoben. Die zugehoerigen Workflows
`inventory-domain-ci.yml` und `finance-domain-ci.yml` sowie der `audit-e2e`-Job in
`ci.yml` entfallen. Die aktiven `packages/erp-domain`-Tests laufen weiterhin im
quality-gate.

### 2. Root-Sprawl: 18 Verzeichnisse archiviert, 1 konsolidiert

Nach `docs/_internal/archive/` verschoben (git mv, Historie erhalten; Verzeichnis ist
von docs-Governance-/Markdown-Checks ausgenommen):

| Verzeichnis | Klassifikation |
|---|---|
| `contract-tests/`, `qa/`, `specs/`, `planning/`, `knowledge-base/`, `memory/`, `reports/` | Einzeldateien/Alt-Doku ohne Referenzen |
| `ols/`, `gap/`, `extensions/`, `mains/`, `observability/` | abgeschlossene Analysen/Experimente |
| `swarm/` (+ `docker-compose.swarm.yml`) | Agent-Schwarm-Experiment, nicht verdrahtet |
| `l3-migration-toolkit/`, `guacamole-l3-migration/` | abgeschlossene L3-Migrationsprojekte |
| `load-tests/` | veraltete Lasttest-Skripte (aktiv: `scripts/loadtest/`) |
| `src/` → `root-src-mcp-policy-server/` | MCP-Policy-Server-Prototyp (Port 7070), nicht der BFF (`packages/bff`, 4001); `mcp:dev`-Script entfernt |
| `domains/` → `domains-ts-backend/` | s. o. |

Konsolidiert: `database/` → `infra/database/` (lose Init-/Analyse-SQL; Compose-Pfade in
`docker-compose.eventbus.yml` und `docker-compose.production.yml` angepasst).

### 3. Ziel-Layout (20 Root-Verzeichnisse)

| Verzeichnis | Zweck |
|---|---|
| `app/`, `modules/`, `alembic/`, `migrations/`, `tests/` | Python-Backend, Domain-Module, Migrationen, Tests |
| `packages/` | pnpm-Monorepo (frontend-web, bff, erp-domain, …) |
| `playwright-tests/` | Frontend-E2E (Root-Playwright-Config) |
| `scripts/`, `tools/` | Betriebs-/CI-/Migrations-Skripte |
| `config/`, `data/` | Laufzeit-Konfiguration (Ratchets, Allowlists, proplanta) |
| `docs/`, `artifacts/` | Dokumentation, CI-/Audit-Evidenz |
| `infra/`, `deploy/`, `k8s/`, `ops/`, `monitoring/`, `database→infra` | Infrastruktur (DMS, nginx, Helm, Superglue, Prometheus) |
| `services/` | EPCIS-Inventory-Service (ci.yml-verdrahtet) |
| `rationsoptimierung/` | Rationsoptimierungs-Service (docker-compose-verdrahtet) |

**Regel:** Neue Top-Level-Verzeichnisse nur mit ADR. Neuer Backend-Code gehoert nach
`app/` bzw. `modules/`, neuer Frontend-/TS-Code nach `packages/`. Experimente starten
nicht im Root, sondern in einem Feature-Branch oder unter `docs/_internal/`.

## Konsequenzen

- **+** Root ist deterministisch lesbar (20 Verzeichnisse, jede mit klarem Zweck).
- **+** Zwei tote CI-Workflows weniger; kein Parallel-Backend mehr neben `app/`.
- **+** Historie bleibt per git mv erhalten; Archiv bleibt durchsuchbar.
- **−** Externe Links auf alte Pfade (z. B. `domains/finance/...`) muessen bei Bedarf
  auf `docs/_internal/archive/...` umgestellt werden.
