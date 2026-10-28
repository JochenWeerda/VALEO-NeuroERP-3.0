# VALEO NeuroERP 3.0

[Deutsch](#deutsch) · [English](#english)

## Deutsch

**VALEO NeuroERP verbindet Agrar- und Landhandelsprozesse mit einer Plattform für nachvollziehbare digitale Zusammenarbeit.** Das Projekt entwickelt ein ERP für Agrargenossenschaften und Landhandelsunternehmen: vom fachlichen Vorgang über die Oberfläche bis zu kontrollierten Schnittstellen für Automatisierung und KI-Agenten.

### Die Produktidee

- **Agrar im Mittelpunkt:** Kontrakte, Ernte und Abrechnung, Einkauf, Verkauf, Lager, Wiegen und Logistik gehören zum fachlichen Zielbild; Finanzbuchhaltung, CRM, Personal und Dokumente ergänzen es.
- **Ein gemeinsamer Prozesskern:** Fachaktionen, Regeln und Nachweise sollen über Oberflächen und agentenfähige Kanäle zusammenwirken. Mandanten- und Berechtigungsgrenzen sind Teil der Verträge.
- **Studio und wiederverwendbare Oberflächen:** Versionierte Definitionen und eine gemeinsame Masken-Runtime bilden die Grundlage für konsistente Arbeitsoberflächen. Das Ziel ist, fachliche Funktionen für Menschen und geeignete Automatisierungskanäle zugänglich zu machen.
- **Nachvollziehbare Automatisierung:** MCP und CLI erweitern die Bedienwege. Schreibaktionen benötigen die jeweils vorgesehenen Rollen, Prüfungen und Freigaben; der [MCP-Schreibstandard](docs/architecture/mcp-write-standard.md) beschreibt die Regeln.

### Unser Anspruch

VALEO verfolgt den Anspruch einer Premium-Plattform für den Agrarhandel: fachliche Tiefe in Agrarprozessen, durchgängige beleggebundene Agentenaktionen, versionierte Oberflächen und adaptive Arbeitsräume sollen zu einem gemeinsamen Arbeitsumfeld zusammenwachsen. Das ist das Produktziel; die Umsetzung und Freigabe erfolgen schrittweise je Prozess und Kanal.

### Mehrwert für den Agrarhandel

Unser Ziel ist, die bewährte Transaktionsstärke eines Premium-ERP um einen durchgängigen Arbeits- und Anpassungsraum zu erweitern:

- **Vom Kontrakt bis zur Abrechnung:** Waage, Qualitätsbewertung, Lager, Logistik und Finanzwirkung im fachlichen Zusammenhang bearbeiten.
- **Vom Anliegen zum Arbeitsablauf:** Im Dialog mit einem Agenten passende Masken und Prozessvorschläge entwickeln, versionieren, simulieren und gezielt freigeben.
- **Eine Fachaktion, mehrere Bedienwege:** Menschen, CLI und MCP sollen dieselben geprüften Domain-Commands mit denselben Mandanten- und Rollenregeln nutzen.
- **Arbeit nach Relevanz bündeln:** Adaptive Arbeitsräume sollen Belege, Freigaben, operative Ereignisse und nächste Schritte im jeweiligen Kontext zusammenführen.

Diese Kombination aus Agrarspezialisierung und kontrollierter Anpassbarkeit ist der angestrebte Mehrwert von VALEO. Konkrete Zeit-, Kosten- und Qualitätsvorteile werden anhand der jeweiligen Prozessabnahme bewertet.

### Plattform und nächste Entwicklungsziele

VALEO ist eine aktiv entwickelte Suite mit einem Python/FastAPI-Backend, einer React/TypeScript-Weboberfläche und Fachpaketen. Der [Process Kernel Status](docs/architecture/process-kernel/STATUS.md) dokumentiert gelieferte Prozesswellen. Die Roadmap umfasst unter anderem die fachliche Parität und Freigabe weiterer Studio-Masken, den adaptiven Arbeitsplatz sowie den Ausbau kontrollierter Agentenaktionen. Funktionsumfang und Reife unterscheiden sich je Prozess; externe Betriebs- und Fachfreigaben benötigen eigene Nachweise.

| Einblick | Quelle |
| --- | --- |
| Lieferstand und Prozesswellen | [Process Kernel Status](docs/architecture/process-kernel/STATUS.md) |
| Laufende Arbeit | [Active Workboard](docs/agent-ops/active-workboard.md) |
| Masken, Studio und Parität | [Universal Mask Runtime Status](docs/architecture/uix/universal-mask-runtime-status.md) · [Reparaturnachweis](docs/quality-assurance/migration-parity-repair-20261022.md) |
| Entwicklungsplanung und nächste Ausbauschritte | [Entwicklungsübersicht](docs/project-context/open-gaps-and-known-issues.md) |
| Betriebs- und externe Freigaben | [Production Readiness Runbook](docs/operations/production-readiness-runbook.md) |
| Architektur und Agenten | [Architekturindex](config/architecture-index.yaml) · [Agent-Handbuch](docs/agent-handbuch/index.md) |

### Lokal entwickeln

Voraussetzungen sind Python 3.11, Node.js mit Corepack und pnpm 9.12.0 sowie eine konfigurierte PostgreSQL-Entwicklungsumgebung. Umgebungsvariablen und Zugangsdaten anhand von [.env.example](.env.example) und der [Frontend-Vorlage](packages/frontend-web/.env.example) einrichten; Schema und Authentifizierung müssen zur Konfiguration passen.

Im Repository-Stamm mit einer bereits eingerichteten Entwicklungsdatenbank:

```sh
python -m venv .venv
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

In einem zweiten Terminal:

```sh
corepack enable
pnpm install --frozen-lockfile
pnpm --filter @valero-neuroerp/frontend-web dev --host 127.0.0.1 --port 3000
```

Frontend: `http://localhost:3000`; API-Dokumentation: `http://localhost:8000/docs`. API-Basis oder Proxy richten sich nach Vite-Modus und Frontend-Umgebung. Alternativ beschreibt [docker-compose.dev.yml](docker-compose.dev.yml) einen Entwicklungsstack; sein [Backend-Einstieg](entrypoint.sh) initialisiert die Datenbank. Vor Verwendung Ressourcen, Datenbankbesitz und Migrationsstand prüfen.

### Qualität und Zusammenarbeit

Für Änderungen gelten [AGENTS.md](AGENTS.md), [Startcheckliste](docs/agent-ops/session-start-checklist.md) und Workboard. Prüfungen und deren Ergebnisse gehören zum jeweiligen Lieferstand. Für datenbankabhängige Tests gilt der [gemeinsame Prüfstand](docs/quality-assurance/test-database-resource-policy-20261001.md): `valeo_probe` oder `TEST_DATABASE_URL` wiederverwenden und zunächst `python scripts/pruefstand_db.py --status` ausführen. Der Aufruf ohne Option setzt den Prüfstand zurück.

Weitere Einstiege: [Dokumentation](docs/README.md) · [Benutzerhandbuch](docs/benutzerhandbuch/index.md) · [Architektur](docs/architecture/index.md) · [MIT-Lizenz](LICENSE).

## English

**VALEO NeuroERP brings agricultural and trading processes together with a platform for accountable digital collaboration.** It is an ERP project for agricultural cooperatives and agricultural trading businesses, connecting domain workflows, user interfaces and controlled interfaces for automation and AI agents.

### Product direction

The domain vision spans contracts, harvest and settlement, procurement, sales, inventory, weighing and logistics, complemented by accounting, CRM, HR and documents. A shared process kernel, tenant and permission contracts, and versioned Studio screen definitions provide the foundations for consistent workflows. MCP and CLI extend the ways users and agents can interact with selected functions; write actions remain subject to their applicable authorization and approval rules.

### Our ambition

VALEO aims to become a premium platform for agricultural trade by bringing together domain depth in agriculture, end-to-end document-linked agent actions, versioned interfaces and adaptive workspaces. This is the product direction; implementation and release proceed incrementally by process and channel.

### Value for agricultural trade

Our goal is to extend the transaction strength expected from premium ERP with a connected workspace for execution and adaptation: contract-to-settlement agricultural workflows; conversational design of versioned screens and processes with simulation and approval; the same governed domain commands for people, CLI and MCP; and contextual workspaces connecting documents, approvals, operational events and next actions. This combination of agricultural specialization and controlled adaptability is VALEO's intended value proposition. Time, cost and quality benefits are assessed per accepted workflow.

### Platform and next development goals

VALEO is an actively developed suite with a Python/FastAPI backend, a React/TypeScript frontend and domain packages. The [Process Kernel Status](docs/architecture/process-kernel/STATUS.md) documents delivered process waves. The roadmap includes functional parity and release of further Studio screens, the adaptive workspace and expanded controlled agent actions. Scope and maturity vary by workflow; external operational and domain approvals require separate evidence. See the [runtime status](docs/architecture/uix/universal-mask-runtime-status.md), [development roadmap](docs/project-context/open-gaps-and-known-issues.md), [workboard](docs/agent-ops/active-workboard.md) and [production readiness runbook](docs/operations/production-readiness-runbook.md).

For local setup, use the [commands above](#lokal-entwickeln) with Python 3.11, Node.js/Corepack, pnpm 9.12.0 and an already configured PostgreSQL development database. Configure the supplied environment templates first. For database tests, reuse the shared environment and follow the [resource policy](docs/quality-assurance/test-database-resource-policy-20261001.md). Start contributions with [AGENTS.md](AGENTS.md) and the [documentation overview](docs/README.md).
