# VALEO NeuroERP 3.0

![Deploy Staging](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/workflows/deploy-staging.yml/badge.svg)
![Security Scan](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/workflows/security-scan.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-blue)
![Version](https://img.shields.io/badge/version-3.0.0--alpha-blue)

VALEO NeuroERP ist ein mehrdomäniges ERP- und Automatisierungs-Repository mit Schwerpunkt auf Landhandel, Agrarhandel, FIBU-nahe Operatorräume, Prozesskernel und agentische Assistenz.

Diese README ist der Einstiegspunkt für lokale Nutzung und Orientierung. Sie ist bewusst keine operative Source of Truth für Lieferstand oder Reifegrad.

## Aktueller Status

- Stand der Doku: `2026-04-12`
- Produktreife: `in aktiver Entwicklung`, nicht allgemein als produktionsreif zu bewerten
- Frontend-TypeScript: `0 Fehler`
- Backend-Testabdeckung: `ca. 45%`
- Alembic: `1 Head`
- Docker-Erstinstallation: auf leerer Postgres-DB mit Alembic-Bootstrap und Strukturprüfung abgesichert

Der belastbare Ist-Zustand liegt in:

- [Process Kernel Status](docs/architecture/process-kernel/STATUS.md)
- [Open Gaps and Known Issues](docs/project-context/open-gaps-and-known-issues.md)
- [Active Workboard](docs/agent-ops/active-workboard.md)

## Was das Repository heute abdeckt

- Mehrdomänige ERP-Struktur mit separaten Domain-Schemas in PostgreSQL
- React-/TypeScript-Frontend mit breiten Fachmasken und Fiori-artig verdichteten Operatorräumen
- FastAPI-Backend mit Multi-Tenancy, OIDC, RAG, Prozesskernel und Admin-/Agent-Ops-Surfaces
- Docker-, Staging- und Dev-Compose-Pfade
- Self-hosted Integrations- und Agentik-Bausteine wie Superglue, Voice-Kanal und konfigurierbarer Event Bus

Die Struktur ist breit, aber nicht in allen Domänen gleich tief ausgebaut. Offene Restthemen sind bewusst in [open-gaps-and-known-issues.md](docs/project-context/open-gaps-and-known-issues.md) dokumentiert.

## Architektur in Kürze

- Frontend: React 18, TypeScript, Vite
- Backend: FastAPI, SQLAlchemy, Alembic
- Datenhaltung: PostgreSQL 15, Redis 7
- Identität: OIDC / Keycloak / JWT
- Eventing: NATS JetStream, derzeit standardmäßig deaktiviert, aber per Config aktivierbar
- Wissens- und Assistenzschicht: ChromaDB/RAG, Agent-Ops, Voice, Superglue-Integration

Wichtige Paketbereiche:

- `packages/frontend-web`: Web-Frontend
- `app/`: FastAPI-Anwendung, Services, Modelle, Endpunkte
- `alembic/`: Datenbankmigrationen
- `docs/`: Architektur-, Workflow-, QA- und Delivery-Dokumentation
- `scripts/`: Bootstrap-, Smoke-, Prüf- und Hilfsskripte

## Mehrdomänige ERP-Struktur

Die aktuelle Erstinstallation erzeugt und prüft zentrale ERP-Schemas, unter anderem:

- `domain_shared`
- `domain_crm`
- `domain_erp`
- `domain_inventory`
- `domain_einkauf`
- `domain_sales`
- `domain_finance`
- `domain_ops`
- `domain_docflow`
- `domain_agrar`
- `domain_controlling`

Das spiegelt die Zielstruktur eines mehrdomänigen ERP wider. Historisch gewachsene Zuordnungen einzelner Tabellen können fachlich noch nachgeschärft werden; das ist kein Bootstrap-Fehler.

## Schnellstart mit Docker

### Voraussetzungen

- Docker Desktop oder Docker Engine mit Compose
- Git

### Minimaler lokaler Start

Für eine lokale Erstinstallation genügt der Compose-Start. Das Backend führt den Alembic-Bootstrap selbst aus und startet nur bei erfolgreicher Migration.

```bash
docker compose up -d postgres redis keycloak backend frontend-web
```

Wichtige lokale Endpunkte:

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- Backend OpenAPI: `http://localhost:8000/docs`
- Keycloak: `http://localhost:8080`
- pgAdmin: `http://localhost:5050`

Hinweis:

- `frontend-web` hängt im Dev-Setup an weiteren Diensten wie `bff-web` und `dev-sse`. Für den vollständigen lokalen UI-Stack ist in der Regel der komplette Compose-Start sinnvoll:

```bash
docker compose up -d
```

## Erstinstallation und Migrationssicherheit

Der relevante Punkt für frische GitHub-Spiegel ist jetzt abgesichert:

- `python scripts/init_db.py` läuft auf leerer Postgres-DB bis `head`
- `python scripts/check_alembic_single_head.py` bestätigt einen einzelnen Alembic-Head
- `python scripts/check_required_domain_schemas.py` prüft zentrale ERP-Domänen und Kernobjekte
- `scripts/smoke_first_install_docker.ps1` und `scripts/smoke_first_install_docker.sh` liefern reproduzierbare Docker-Smokes

Wichtig:

- Migrationsfehler werden im Docker-Pfad nicht mehr still geschluckt
- Legacy-SQL-Parallelpfade sind aus dem Dev-Erststart entfernt
- Der Backend-Start hängt im Container an `python scripts/init_db.py`

## Nützliche lokale Prüfungen

```bash
pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false
node scripts/docs-governance-check.cjs
python scripts/check_alembic_single_head.py
python scripts/check_required_domain_schemas.py
```

PowerShell-Beispiel für den Docker-Erstinstallations-Smoke:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/smoke_first_install_docker.ps1 -HostPort 55434
```

## Doku-Startreihenfolge für Entwickler und Agenten

1. [docs/README.md](docs/README.md)
2. [AGENTS.md](AGENTS.md)
3. [Process Kernel Status](docs/architecture/process-kernel/STATUS.md)
4. [Agent Ops README](docs/agent-ops/README.md)
5. [Active Workboard](docs/agent-ops/active-workboard.md)
6. [Open Gaps and Known Issues](docs/project-context/open-gaps-and-known-issues.md)

## Reifegrad ehrlich eingeordnet

Belastbar vorhanden:

- breiter Domänenschnitt des ERP
- operatives Arbeitsmodell in vielen priorisierten Kernmasken
- Prozesskernel mit dokumentierten Waves
- Agent-Ops- und Superglue-Adminflächen
- abgesicherter Alembic-/Docker-Erstinstallationspfad

Bewusst noch offen oder nur teilweise produktiv:

- Backend-Testabdeckung ist für ein ERP noch zu niedrig
- NATS/Event-Bus läuft nicht standardmäßig im Dev-Betrieb
- einige Live-Integrationen hängen weiter an externen Credentials, Zielsystemen und Ops-Setups
- nicht jede Domäne ist fachlich gleich tief ausgebaut

## Third-Party Licensing Notes

Dieses Repository enthält Integrations- und Deployment-Support für das Drittprojekt `superglue-ai/superglue`.

- Upstream-Lizenz: `FSL-1.1-Apache-2.0`
- Upstream-Lizenzdatei: <https://github.com/superglue-ai/superglue/blob/main/LICENSE>
- Lokaler Attribution-Hinweis: [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)

Wenn Kopien, Änderungen oder Derivate von Superglue mit diesem Repository weitergegeben werden, müssen die jeweiligen Copyright- und Lizenzhinweise erhalten bleiben.

## Lizenz

Für dieses Repository selbst gilt, sofern nicht in Teilbereichen abweichend dokumentiert:

- [MIT License](LICENSE)
