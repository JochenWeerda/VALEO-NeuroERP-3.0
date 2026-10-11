# VALEO NeuroERP 3.0

[![Quality Gate](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/workflows/quality-gate.yml/badge.svg?branch=main)](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/workflows/quality-gate.yml)
[![Security Scan](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/workflows/security-scan.yml/badge.svg?branch=main)](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/workflows/security-scan.yml)
[![Universal Mask CI](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/workflows/universal-mask-ci.yml/badge.svg?branch=main)](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/workflows/universal-mask-ci.yml)
[![PostgreSQL Tests](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/workflows/pytest-postgres-require-db.yml/badge.svg?branch=main)](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/workflows/pytest-postgres-require-db.yml)
[![Docs Governance](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/workflows/docs-governance.yml/badge.svg?branch=main)](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/workflows/docs-governance.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

[Deutsch](#deutsch) · [English](#english)

## Deutsch

VALEO NeuroERP 3.0 ist ein ERP-System für Agrargenossenschaften und Landhandelsunternehmen. Es verbindet Fachprozesse, mandantenbezogene Datenzugriffe und agentenfähige Schnittstellen in einem gemeinsamen Repository.

### Entwicklungsstand

**README geprüft am 11. Oktober 2026. Das Projekt befindet sich in der Entwicklungs- und Stabilisierungsphase.** Der Status einzelner Funktionen ergibt sich aus den verlinkten Lieferständen und Prüfnachweisen; eine allgemeine Produktivfreigabe ist damit nicht verbunden.

| Bereich | Verbindlicher Einstieg |
| --- | --- |
| Gelieferte Prozesswellen | [Process Kernel Status](docs/architecture/process-kernel/STATUS.md) und die dort verlinkten Wave-Statusdateien |
| Laufende Arbeiten und Integration | [Active Workboard](docs/agent-ops/active-workboard.md) |
| Offene Befunde und Abhängigkeiten | [Open Gaps](docs/project-context/open-gaps-and-known-issues.md) |
| Masken und Bedienoberfläche | [Universal Mask Runtime Status](docs/architecture/uix/universal-mask-runtime-status.md) |
| Aktuelle CI-Ergebnisse | [GitHub Actions](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions?query=branch%3Amain) |
| Betriebsfreigabe und externe Nachweise | [Production Readiness Runbook](docs/operations/production-readiness-runbook.md) |

Die CI-Badges zeigen den jeweiligen Workflow-Stand. Bei der Prüfung des veröffentlichten Commits `4337dd684` waren Docs Governance, Docs Build und PostgreSQL-Tests erfolgreich; der [Quality Gate](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/runs/38121252132) war fehlgeschlagen. Maßgeblich für spätere Änderungen sind deren eigene Läufe.

Ein jüngster abgeschlossener Schwerpunkt ist die **Fuhrpark- und MCP-Mandantenisolation**: verifizierte Mandantenclaims, Schutz vor Fremdmandantenreferenzen, einheitliche Command-Validierung sowie atomare Audit-/Replay-Verarbeitung. Die [Abnahme vom 9. Oktober](docs/quality-assurance/fuhrpark-mcp-isolation-20261009.md) dokumentiert **581 bestandene Tests ohne Skip** für den isolierten Lieferstand. Das ist eine gezielte Abnahme; sie ersetzt keinen aktuellen Gesamttest des Projekts. Der dokumentierte Katalog umfasst 56 MCP-Tools und 41 zugeordnete Maskenaktionen; FIN-CLOSE gegen ADR-076 und Zahlauf `open_high` bleiben dort als offene Fachthemen ausgewiesen.

Externe Freigaben, darunter ELSTER/ERiC-Live-Übermittlung, OIDC-Abnahme im Zielbetrieb und Fiskalisierung, werden gesondert nachgewiesen. Vorhandene Adapter, Simulationen oder Dokumentation allein schließen diese Gates nicht.

### Fachlicher und technischer Aufbau

Der Fachumfang umfasst Agrarprozesse und Ernteabrechnung, Kontrakte, Verkauf, Einkauf, Lager und Wiegen, Logistik und Fuhrpark, Finanzbuchhaltung, CRM, Personal sowie Dokumente und Nachweise. Den jeweiligen Umsetzungsstand beschreiben die Statusdateien und offenen Befunde.

| Baustein | Grundlage |
| --- | --- |
| Zentrales Backend | Python, FastAPI, SQLAlchemy, PostgreSQL und Alembic; Einstieg `main:app` |
| Weboberfläche | React, TypeScript und Vite in `packages/frontend-web` |
| Maskenarchitektur | `ScreenDefinition` → `RenderPlan` → `useUniversalMaskRuntime` → `UniversalMaskRenderer` |
| Weitere Fachpakete und Services | `packages/` und `services/`; Zuordnung im [Architekturindex](config/architecture-index.yaml) |
| Ereignisse und Integrationen | NATS und domänenspezifische Integrationen gemäß Architekturverträgen |
| Agentenzugriff | MCP-Tools und Fachcommands mit Mandanten- und Berechtigungsverträgen; [Agent-Handbuch](docs/agent-handbuch/index.md) |

Architekturentscheidungen stehen im [ADR-Index](docs/adr/README.md), der strukturelle Überblick im [Architektureinstieg](docs/architecture/index.md). Änderungen müssen bestehende Verbraucher, Berechtigungen und Datenverträge berücksichtigen.

### Lokal entwickeln

Voraussetzungen: Python 3.11 entsprechend dem Backend-Entwicklungsimage, Node.js mit Corepack und **pnpm 9.12.0** gemäß [package.json](package.json), sowie eine konfigurierte PostgreSQL-Entwicklungsumgebung. Umgebungsvariablen und Zugangsdaten anhand von [.env.example](.env.example) und der [Frontend-Vorlage](packages/frontend-web/.env.example) einrichten. Datenbankschema und Authentifizierung müssen zur gewählten Konfiguration passen.

Vom Repository-Stamm aus, für eine bereits eingerichtete Entwicklungsdatenbank:

```sh
python -m venv .venv
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Die Weboberfläche in einem zweiten Terminal starten:

```sh
corepack enable
pnpm install --frozen-lockfile
pnpm --filter @valero-neuroerp/frontend-web dev --host 127.0.0.1 --port 3000
```

Frontend: `http://localhost:3000`. Backend und interaktive API-Dokumentation: `http://localhost:8000/docs`. Die API-Basis bzw. Proxy-Konfiguration richtet sich nach dem verwendeten Vite-Modus und den Frontend-Umgebungsvariablen.

Als Alternative beschreibt [docker-compose.dev.yml](docker-compose.dev.yml) einen Entwicklungsstack aus PostgreSQL, NATS, Backend und Frontend mit Ports 8000/3000. Der Backend-Einstieg [entrypoint.sh](entrypoint.sh) führt vor dem Start die Datenbankinitialisierung aus. Vor dessen Verwendung bestehende Ressourcen, Datenbankbesitz und Migrationsstand prüfen. Dieser Stack ersetzt den gemeinsamen Testprüfstand nicht.

### Qualität und Zusammenarbeit

Geeignete Prüfungen aus dem Repository-Stamm:

```sh
pnpm --filter @valero-neuroerp/frontend-web type-check
pnpm --filter @valero-neuroerp/frontend-web test:run
pnpm test:erp-domain
pnpm docs:governance
pnpm arch:validate
pnpm arch:drift
python scripts/generate_agent_handbuch.py --check
```

Backend-Tests je Änderung gezielt auswählen; datenbankabhängige Tests benötigen den bestehenden Prüfstand. **Alle Agenten verwenden `valeo_probe` bzw. die konfigurierte `TEST_DATABASE_URL`. Keine neue Datenbank und kein neuer Docker-Container pro Test, Suite oder Agent.** Vor der Nutzung nur den Status prüfen:

```sh
python scripts/pruefstand_db.py --status
```

Der Aufruf ohne Option setzt den Prüfstand zurück und ist keine normale Testvorbereitung. Daten durch Transaktionen/Savepoints oder eigene Datensätze isolieren; Migrationen und Rücksetzungen vorher koordinieren. CI nutzt die bereits vom Job bereitgestellte Datenbank. Einzelheiten: [Testdatenbank-Ressourcenregel](docs/quality-assurance/test-database-resource-policy-20261001.md).

Vor Änderungen [AGENTS.md](AGENTS.md), die [Startcheckliste](docs/agent-ops/session-start-checklist.md) und das Workboard lesen, vorhandene Lösungen prüfen und den eigenen Slice claimen. Code, Tests und Dokumentation gemeinsam pflegen; fremde laufende Änderungen schützen. Überholte Entwicklungsaltlasten dürfen nach Prüfung ihrer Verbraucher entfernt werden.

### Dokumentation und Lizenz

- [Dokumentationsübersicht](docs/README.md)
- [Benutzerhandbuch](docs/benutzerhandbuch/index.md)
- [Agent Ops und Zusammenarbeit](docs/agent-ops/README.md)
- [Offene Befunde](docs/project-context/open-gaps-and-known-issues.md)
- [MIT-Lizenz](LICENSE)

## English

VALEO NeuroERP 3.0 is an ERP system for agricultural cooperatives and agricultural trading companies. This repository connects business processes, tenant-scoped data access and agent-facing interfaces.

### Development status

**README reviewed on October 11, 2026. The project is in development and stabilization.** Delivery records and test evidence describe the status of individual features; they do not constitute a general production approval.

| Area | Authoritative entry point |
| --- | --- |
| Delivered process waves | [Process Kernel Status](docs/architecture/process-kernel/STATUS.md) and its linked wave status files |
| Active work and integration | [Active Workboard](docs/agent-ops/active-workboard.md) |
| Open findings and dependencies | [Open Gaps](docs/project-context/open-gaps-and-known-issues.md) |
| Screens and UI runtime | [Universal Mask Runtime Status](docs/architecture/uix/universal-mask-runtime-status.md) |
| Current CI results | [GitHub Actions](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions?query=branch%3Amain) |
| Operational approval and external evidence | [Production Readiness Runbook](docs/operations/production-readiness-runbook.md) |

Badges reflect individual workflows. When published commit `4337dd684` was reviewed, Docs Governance, Docs Build and PostgreSQL tests had succeeded, while the [Quality Gate](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/runs/38121252132) had failed. Subsequent changes require their own CI results.

Recent completed work strengthened **fleet and MCP tenant isolation**: verified tenant claims, cross-tenant reference protection, consistent command validation and atomic audit/replay handling. The [October 9 verification](docs/quality-assurance/fuhrpark-mcp-isolation-20261009.md) records **581 passing tests without skips** for that isolated delivery. This targeted verification does not replace a current full-project test run. Its documented catalog contains 56 MCP tools and 41 mapped screen actions; FIN-CLOSE against ADR-076 and payment run `open_high` remain listed as open business topics.

External acceptance, including live ELSTER/ERiC transmission, OIDC validation in the target environment and fiscalization, requires separate evidence. Existing adapters, simulations or documentation alone do not close these gates.

### Architecture and local development

Business scope covers agriculture and harvest settlement, contracts, sales, procurement, inventory and weighing, logistics and fleet, accounting, CRM, HR, documents and evidence. Consult the status files for implementation depth.

The central backend uses Python, FastAPI, SQLAlchemy, PostgreSQL and Alembic with **`main:app`** as its entry point. The frontend in `packages/frontend-web` uses React, TypeScript and Vite. Screens follow `ScreenDefinition` → `RenderPlan` → `useUniversalMaskRuntime` → `UniversalMaskRenderer`. Additional packages, services and NATS integrations follow the [architecture index](config/architecture-index.yaml). See the [architecture overview](docs/architecture/index.md), [ADRs](docs/adr/README.md) and [agent handbook](docs/agent-handbuch/index.md) for contracts and decisions.

Use Python 3.11 as in the backend development image, Node.js with Corepack, and **pnpm 9.12.0** as pinned in [package.json](package.json). Configure an existing PostgreSQL development environment and authentication using [.env.example](.env.example) and the [frontend environment template](packages/frontend-web/.env.example).

Run from the repository root against an already configured development database:

```sh
python -m venv .venv
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

In a second terminal:

```sh
corepack enable
pnpm install --frozen-lockfile
pnpm --filter @valero-neuroerp/frontend-web dev --host 127.0.0.1 --port 3000
```

Frontend: `http://localhost:3000`; API documentation: `http://localhost:8000/docs`. Configure the API base or proxy according to the selected Vite mode and environment variables.

Alternatively, [docker-compose.dev.yml](docker-compose.dev.yml) describes PostgreSQL, NATS, backend and frontend services on ports 8000/3000. Its [backend entrypoint](entrypoint.sh) initializes the database before starting the API. Check existing resources, database ownership and migration state before using it. This stack does not replace the shared test environment.

### Quality and contribution

Use the [checks listed above](#qualität-und-zusammenarbeit) for frontend types and tests, ERP domain tests, documentation governance, architecture validation and generated handbook consistency. Select backend tests according to the change.

**All agents must reuse `valeo_probe` or the configured `TEST_DATABASE_URL`. Do not create a database or Docker container per test, suite or agent.** First inspect the existing environment with `python scripts/pruefstand_db.py --status`. Running that script without an option resets the environment. Isolate test data with transactions/savepoints or owned records; coordinate migrations and resets. CI reuses the database supplied by its job. See the [shared test resource policy](docs/quality-assurance/test-database-resource-policy-20261001.md).

Read [AGENTS.md](AGENTS.md), the [session checklist](docs/agent-ops/session-start-checklist.md) and the workboard before editing. Check for existing solutions, claim your slice, update code/tests/documentation together and preserve other contributors' active changes. Obsolete development legacy may be removed after checking its consumers.

- [Documentation overview](docs/README.md)
- [User manual](docs/benutzerhandbuch/index.md)
- [Agent operations](docs/agent-ops/README.md)
- [Open findings](docs/project-context/open-gaps-and-known-issues.md)
- [MIT license](LICENSE)
