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
| Doku-Stand | `2026-05-16` |
| Produktreife | aktive Entwicklung, nicht allgemein produktionsreif |
| Frontend TypeScript | 0 Fehler |
| Backend-Testabdeckung | ~43 % gesamt; kritische Kernpfade über Ratchet-Schwellen |
| Alembic | 1 Head |
| Service-Layer | vollständig refaktoriert — alle Endpoints auf thin-router + Service-Klassen |
| Docker-Erstinstallation | abgesichert mit Alembic-Bootstrap und Schema-Prüfung |

Der belastbare Ist-Zustand liegt in:

- [Process Kernel Status](docs/architecture/process-kernel/STATUS.md)
- [Open Gaps and Known Issues](docs/project-context/open-gaps-and-known-issues.md)
- [Active Workboard](docs/agent-ops/active-workboard.md)

### Was das System heute abdeckt

- **12+ Fachdomänen**: Agrar (Ernteannahme, Kontrakte, Trocknungsregeln), Verkauf, Einkauf, Lager, Finanzen/FIBU, CRM, Logistik, Compliance, HRM, POS, Futtermittel/Rationsoptimierung
- **Multi-Tenancy** via `X-Tenant-ID` Header, OIDC-Authentifizierung (Keycloak/Azure AD/Auth0)
- **Prozesskernel** — 17 Waves abgeschlossen, 903 Tests grün
- **Service-Layer** — alle Endpoints auf dünnen Router + domänenspezifische Service-Klassen umgestellt
- **React-Frontend** mit Mask-Builder-Framework (ObjectPage, ListReport, Wizard, Worklist)
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
- Vollständig refaktorierter Service-Layer (thin-router + Domain-Services)
- Prozesskernel mit 17 abgeschlossenen Waves, 903 Tests
- HRM-Betriebsfreigabe-Gates mit ausfüllbaren Vorlagen
- Abgesicherter Alembic-/Docker-Erstinstallationspfad
- UX-Baukasten vollständig ausgerollt (Seitentyp-Logik)

**Bewusst noch offen:**
- Backend-Gesamtabdeckung ~43 % (kritische Pfade über Ratchet gesichert)
- NATS/Event-Bus läuft nicht standardmäßig im Dev-Betrieb
- Einige Live-Integrationen benötigen externe Credentials und Ops-Setups
- Fachliche Tiefe der Domänen ist nicht überall gleich

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
| Docs date | `2026-05-16` |
| Maturity | active development, not generally production-ready |
| Frontend TypeScript | 0 errors |
| Backend test coverage | ~43 % overall; critical paths secured via ratchet |
| Alembic | 1 head |
| Service layer | fully refactored — all endpoints on thin-router + service classes |
| Docker first install | secured with Alembic bootstrap and schema validation |

Authoritative status documents:

- [Process Kernel Status](docs/architecture/process-kernel/STATUS.md)
- [Open Gaps and Known Issues](docs/project-context/open-gaps-and-known-issues.md)
- [Active Workboard](docs/agent-ops/active-workboard.md)

### What the System Covers Today

- **12+ business domains**: Agrar (harvest acceptance, contracts, drying rules), Sales, Procurement, Inventory, Finance/Accounting, CRM, Logistics, Compliance, HRM, POS, Feed/Ration Optimization
- **Multi-tenancy** via `X-Tenant-ID` header, OIDC authentication (Keycloak/Azure AD/Auth0)
- **Process kernel** — 17 waves completed, 903 tests green
- **Service layer** — all endpoints refactored to thin routers + domain service classes
- **React frontend** with Mask Builder Framework (ObjectPage, ListReport, Wizard, Worklist)
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
- Fully refactored service layer (thin-router + domain services)
- Process kernel with 17 completed waves, 903 tests
- HRM operating-release gates with fillable template packages
- Secured Alembic/Docker first-install path
- UX component kit fully rolled out (page-type logic)

**Intentionally still open:**
- Overall backend coverage ~43 % (critical paths secured via ratchet)
- NATS/event bus not started by default in dev mode
- Some live integrations require external credentials and ops setup
- Domain depth is not uniform across all areas

All open items are fully documented in [open-gaps-and-known-issues.md](docs/project-context/open-gaps-and-known-issues.md).

### Third-Party Licenses

This repository includes integration support for `superglue-ai/superglue` (license: `FSL-1.1-Apache-2.0`).
Local attribution: [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)

### License

[MIT License](LICENSE) — unless documented otherwise in specific sub-areas.
