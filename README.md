# VALEO NeuroERP 3.0

![Quality Gate](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/workflows/quality-gate.yml/badge.svg?branch=main)
![Security Scan](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/workflows/security-scan.yml/badge.svg?branch=main)
![Universal Mask CI](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/workflows/universal-mask-ci.yml/badge.svg?branch=main)
![Runtime Sweep](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/workflows/runtime-sweep.yml/badge.svg?branch=main)
![Deploy Staging](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/workflows/deploy-staging.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-blue)
![Version](https://img.shields.io/badge/version-3.0.0--beta-orange)

---

> 🇩🇪 [Deutsche Version](#deutsch) | 🇬🇧 [English Version](#english)

---

<a name="deutsch"></a>
## 🇩🇪 Deutsch

VALEO NeuroERP 3.0 ist ein mehrdomäniges ERP-System für Agrargenossenschaften und Landhandelsunternehmen. Der Fokus liegt auf prozessdurchgängiger Landhandels-Exzellenz, agentenfähiger Facharchitektur und schneller Prozess-UX — kein generisches Horizontal-ERP.

---

### Aktueller Status

| Kennzahl | Stand |
|----------|-------|
| Doku-Stand | `2026-07-06` |
| Produktreife | **Beta** — Kernprozesse operativ, externe Go-Live-Gates offen |
| CI (GitHub Actions, `main`) | **quality-gate, security-scan, universal-mask-ci, runtime-sweep grün** (2026-07-06, Run 28788983957 auf `c2df41595`) — Evidenz: `artifacts/ci-green-evidence.md` |
| Doku-Code-Drift | **0 Items** (`python scripts/doc_drift_report.py --fail-over 0`, 2026-07-06) |
| Release-Evidence | **WARN** — 4 PASS / 2 WARN / 0 FAIL (`artifacts/release_evidence.json`, SHA `1772798e0`) |
| Mask-CommandEndpoints | **26 native SDs, 0 stubReason** (SPEC-P1-04, Inventur-Skript) |
| Frontend TypeScript | 0 Fehler (`tsc --noEmit`) |
| Backend-Tests | **11 943 passed** im CI-Volllauf (2026-07-06), 0 Fehler |
| Kritische Coverage-Ratchets | grün, **only-up-Politik** (`config/coverage_ratchet_baseline.json`, Absenkung = CI-Fehler) |
| Backend-Gesamtabdeckung | 65,66 % (Ziel langfristig ≥ 80 %) |
| OpenAPI-Routen | **2 537 Pfade** / 3 274 Operationen mit `summary=` (100 %) |
| Alembic | 1 Head (`inv_lot_depth_spec_p1_08`), Fresh-DB-Drift geschlossen |
| Runtime-API-Sweep | **Nightly-Gate 0×5xx** über alle parameterlosen GET-Routen gegen frisch migrierte DB (`scripts/api_runtime_sweep.py`) |
| Audit-Readiness | ISO-27001 Annex A 93/93 + SOC-2-TSC-Matrix (`config/audit/`), Orchestrator `audit-simulation.yml` |
| Domänentiefe | DOM-\*-004 abgeschlossen: Kontrakte, O2C, FIBU, P2P, Nachweisraum, Lieferkette |
| Architektur-Doku | arc42 (12 Kapitel), C4 Context/Container/Components, 42 ADRs |
| Workflow-Cockpit | MVP + Retry/Kompensation + NATS-Projektor + Dead-Letter-Sicht |

---

### Reifegrad: Was fehlt bis Production?

#### Repo-seitig bereit ✅
- Breiter Domänenschnitt über 12+ ERP-Bereiche mit operativer Endlogik
- OIDC-Auth, Multi-Tenancy, Bearer-Token-Enforcement, RFC-7807 Fehlermodell
- Harte CI-Gates: TypeScript, ESLint, pytest-Ratchet, Security-Scan, SBOM
- Unveränderliche SHA-Images, Helm-Rollout, `/healthz`/`/readyz`-Smoke
- Alembic single head, idempotente Migrationen, Keycloak-DB-Bootstrap
- GoBD-Nachweisraum, DATEV-Export, UStVA-Übermittlungs-Client
- POS mit TSE-Simulation (Fiskaly-Anbindung vorbereitet)
- Vollständige UAT-Dokumentation, Playwright-E2E-Evidence, Traceability-Matrix

#### Externe Go-Live-Gates ⏳ (Betriebsverantwortung)
| Gate | Zuständigkeit |
|------|--------------|
| Produktive Keycloak-/OIDC-Credentials | Betrieb |
| TSE-Hardware-Abnahme & DSFinV-K-Zertifizierung | Betrieb / Fiskalisierungs-Provider |
| ERiC/ELSTER-Live-Übermittlung | Steuerberater + DATEV-Cutover-Mapping |
| DMS Paperless-ngx Live-Probe | Betrieb |
| Staging-Domain + DNS + TLS-Zertifikat | Betrieb |
| Backup-/Restore-Drill (15-min RTO) | Betrieb |
| Erntepeak-Lasttest auf Staging | Betrieb (k6, `load-test.yml`) |
| Reale UAT-Unterschriften | Fachbereich + Geschäftsführung |
| DSGVO-DSB-Freigabe | Datenschutzbeauftragter |

Die vollständige Gate-Liste: [`docs/operations/production-readiness-runbook.md`](docs/operations/production-readiness-runbook.md)

---

### Was das System heute abdeckt

**12+ Fachdomänen mit operativer Tiefe:**

| Domäne | Tiefe |
|--------|-------|
| Agrar | Ernteannahme, Waage, Kontrakte (MATIF/Fixing), Trocknungsregeln, Selbstabrechnung, Partie-Aggregation |
| Verkauf (O2C) | Angebot → Auftrag → Lieferschein → Rechnung, Positions-Match, Kreditlimit, Storno/Gutschrift |
| Einkauf (P2P) | RFQ → Bestellung → Wareneingang → 3-Wege-Match, ERS, Rechnungsprüfung |
| Lager/WMS | Bestandsführung, Silozellen, Materialfluss, Chargen-Rückverfolgung, QS-Leitstand |
| FIBU | Mahnlauf, OP-Auszifferung, Periodenabschluss, DATEV-Export, UStVA, Atlas/Zoll |
| CRM / KIM | 360°-Cockpit (KIM), Kaufverhalten-Klassifikation, Auto-Capture (E-Mail/Telefon), TAPI |
| Logistik | Frachtbriefe, Tourenplanung, ePOD, Fahrerzeiterfassung |
| Compliance | GoBD-Nachweisraum, LkSG, DSGVO Art. 30/33, Gefahrgut, Zoll/Atlas, VVVO |
| HRM | Personalakte, Abwesenheit (ArbZG), Zeiterfassung, Lohnabrechnung (DE), Planungswizard |
| POS | Kassenabschluss, TSE-Simulation, DSFinV-K-Vorbereitung, Retoure |
| Futtermittel | Rezeptur, Rationsoptimierung (Tierwohl), Produktionsfreigabe, Inventory-Link |
| Agent-Ops / KI | Workflow-Cockpit, MCP-Tool-Registry, LLM-Gateway, Voice-Adapter, WhatsApp-Bestellassistent, RAG/Wissensbase |

---

### Architektur

| Schicht | Technologie |
|---------|-------------|
| Frontend | React 18, TypeScript 5.5, Vite 5.4, Tailwind CSS, Radix UI, Zustand, TanStack Query |
| Backend | Python 3.11+, FastAPI, SQLAlchemy 2.0, Alembic, Pydantic 2.x |
| Datenbank | PostgreSQL 15+ (Multi-Schema), Redis 7 |
| Authentifizierung | OIDC / Keycloak / Azure AD / Auth0, JWT RS256/JWKS |
| Eventing | NATS JetStream (Outbox-Pattern, Workflow-Cockpit-Projektor) |
| Infrastruktur | Docker Compose, Helm/Kubernetes, GitHub Actions CI/CD |
| KI / Wissen | ChromaDB/RAG, MCP-Tool-Contracts, Superglue, LLM-Gateway (anbieterunabhängig) |
| Design | Meridian UI (Navy-Sidebar, tokenisierte Farben, Mask-Builder-Framework) |

**Wichtige Verzeichnisse:**

```
app/                    FastAPI-Backend (Services, Modelle, Endpoints, Agent-Ops)
app/services/           ~160 Domain-Service-Module (thin-router pattern)
packages/frontend-web/  React-Frontend (Mask-Builder, Meridian-Shell)
modules/agrar/          Agrar-Vertikalmodul
alembic/                Datenbankmigrationen (single head)
docs/                   Architektur (arc42, C4, ADRs), Handbuch, QA, Runbooks
scripts/                Bootstrap-, Smoke-, Governance- und Prüfskripte
```

**PostgreSQL-Schemas:**
`domain_shared` · `domain_crm` · `domain_erp` · `domain_inventory` · `domain_einkauf` · `domain_sales` · `domain_finance` · `domain_ops` · `domain_docflow` · `domain_agrar` · `domain_controlling` · `domain_hr` · `domain_logistics` · `domain_workflow`

---

### Schnellstart mit Docker

**Voraussetzungen:** Docker Desktop, Git

```bash
# Vollständiger Stack (Postgres, Redis, NATS, Keycloak, Backend, Frontend)
docker compose up -d

# Nur Backend + Postgres (leichtgewichtig für Entwicklung)
docker compose -f docker-compose.dev.yml up -d
```

Lokale Endpunkte nach `up`:

| Dienst | URL |
|--------|-----|
| Frontend | http://localhost:3001 |
| Backend API | http://localhost:8000 |
| OpenAPI Docs | http://localhost:8000/docs |
| Keycloak | http://localhost:8080 |
| pgAdmin | http://localhost:5050 |

---

### Lokale Entwicklung (ohne Docker)

```bash
# Backend starten
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Datenbankmigrationen (Erstinstallation: alle Tabellen anlegen)
alembic upgrade head

# Tests
pytest -m unit --no-cov          # Nur reine Logik-Unit-Tests (schnell, kein DB)
pytest                            # Vollständige Suite
pytest --cov=app --cov-report=term

# Frontend
cd packages/frontend-web
npm install
npm run dev                       # Port 3001, proxied → Backend :8000
npm run build
npm run lint
```

---

### Erstinstallation und Migrations-Sicherheit

```bash
# DB initialisieren
python scripts/init_db.py

# Qualitäts-Gates prüfen
python scripts/check_alembic_single_head.py
python scripts/check_required_domain_schemas.py
python scripts/check_critical_backend_coverage.py
python scripts/check_toolchain_pins.py

# TypeScript-Typen prüfen
pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false
```

Docker-Smoke (Windows):
```powershell
powershell -ExecutionPolicy Bypass -File scripts/smoke_first_install_docker.ps1 -HostPort 55434
```

---

### Architektur-Dokumentation

| Dokument | Inhalt |
|----------|--------|
| [arc42](docs/architecture/arc42/) | 12-Kapitel-Architekturbeschreibung (ISO 42010) |
| [C4-Diagramme](docs/architecture/c4/) | Context, Container, Components (Mermaid) |
| [ADR-001…036](docs/adr/) | Architecture Decision Records |
| [Benutzerhandbuch](docs/user-manual/) | Vollständiges deutsches Handbuch (Wave 17) |
| [Admin-Dokumentation](docs/admin/) | Deployment, RBAC, Monitoring, Backup |
| [Open Gaps](docs/project-context/open-gaps-and-known-issues.md) | Offene Punkte, technische Schulden |
| [Production Readiness Runbook](docs/operations/production-readiness-runbook.md) | Go-Live-Checkliste + externe Gates |
| [Process Kernel Status](docs/architecture/process-kernel/STATUS.md) | Wave-Übersicht Waves 1–104+ |
| [Active Workboard](docs/agent-ops/active-workboard.md) | Laufende Arbeitsstände |
| [MASKEN.md](docs/MASKEN.md) | UX-Standard Dokument-Konsistenzprinzip |

---

### Drittlizenzen

Dieses Repository enthält Integrations-Support für `superglue-ai/superglue` (Lizenz: `FSL-1.1-Apache-2.0`).
Lokaler Hinweis: [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)

---

### Lizenz

[MIT License](LICENSE) — sofern in Teilbereichen nicht abweichend dokumentiert.

---

<a name="english"></a>
## 🇬🇧 English

VALEO NeuroERP 3.0 is a multi-domain ERP system for agricultural cooperatives and grain trading companies. The focus is on end-to-end agricultural trading excellence, agent-capable domain architecture, and fast process UX — not a generic horizontal ERP.

---

### Current Status

| Metric | As of |
|--------|-------|
| Docs date | `2026-07-06` |
| Maturity | **Beta** — core processes operational, external go-live gates open |
| Doc-code drift | **0 items** (`doc_drift_report.py --fail-over 0`, 2026-07-06) |
| Release evidence | **WARN** — 4 PASS / 2 WARN / 0 FAIL (`artifacts/release_evidence.json`) |
| Mask commandEndpoints | **26 native SDs, 0 stubReason** (SPEC-P1-04 inventory script) |
| Frontend TypeScript | 0 errors (`tsc --noEmit`) |
| Backend tests | **11,810 passed** in CI full run (2026-07-05) |
| Critical coverage ratchets | only-up policy green in CI |
| Backend overall coverage | 65.66 % (long-term target ≥ 80 %) |
| OpenAPI routes | **2,537 paths** with `summary=` (100 %) |
| Alembic | 1 head (`inv_lot_depth_spec_p1_08`) |
| Domain depth | DOM-\*-004 completed: contracts, O2C, accounting, P2P, evidence room, supply chain |
| Architecture docs | arc42 (12 chapters), C4 Context/Container/Components, 036 ADRs |
| User manual | DOC-USER-MANUAL-004 Wave 17 — complete (German) |
| Runtime API sweep | 1,059 GET endpoints live tested; known 5xx closed repo-side |
| Workflow Cockpit | MVP + retry/compensation + NATS projector + dead-letter view |

---

### Maturity: What's Missing for Production?

#### Repo-side ready ✅
- Broad domain coverage across 12+ ERP areas with operational end-logic
- OIDC auth, multi-tenancy, bearer token enforcement, RFC-7807 error model
- Hard CI gates: TypeScript, ESLint, pytest ratchet, security scan, SBOM
- Immutable SHA images, Helm rollout, `/healthz`/`/readyz` smoke
- Alembic single head, idempotent migrations, Keycloak DB bootstrap
- GoBD evidence room, DATEV export, UStVA submission client
- POS with TSE simulation (Fiskaly integration prepared)
- Full UAT documentation, Playwright E2E evidence, traceability matrix

#### External go-live gates ⏳ (operations responsibility)
| Gate | Owner |
|------|-------|
| Production Keycloak/OIDC credentials | Operations |
| TSE hardware acceptance & DSFinV-K certification | Operations / fiscal provider |
| ERiC/ELSTER live submission | Tax advisor + DATEV cutover mapping |
| DMS Paperless-ngx live probe | Operations |
| Staging domain + DNS + TLS certificate | Operations |
| Backup/restore drill (15-min RTO) | Operations |
| Harvest-peak load test on staging | Operations (k6, `load-test.yml`) |
| Real UAT signatures | Business + management |
| GDPR data-protection-officer sign-off | DPO |

Full gate list: [`docs/operations/production-readiness-runbook.md`](docs/operations/production-readiness-runbook.md)

---

### What the System Covers Today

**12+ business domains with operational depth:**

| Domain | Depth |
|--------|-------|
| Agrar | Harvest acceptance, weighing, contracts (MATIF/fixing), drying rules, self-billing, batch aggregation |
| Sales (O2C) | Quote → order → delivery note → invoice, position match, credit limit, cancellation/credit note |
| Procurement (P2P) | RFQ → PO → goods receipt → three-way match, ERS, invoice verification |
| Inventory/WMS | Stock management, silo cells, material flow, lot traceability, QS control board |
| Accounting | Dunning run, OP clearing, period close, DATEV export, UStVA, Atlas/customs |
| CRM / KIM | 360° cockpit (KIM), buyer classification, auto-capture (email/phone), TAPI |
| Logistics | Freight documents, route planning, ePOD, driver time tracking |
| Compliance | GoBD evidence room, LkSG, GDPR Art. 30/33, hazmat, customs/Atlas, VVVO |
| HRM | Personnel file, absence (ArbZG), time tracking, payroll (DE), planning wizard |
| POS | Day-end closing, TSE simulation, DSFinV-K preparation, returns |
| Feed/Rations | Recipe, ration optimization (animal welfare), production approval, inventory link |
| Agent-Ops / AI | Workflow cockpit, MCP tool registry, LLM gateway, voice adapter, WhatsApp order assistant, RAG/knowledge base |

---

### Architecture

| Layer | Technology |
|-------|------------|
| Frontend | React 18, TypeScript 5.5, Vite 5.4, Tailwind CSS, Radix UI, Zustand, TanStack Query |
| Backend | Python 3.11+, FastAPI, SQLAlchemy 2.0, Alembic, Pydantic 2.x |
| Database | PostgreSQL 15+ (multi-schema), Redis 7 |
| Auth | OIDC / Keycloak / Azure AD / Auth0, JWT RS256/JWKS |
| Eventing | NATS JetStream (outbox pattern, workflow cockpit projector) |
| Infrastructure | Docker Compose, Helm/Kubernetes, GitHub Actions CI/CD |
| AI / Knowledge | ChromaDB/RAG, MCP tool contracts, Superglue, LLM gateway (provider-agnostic) |
| Design | Meridian UI (navy sidebar, tokenized colors, Mask Builder Framework) |

**Key directories:**

```
app/                    FastAPI backend (services, models, endpoints, agent-ops)
app/services/           ~160 domain service modules (thin-router pattern)
packages/frontend-web/  React frontend (Mask Builder, Meridian shell)
modules/agrar/          Agrar vertical module
alembic/                Database migrations (single head)
docs/                   Architecture (arc42, C4, ADRs), manual, QA, runbooks
scripts/                Bootstrap, smoke, governance and validation scripts
```

**PostgreSQL schemas:**
`domain_shared` · `domain_crm` · `domain_erp` · `domain_inventory` · `domain_einkauf` · `domain_sales` · `domain_finance` · `domain_ops` · `domain_docflow` · `domain_agrar` · `domain_controlling` · `domain_hr` · `domain_logistics` · `domain_workflow`

---

### Quick Start with Docker

**Prerequisites:** Docker Desktop, Git

```bash
# Full stack (Postgres, Redis, NATS, Keycloak, backend, frontend)
docker compose up -d

# Backend + Postgres only (lightweight for development)
docker compose -f docker-compose.dev.yml up -d
```

Local endpoints after `up`:

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3001 |
| Backend API | http://localhost:8000 |
| OpenAPI Docs | http://localhost:8000/docs |
| Keycloak | http://localhost:8080 |
| pgAdmin | http://localhost:5050 |

---

### Local Development (without Docker)

```bash
# Start backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Database migrations (first install: create all tables)
alembic upgrade head

# Tests
pytest -m unit --no-cov          # Pure logic unit tests only (fast, no DB)
pytest                            # Full suite
pytest --cov=app --cov-report=term

# Frontend
cd packages/frontend-web
npm install
npm run dev                       # Port 3001, proxied → backend :8000
npm run build
npm run lint
```

---

### First Install & Migration Safety

```bash
# Initialize DB
python scripts/init_db.py

# Validate quality gates
python scripts/check_alembic_single_head.py
python scripts/check_required_domain_schemas.py
python scripts/check_critical_backend_coverage.py
python scripts/check_toolchain_pins.py

# Check TypeScript types
pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false
```

Docker smoke test (Windows):
```powershell
powershell -ExecutionPolicy Bypass -File scripts/smoke_first_install_docker.ps1 -HostPort 55434
```

---

### Architecture Documentation

| Document | Contents |
|----------|----------|
| [arc42](docs/architecture/arc42/) | 12-chapter architecture description (ISO 42010) |
| [C4 diagrams](docs/architecture/c4/) | Context, Container, Components (Mermaid) |
| [ADR-001…036](docs/adr/) | Architecture Decision Records |
| [User Manual](docs/user-manual/) | Complete German user manual (Wave 17) |
| [Admin Documentation](docs/admin/) | Deployment, RBAC, monitoring, backup |
| [Open Gaps](docs/project-context/open-gaps-and-known-issues.md) | Open items, technical debt |
| [Production Readiness Runbook](docs/operations/production-readiness-runbook.md) | Go-live checklist + external gates |
| [Process Kernel Status](docs/architecture/process-kernel/STATUS.md) | Wave overview Waves 1–104+ |
| [Active Workboard](docs/agent-ops/active-workboard.md) | Current work in progress |
| [MASKEN.md](docs/MASKEN.md) | UX standard: document consistency principle |

---

### Third-Party Licenses

This repository includes integration support for `superglue-ai/superglue` (license: `FSL-1.1-Apache-2.0`).
Local attribution: [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)

---

### License

[MIT License](LICENSE) — unless documented otherwise in specific sub-areas.
