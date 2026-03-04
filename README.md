# VALEO NeuroERP 3.0 🚀

Experimental **open-source ERP and automation platform** combining classical enterprise resource planning with AI-assisted workflows. A modular research and development environment for AI agents, automation pipelines, and enterprise data.

![Deploy Staging](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/workflows/deploy-staging.yml/badge.svg)
![Security Scan](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/workflows/security-scan.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-blue)
![Version](https://img.shields.io/badge/version-3.0.0-blue)

**Status:** 🚧 **In Development** | **Version:** 3.0.0-alpha | **Authentication:** ✅ OIDC Enabled

*Maintained by a generalist in agricultural trading (field service) with a focus on AI automation – building an open, AI-friendly ERP experimentation platform.*

> ⚠️ **Hinweis:** Das System befindet sich noch in aktiver Entwicklung. Es fehlen noch etliche Tests, GAP-Schließungen und Issue-Resolutionen, bevor es als production-ready eingestuft werden kann.

## 🌟 Key Features

### ✅ Production-Ready Authentication
- **OIDC Integration** with Azure AD, Keycloak, Auth0 support
- **JWT Token Management** with automatic refresh
- **Multi-Provider Support** for enterprise SSO
- **Role-Based Access Control** (RBAC) with scopes

### 🏗️ Modern Architecture
- **Frontend:** React 18 + TypeScript + Vite
- **Backend:** Python FastAPI + PostgreSQL
- **Real-Time:** Server-Sent Events (SSE) + WebSocket support
- **Authentication:** OIDC with JWT tokens
- **Deployment:** Docker + Kubernetes ready

### 🔗 Live API Integration
- **Production Backend Schnittstellen** (not mocks)
- **Real-Time Data Flow** between frontend and backend
- **Comprehensive Error Handling** and logging
- **Request/Response Interceptors** for authentication

## 🏢 Core Domains

| Domain | Status | Description |
|--------|--------|-------------|
| **Inventory** | ✅ Complete | Warehouse management, putaway/slotting, cycle counting |
| **ERP** | ✅ Complete | Order management, core business logic |
| **Finance** | ✅ Complete | AI-powered bookkeeping, bank reconciliation |
| **HR** | ✅ Complete | Employee management, time tracking, payroll |
| **Production** | ✅ Complete | Recipe management, quality control, batch tracking |
| **Sales** | ✅ Complete | Quote and invoice management |
| **Analytics** | ✅ Complete | KPI calculation, forecasting, reporting |
| **Regulatory** | ✅ Complete | Compliance checking, GHG calculations |
| **Logistics** | ✅ Complete | Dispatch, routing, telematics |
| **Quality** | ✅ Complete | CAPA management, non-conformities |
| **Procurement** | ✅ Complete | Supplier risk management |
| **Weighing** | ✅ Complete | Weighing ticket management |

## 🤖 AI & Automation

- **AI-assisted workflows** – Decision support, automation pipelines, and intelligent knowledge systems
- **Event-driven architecture** – NATS JetStream, outbox pattern for reliable async events
- **Extensibility** – Designed for AI agents, LLM integrations, and automation frameworks
- **Voice/Intent & Command Palette** – See [docs/architecture/KI-USABILITY-MICROSERVICES.md](docs/architecture/KI-USABILITY-MICROSERVICES.md) for unified AI usability (voice-to-intent, shortcuts, actions)

See [docs/AI-VISION.md](docs/AI-VISION.md) for the project’s AI and research vision.

## 📸 Screenshots

| Dashboard / Navigation | Finance – Open Items | Agrar – Ernteannahme |
|------------------------|----------------------|----------------------|
| ![Dashboard](docs/screenshots/dashboard.png?v=2) | ![Finance](docs/screenshots/finance.png?v=2) | ![Agrar](docs/screenshots/agrar.png?v=2) |

Screenshots are from staging or local. Add `dashboard.png`, `finance.png`, and `agrar.png` to [docs/screenshots/](docs/screenshots/) (see [docs/screenshots/README.md](docs/screenshots/README.md) for how to capture them).

## 🚀 Quick Start

### Prerequisites
- **Git** (for cloning)
- **Docker & Docker Compose** (for local development)
- **OIDC Provider** (Azure AD, Keycloak, or Auth0 for production auth)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/JochenWeerda/VALEO-NeuroERP-3.0.git
cd VALEO-NeuroERP-3.0
```

2. **Start the complete stack:**
```bash
# Start all services (databases, backend, frontend)
docker-compose up -d

# Or start individual components
docker-compose up -d postgres redis
python main.py  # Backend API
cd packages/frontend-web && npm run dev  # Frontend
```

3. **Datenbank-Migrationen ausführen (alle Tabellen anlegen):**
```bash
# Nach Neuinstallation oder Clone: Alle Schemas und Tabellen anlegen
alembic upgrade head
```
Dabei werden alle im Repository enthaltenen Alembic-Migrationen nacheinander angewendet (domain_shared, domain_ops, domain_erp, domain_inventory, domain_crm, domain_finance, …). Ohne diesen Schritt fehlen Tabellen und die API kann fehlschlagen.

### Frontend Commands (pnpm)

```bash
cd packages/frontend-web
pnpm install
pnpm dev          # Start Vite Dev-Server
pnpm build        # Production Build
pnpm typecheck    # TypeScript Project Check
pnpm lint         # ESLint (fails on warnings)
pnpm storybook    # UI Workbench
```

4. **Configure Authentication:**
```bash
# Copy environment template
cp .env.example .env

# Configure your OIDC provider in .env:
# VITE_OIDC_DISCOVERY_URL=https://your-provider.com/.well-known/openid_configuration
# VITE_OIDC_CLIENT_ID=your-client-id
# API_DEV_TOKEN=dev-token  # Change for local security
```

5. **Access the application:**
- **Frontend:** http://localhost:3000
- **Backend Modul:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

## 🔐 Authentication Setup

### Production OIDC Configuration

The system supports multiple OIDC providers:

#### Azure Active Directory
```env
VITE_OIDC_DISCOVERY_URL=https://login.microsoftonline.com/YOUR_TENANT_ID/v2.0/.well-known/openid_configuration
VITE_OIDC_CLIENT_ID=your-azure-client-id
```

#### Keycloak
```env
VITE_OIDC_DISCOVERY_URL=https://your-keycloak.com/realms/YOUR_REALM/.well-known/openid_configuration
VITE_OIDC_CLIENT_ID=your-keycloak-client-id
```

#### Auth0
```env
VITE_OIDC_DISCOVERY_URL=https://your-domain.auth0.com/.well-known/openid_configuration
VITE_OIDC_CLIENT_ID=your-auth0-client-id
```

### Development Mode
For development without OIDC setup, the system includes demo authentication endpoints (not for production use).

## 📊 System Status

| Component | Status | Health Check |
|-----------|--------|--------------|
| **Frontend** | ✅ Running | http://localhost:3000 |
| **Backend API** | ✅ Running | http://localhost:8000/healthz |
| **Database** | ✅ Running | PostgreSQL 15+ |
| **Authentication** | ✅ Configured | OIDC with JWT |
| **Real-Time Events** | ✅ Active | SSE WebSocket |
| **API Integration** | ✅ Verified | Production endpoints |

## 🛠️ Development

### Project Structure
```
├── packages/
│   ├── frontend-web/          # React frontend with authentication
│   ├── inventory-domain/      # Inventory management
│   ├── erp-domain/           # ERP core functionality
│   ├── finance-domain/       # Financial services
│   └── ...                   # Other domain modules
├── app/                      # Python FastAPI backend
├── main.py                   # Main application entry point
├── docker-compose.yml        # Complete stack definition
└── docs/                     # Documentation
```

### Key Technologies
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS
- **Backend:** Python 3.11, FastAPI, PostgreSQL, Redis
- **Authentication:** OIDC, JWT, OAuth2
- **Real-Time:** Server-Sent Events, WebSocket
- **Deployment:** Docker, Kubernetes, Helm
- **Monitoring:** Prometheus, Grafana, Loki

## 🔒 Security Features

- ✅ **OIDC Authentication** with enterprise providers
- ✅ **JWT Token Management** with secure storage
- ✅ **CORS Configuration** for cross-origin requests
- ✅ **Rate Limiting** and request throttling
- ✅ **Input Validation** and sanitization
- ✅ **Audit Logging** for all operations
- ✅ **Role-Based Access Control** (RBAC)

## 🚢 Deployment

### Staging Deployment (Docker Desktop on Windows)

**Quick-Start:**
```powershell
# Deploy Staging-Stack
.\scripts\staging-deploy.ps1

# Run Smoke-Tests
.\scripts\smoke-tests-staging.sh

# Access Frontend
# http://localhost:3001
# Login: test-admin / Test123!
```

**Auto-Deploy via GitHub Actions:**
```bash
# Push to develop branch triggers automatic deployment
git push origin develop

# Or manually trigger via GitHub UI:
# https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/workflows/deploy-staging.yml
```

**Dokumentation:**
- [STAGING-DEPLOYMENT.md](./STAGING-DEPLOYMENT.md) - Vollständige Staging-Anleitung
- [GITHUB-ACTIONS-STAGING-SETUP.md](./GITHUB-ACTIONS-STAGING-SETUP.md) - Auto-Deploy Setup
- [scripts/README.md](./scripts/README.md) - Scripts-Dokumentation

### Production Deployment
```bash
# Build and deploy with Docker
docker-compose -f docker-compose.prod.yml up -d

# Or deploy to Kubernetes
kubectl apply -f k8s/
```

**Dokumentation:**
- [DEPLOYMENT-PLAN.md](./DEPLOYMENT-PLAN.md) - Production-Deployment-Plan
- [PRODUCTION-AUTH-SETUP.md](./PRODUCTION-AUTH-SETUP.md) - Authentication-Setup
- [docs/db/l3_import.md](./docs/db/l3_import.md) - L3 Datenimport & Bootstrap

### Environment Configuration
- **Development:** `.env` with local configuration (`API_DEV_TOKEN`, `API_URL`, database DSN)
- **Frontend Dev:** `packages/frontend-web/env.example` (`VITE_API_DEV_TOKEN`, `VITE_API_BASE_URL`)
- **Staging:** `env.example.staging` - Docker Desktop (Windows)
- **Production:** Environment variables or Kubernetes secrets
- **Feature Flags:** `VITE_FEATURE_SSE`, `VITE_FEATURE_COMMAND_PALETTE`, `VITE_FEATURE_AGRAR` (remote overrides via `VITE_FLAGS_URL`, fallback to `/flags.json`)

### Database Init & Seed Data
```bash
# Start local PostgreSQL (falls noch nicht vorhanden)
docker run --name neuroerp-db -d \
  -e POSTGRES_DB=valeo_neuro_erp \
  -e POSTGRES_USER=valeo_dev \
  -e POSTGRES_PASSWORD=REDACTED_PASSWORD \
  -p 5432:5432 postgres:15

# Initialize database schema (runs SQLAlchemy Base metadata)
PYTHONPATH=. python scripts/init_db.py

# Insert sample inventory data for POS/Inventory views
PYTHONPATH=. python -m app.seeds.inventory_seed
```

> Playwright API checks require `API_URL` (and optionally `API_DEV_TOKEN`) to be exported before running `pnpm playwright test`.

### OIDC / Auth Setup
- Schnelleinführung: siehe `docs/setup/oidc_dev_setup.md` für Dev-Token, Keycloak-Docker und Provider-spezifische Hinweise.
- Für produktive Tenants Dev-Token deaktivieren und Tokens per JWT verifizieren (siehe Roadmap Phase 2).
- Relevante Variablen: `OIDC_CLIENT_ID`, `OIDC_ISSUER_URL`, `OIDC_JWKS_URL` (werden sonst aus Keycloak-Einstellungen abgeleitet).

## 📈 Monitoring & Observability

- **Metrics:** Prometheus metrics at `/metrics`
- **Logging:** Structured JSON logging with Loki
- **Tracing:** OpenTelemetry distributed tracing
- **Dashboards:** Grafana dashboards for system monitoring
- **Health Checks:** `/healthz` and `/readyz` endpoints

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

**AI-assisted development** is welcome. Please mark AI involvement in commit messages (e.g. `[AI-Assisted]` or `[AI-Generated]`) and in PR descriptions so that reviewers have full transparency.

## 📄 License

MIT License – see [LICENSE](LICENSE). Copyright (c) 2024 Jochen Weerda.

## 🆘 Support

- **Documentation:** See `/docs` folder
- **API Documentation:** http://localhost:8000/docs when running
- **Health Check:** `/healthz` endpoint

---

**🆕 Latest Updates**

- ✅ Staging deployment automated (Docker Desktop + GitHub Actions)
- ✅ 18 automated smoke tests for staging
- ✅ OIDC authentication, real API integration, frontend-backend integration
- ✅ Finance module with 23+ backend APIs, IBAN lookup, i18n (German)
- 🤖 AI & automation focus – event-driven architecture, extensible for agents and workflows

**Repository:** https://github.com/JochenWeerda/VALEO-NeuroERP-3.0

