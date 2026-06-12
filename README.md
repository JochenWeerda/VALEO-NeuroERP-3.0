# VALEO NeuroERP 3.0

![Deploy Staging](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/workflows/deploy-staging.yml/badge.svg)
![Security Scan](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/workflows/security-scan.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-blue)
![Version](https://img.shields.io/badge/version-3.0.0--alpha-blue)

---

> 🇩🇪 [Deutsche Version](#deutsch) | 🇬🇧 [English Version](#english)

---

<a name="deutsch"></a>
## 🇩🇪 Deutsch

VALEO NeuroERP 3.0 ist ein mehrdomäniges ERP-System für Agrargenossenschaften und Landhandelsunternehmen. Der Fokus liegt auf prozessdurchgängiger Landhandels-Exzellenz, agentenfähiger Facharchitektur und schneller Prozess-UX — kein generisches Horizontal-ERP.

### Aktueller Status

| Kennzahl | Stand |
|----------|-------|
| Doku-Stand | `2026-06-12` |
| Produktreife | aktive Entwicklung, nicht allgemein produktionsreif |
| Frontend TypeScript | 0 Fehler |
| Backend-Testabdeckung | 64,85 % gesamt; 18/18 kritische Ratchet-Pfade grün |
| Domänentiefe | `DOM-*-004`-Welle abgeschlossen: Kontrakte, O2C, FIBU, Beschaffung, Nachweisraum, Lieferkette je auf voller Tiefe ([Übersicht](docs/dom-004-spine-buildout-2026-06-12.md)) |
| Alembic | 1 Head (`merge_doc_proc_20260612`) |
| Service-Layer | Bekannte große Legacy-Endpunkte repo-seitig auf dedizierte Services nachgezogen |
| Docker/Container | Erstinstallation, Keycloak-DB-Bootstrap und mehrere Healthcheck-/CRM-/Inventory-Fixes nachgezogen |
| Production Release | Harte CI-/Security-Gates, SBOM, getrennte immutable Backend-/Frontend-Images, atomarer Helm-Rollout |
| UAT | Abgenommen mit dokumentierten externen Gates; repo-seitige UAT-Auflagen nachgeliefert |

Der belastbare Ist-Zustand liegt in:

- [Process Kernel Status](docs/architecture/process-kernel/STATUS.md)
- [Open Gaps and Known Issues](docs/project-context/open-gaps-and-known-issues.md)
- [Active Workboard](docs/agent-ops/active-workboard.md)
- [UAT Master Plan](docs/uat/UAT-MASTER-PLAN.md)
- [Production Readiness Runbook](docs/operations/production-readiness-runbook.md)
- [Meridian Design Concept](docs/design/DESIGN-KONZEPT-1-MERIDIAN.md)

### Was das System heute abdeckt

- **12+ Fachdomänen**: Agrar (Ernteannahme, Kontrakte, Trocknungsregeln), Verkauf, Einkauf, Lager, Finanzen/FIBU, CRM, Logistik, Compliance, HRM, POS, Futtermittel/Rationsoptimierung
- **Prozessdurchgängige Domänentiefe (`DOM-*-004`)** — operative Endlogik nachgezogen: Kontrakt-Fixierung/MATIF/Settlement, O2C Match→Kreditlimit→Storno/Gutschrift, FIBU Mahnlauf→Auszifferung→Periodenabschluss→DATEV, GoBD-Nachweisraum (Upload/Freigabe/Wiedervorlage/Export), P2P 3-Wege-Match/ERS/RFQ, Lieferketten-Rückverfolgbarkeit — je mit Live-UAT verifiziert ([Übersicht](docs/dom-004-spine-buildout-2026-06-12.md))
- **Multi-Tenancy** via `X-Tenant-ID` Header, OIDC-Authentifizierung (Keycloak/Azure AD/Auth0)
- **Prozesskernel** — Waves 1–104 abgeschlossen, 8564 Tests grün
- **Service-Layer** — zentrale Refaktorierungswellen abgeschlossen; `harvest_acceptance.py`, `agrar_settlements.py` und `docflow.py` sind auf dedizierte Services nachgezogen
- **React-Frontend** mit Mask-Builder-Framework (ObjectPage, ListReport, Wizard, Worklist)
- **Meridian UI** — Root-Theme aktiv, Navy-Sidebar, 56px Topbar, 44px Button/Input-Ziele und tokenisierte Dashboard-/ListReport-/Kernscreen-Muster
- **Event-Bus** via NATS JetStream mit Outbox-Pattern
- **Agent-Ops**, Voice-Kanal, RAG/Wissensbase, Superglue-Integration

### Architektur

| Schicht | Technologie |
|---------|-------------|
| Frontend | React 18, TypeScript 5.5, Vite 5.4, Tailwind CSS, Radix UI, Zustand, TanStack Query |
| Backend | Python 3.11+, FastAPI, SQLAlchemy 2.0, Alembic, Pydantic 2.x |
| Datenbank | PostgreSQL 15+, Redis 7 |
| Authentifizierung | OIDC / Keycloak / JWT |
| Eventing | NATS JetStream (Outbox-Pattern) |
| Infrastruktur | Docker Compose, Helm/Kubernetes-Pfade vorhanden |
| Wissensschicht | ChromaDB/RAG, Agent-Ops, Superglue |

Wichtige Verzeichnisse:

- `packages/frontend-web/` — React-Frontend
- `app/` — FastAPI-Backend, Services, Modelle, Endpoints
- `app/services/` — Domain-Service-Klassen (thin-router pattern)
- `modules/agrar/` — Agrar-Vertikalmodul
- `alembic/` — Datenbankmigrationen
- `docs/` — Architektur-, QA- und Delivery-Dokumentation
- `scripts/` — Bootstrap-, Smoke- und Prüfskripte

### Domänen-Schemas in PostgreSQL

`domain_shared`, `domain_crm`, `domain_erp`, `domain_inventory`, `domain_einkauf`, `domain_sales`, `domain_finance`, `domain_ops`, `domain_docflow`, `domain_agrar`, `domain_controlling`

### Schnellstart mit Docker

**Voraussetzungen:** Docker Desktop, Git

```bash
# Vollständiger Stack
docker compose up -d

# Nur Backend + Postgres (leichtgewichtig)
docker compose -f docker-compose.dev.yml up -d
```

Lokale Endpunkte:

| Dienst | URL |
|--------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| OpenAPI Docs | http://localhost:8000/docs |
| Keycloak | http://localhost:8080 |
| pgAdmin | http://localhost:5050 |

### Lokale Entwicklung (ohne Docker)

```bash
# Backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Datenbankmigrationen
alembic upgrade head

# Tests
pytest
pytest --cov=app --cov-report=term

# Frontend
cd packages/frontend-web
npm install
npm run dev   # Port 3001
```

### Erstinstallation und Migrationssicherheit

```bash
python scripts/init_db.py
python scripts/check_alembic_single_head.py
python scripts/check_required_domain_schemas.py
pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false
```

Docker-Smoke:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/smoke_first_install_docker.ps1 -HostPort 55434
```

### Reifegrad

**Belastbar vorhanden:**
- Breiter Domänenschnitt über 12+ ERP-Bereiche
- `DOM-*-004`-Tiefenwelle (Kontrakte, O2C, FIBU, Beschaffung, Nachweisraum, Lieferkette) auf voller Tiefe `.2`–`.5`, je mit reinen Logik-Unit-Tests und Live-UAT (mit DB-Restore) verifiziert
- Prozesskernel mit Waves 1–104 abgeschlossen, 8564 Tests im letzten formalen Kernel-Status
- Backend-Abdeckung 64,85 % im letzten formalen Kernel-Status; kritische Ratchet-Pfade grün
- Service-Layer-Hauptwellen, Base-Worker/-Repository, Domain-Error-Konzept und dedizierte Services fuer die bekannten grossen Legacy-Endpunkte
- Meridian-Shell und sichtbare Core-UI auf `localhost:3000`
- HRM-Betriebsfreigabe-Gates mit ausfüllbaren Vorlagen
- UAT-Dokumentation mit Masterplan, Traceability, API-Contracts und Playwright-UAT-Evidence
- Abgesicherter Alembic-/Docker-Erstinstallationspfad inklusive Keycloak-Datenbank-Bootstrap
- UX-Baukasten vollständig ausgerollt (Seitentyp-Logik)

**Bewusst noch offen:**
- Tiefe Modulunterseiten enthalten noch harte Tailwind-Farben und brauchen weitere Meridian-Slices
- Externe Gates bleiben außerhalb des Repos: echte UAT-Unterschriften, Steuerberater-/DATEV-Mapping, DMS-Live-Probe, TSE-/DSFinV-K-Prüfwerkzeug, ERiC/ELSTER und Provider-Credentials
- Fachliche Tiefe der Domänen ist nicht überall gleich und wird über Gap-/Parity-Dokumente weitergeführt

Offene Punkte sind vollständig in [open-gaps-and-known-issues.md](docs/project-context/open-gaps-and-known-issues.md) dokumentiert.

### Drittlizenzen

Dieses Repository enthält Integrations-Support für `superglue-ai/superglue` (Lizenz: `FSL-1.1-Apache-2.0`).
Lokaler Hinweis: [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)

### Lizenz

[MIT License](LICENSE) — sofern in Teilbereichen nicht abweichend dokumentiert.

---

<a name="english"></a>
## 🇬🇧 English

VALEO NeuroERP 3.0 is a multi-domain ERP system for agricultural cooperatives and grain trading companies. The focus is on end-to-end agricultural trading excellence, agent-capable domain architecture, and fast process UX — not a generic horizontal ERP.

### Current Status

| Metric | As of |
|--------|-------|
| Docs date | `2026-06-12` |
| Maturity | active development, not generally production-ready |
| Frontend TypeScript | 0 errors |
| Backend test coverage | 64.85 % overall; 18/18 critical ratchet paths green |
| Domain depth | `DOM-*-004` wave completed: contracts, O2C, accounting, procurement, evidence room, supply chain at full depth ([overview](docs/dom-004-spine-buildout-2026-06-12.md)) |
| Alembic | 1 head (`merge_doc_proc_20260612`) |
| Service layer | known large legacy endpoints have repo-side dedicated services |
| Docker/containers | first install, Keycloak DB bootstrap and several healthcheck/CRM/Inventory fixes delivered |
| Production release | hard CI/security gates, SBOM, separate immutable backend/frontend images, atomic Helm rollout |
| UAT | accepted with documented external gates; repo-side UAT conditions delivered |

Authoritative status documents:

- [Process Kernel Status](docs/architecture/process-kernel/STATUS.md)
- [Open Gaps and Known Issues](docs/project-context/open-gaps-and-known-issues.md)
- [Active Workboard](docs/agent-ops/active-workboard.md)
- [UAT Master Plan](docs/uat/UAT-MASTER-PLAN.md)
- [Production Readiness Runbook](docs/operations/production-readiness-runbook.md)
- [Meridian Design Concept](docs/design/DESIGN-KONZEPT-1-MERIDIAN.md)

### What the System Covers Today

- **12+ business domains**: Agrar (harvest acceptance, contracts, drying rules), Sales, Procurement, Inventory, Finance/Accounting, CRM, Logistics, Compliance, HRM, POS, Feed/Ration Optimization
- **End-to-end domain depth (`DOM-*-004`)** — operational endgame logic delivered: contract fixing/MATIF/settlement, O2C match→credit limit→cancellation/credit note, accounting dunning→clearing→period close→DATEV, GoBD evidence room (upload/release/follow-up/export), P2P three-way match/ERS/RFQ, supply-chain traceability — each verified by live UAT ([overview](docs/dom-004-spine-buildout-2026-06-12.md))
- **Multi-tenancy** via `X-Tenant-ID` header, OIDC authentication (Keycloak/Azure AD/Auth0)
- **Process kernel** — Waves 1–104 completed, 8564 tests green
- **Service layer** — central refactoring waves completed; `harvest_acceptance.py`, `agrar_settlements.py` and `docflow.py` are backed by dedicated services
- **React frontend** with Mask Builder Framework (ObjectPage, ListReport, Wizard, Worklist)
- **Meridian UI** — root theme active, navy sidebar, 56px top bar, 44px button/input targets and tokenized dashboard/list-report/core-screen patterns
- **Event bus** via NATS JetStream with outbox pattern
- **Agent-Ops**, voice channel, RAG/knowledge base, Superglue integration

### Architecture

| Layer | Technology |
|-------|------------|
| Frontend | React 18, TypeScript 5.5, Vite 5.4, Tailwind CSS, Radix UI, Zustand, TanStack Query |
| Backend | Python 3.11+, FastAPI, SQLAlchemy 2.0, Alembic, Pydantic 2.x |
| Database | PostgreSQL 15+, Redis 7 |
| Auth | OIDC / Keycloak / JWT |
| Eventing | NATS JetStream (outbox pattern) |
| Infrastructure | Docker Compose, Helm/Kubernetes paths available |
| Knowledge layer | ChromaDB/RAG, Agent-Ops, Superglue |

Key directories:

- `packages/frontend-web/` — React frontend
- `app/` — FastAPI backend, services, models, endpoints
- `app/services/` — domain service classes (thin-router pattern)
- `modules/agrar/` — Agrar vertical module
- `alembic/` — database migrations
- `docs/` — architecture, QA and delivery documentation
- `scripts/` — bootstrap, smoke and validation scripts

### PostgreSQL Domain Schemas

`domain_shared`, `domain_crm`, `domain_erp`, `domain_inventory`, `domain_einkauf`, `domain_sales`, `domain_finance`, `domain_ops`, `domain_docflow`, `domain_agrar`, `domain_controlling`

### Quick Start with Docker

**Prerequisites:** Docker Desktop, Git

```bash
# Full stack
docker compose up -d

# Backend + Postgres only (lightweight)
docker compose -f docker-compose.dev.yml up -d
```

Local endpoints:

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| OpenAPI Docs | http://localhost:8000/docs |
| Keycloak | http://localhost:8080 |
| pgAdmin | http://localhost:5050 |

### Local Development (without Docker)

```bash
# Backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Database migrations
alembic upgrade head

# Tests
pytest
pytest --cov=app --cov-report=term

# Frontend
cd packages/frontend-web
npm install
npm run dev   # port 3001
```

### First Install & Migration Safety

```bash
python scripts/init_db.py
python scripts/check_alembic_single_head.py
python scripts/check_required_domain_schemas.py
pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false
```

Docker smoke test:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/smoke_first_install_docker.ps1 -HostPort 55434
```

### Maturity Assessment

**Solid and working:**
- Broad domain coverage across 12+ ERP areas
- `DOM-*-004` depth wave (contracts, O2C, accounting, procurement, evidence room, supply chain) at full depth `.2`–`.5`, each verified with pure-logic unit tests and live UAT (with DB restore)
- Process kernel with Waves 1–104 completed, 8564 tests in the latest formal kernel status
- Backend coverage 64.85 % in the latest formal kernel status; critical ratchet paths green
- Main service-layer waves, BaseWorker/BaseRepository, domain error model and dedicated services for the known large legacy endpoints
- Meridian shell and visible core UI on `localhost:3000`
- HRM operating-release gates with fillable template packages
- UAT documentation with master plan, traceability, API contracts and Playwright UAT evidence
- Secured Alembic/Docker first-install path including Keycloak database bootstrap
- UX component kit fully rolled out (page-type logic)

**Intentionally still open:**
- Deep module pages still contain hard-coded Tailwind colors and need further Meridian slices
- External gates remain outside the repository: real UAT signatures, tax-advisor/DATEV mapping, DMS live probe, TSE/DSFinV-K validation tooling, ERiC/ELSTER and provider credentials
- Domain depth is not uniform across all areas and remains tracked through gap/parity documents

All open items are fully documented in [open-gaps-and-known-issues.md](docs/project-context/open-gaps-and-known-issues.md).

### Third-Party Licenses

This repository includes integration support for `superglue-ai/superglue` (license: `FSL-1.1-Apache-2.0`).
Local attribution: [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)

### License

[MIT License](LICENSE) — unless documented otherwise in specific sub-areas.
