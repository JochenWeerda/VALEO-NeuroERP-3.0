***REMOVED*** VALEO NeuroERP 3.0 🚀

***REMOVED******REMOVED*** Production-Ready Enterprise Resource Planning System

![Deploy Staging](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/workflows/deploy-staging.yml/badge.svg)
![Security Scan](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/workflows/security-scan.yml/badge.svg)
![License](https://img.shields.io/badge/license-Proprietary-red)
![Version](https://img.shields.io/badge/version-3.0.0-blue)

**Status:** ✅ **Production Ready** | **Version:** 3.0.0 | **Authentication:** ✅ OIDC Enabled

A comprehensive, production-ready ERP system with modern authentication, real-time capabilities, and enterprise-grade security.

***REMOVED******REMOVED*** 🌟 Key Features

***REMOVED******REMOVED******REMOVED*** ✅ Production-Ready Authentication
- **OIDC Integration** with Azure AD, Keycloak, Auth0 support
- **JWT Token Management** with automatic refresh
- **Multi-Provider Support** for enterprise SSO
- **Role-Based Access Control** (RBAC) with scopes

***REMOVED******REMOVED******REMOVED*** 🏗️ Modern Architecture
- **Frontend:** React 18 + TypeScript + Vite
- **Backend:** Python FastAPI + PostgreSQL
- **Real-Time:** Server-Sent Events (SSE) + WebSocket support
- **Authentication:** OIDC with JWT tokens
- **Deployment:** Docker + Kubernetes ready

***REMOVED******REMOVED******REMOVED*** 🔗 Live API Integration
- **Production Backend Schnittstellen** (not mocks)
- **Real-Time Data Flow** between frontend and backend
- **Comprehensive Error Handling** and logging
- **Request/Response Interceptors** for authentication

***REMOVED******REMOVED*** 🏢 Core Domains

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

***REMOVED******REMOVED*** 🚀 Quick Start

***REMOVED******REMOVED******REMOVED*** Prerequisites
- **Git** (for cloning)
- **Docker & Docker Compose** (for local development)
- **OIDC Provider** (Azure AD, Keycloak, or Auth0 for production auth)

***REMOVED******REMOVED******REMOVED*** Installation

1. **Clone the repository:**
```bash
git clone https://github.com/JochenWeerda/VALEO-NeuroERP-3.0.git
cd VALEO-NeuroERP-3.0
```

2. **Start the complete stack:**
```bash
***REMOVED*** Start all services (databases, backend, frontend)
docker-compose up -d

***REMOVED*** Or start individual components
docker-compose up -d postgres redis
python main.py  ***REMOVED*** Backend API
cd packages/frontend-web && npm run dev  ***REMOVED*** Frontend
```

***REMOVED******REMOVED******REMOVED*** Frontend Commands (pnpm)

```bash
cd packages/frontend-web
pnpm install
pnpm dev          ***REMOVED*** Start Vite Dev-Server
pnpm build        ***REMOVED*** Production Build
pnpm typecheck    ***REMOVED*** TypeScript Project Check
pnpm lint         ***REMOVED*** ESLint (fails on warnings)
pnpm storybook    ***REMOVED*** UI Workbench
```

3. **Configure Authentication:**
```bash
***REMOVED*** Copy environment template
cp .env.example .env

***REMOVED*** Configure your OIDC provider in .env:
***REMOVED*** VITE_OIDC_DISCOVERY_URL=https://your-provider.com/.well-known/openid_configuration
***REMOVED*** VITE_OIDC_CLIENT_ID=your-client-id
***REMOVED*** API_DEV_TOKEN=dev-token  ***REMOVED*** Change for local security
```

4. **Access the application:**
- **Frontend:** http://localhost:3000
- **Backend Modul:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

***REMOVED******REMOVED*** 🔐 Authentication Setup

***REMOVED******REMOVED******REMOVED*** Production OIDC Configuration

The system supports multiple OIDC providers:

***REMOVED******REMOVED******REMOVED******REMOVED*** Azure Active Directory
```env
VITE_OIDC_DISCOVERY_URL=https://login.microsoftonline.com/YOUR_TENANT_ID/v2.0/.well-known/openid_configuration
VITE_OIDC_CLIENT_ID=your-azure-client-id
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Keycloak
```env
VITE_OIDC_DISCOVERY_URL=https://your-keycloak.com/realms/YOUR_REALM/.well-known/openid_configuration
VITE_OIDC_CLIENT_ID=your-keycloak-client-id
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Auth0
```env
VITE_OIDC_DISCOVERY_URL=https://your-domain.auth0.com/.well-known/openid_configuration
VITE_OIDC_CLIENT_ID=your-auth0-client-id
```

***REMOVED******REMOVED******REMOVED*** Development Mode
For development without OIDC setup, the system includes demo authentication endpoints (not for production use).

***REMOVED******REMOVED*** 📊 System Status

| Component | Status | Health Check |
|-----------|--------|--------------|
| **Frontend** | ✅ Running | http://localhost:3000 |
| **Backend API** | ✅ Running | http://localhost:8000/healthz |
| **Database** | ✅ Running | PostgreSQL 15+ |
| **Authentication** | ✅ Configured | OIDC with JWT |
| **Real-Time Events** | ✅ Active | SSE WebSocket |
| **API Integration** | ✅ Verified | Production endpoints |

***REMOVED******REMOVED*** 🛠️ Development

***REMOVED******REMOVED******REMOVED*** Project Structure
```
├── packages/
│   ├── frontend-web/          ***REMOVED*** React frontend with authentication
│   ├── inventory-domain/      ***REMOVED*** Inventory management
│   ├── erp-domain/           ***REMOVED*** ERP core functionality
│   ├── finance-domain/       ***REMOVED*** Financial services
│   └── ...                   ***REMOVED*** Other domain modules
├── app/                      ***REMOVED*** Python FastAPI backend
├── main.py                   ***REMOVED*** Main application entry point
├── docker-compose.yml        ***REMOVED*** Complete stack definition
└── docs/                     ***REMOVED*** Documentation
```

***REMOVED******REMOVED******REMOVED*** Key Technologies
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS
- **Backend:** Python 3.11, FastAPI, PostgreSQL, Redis
- **Authentication:** OIDC, JWT, OAuth2
- **Real-Time:** Server-Sent Events, WebSocket
- **Deployment:** Docker, Kubernetes, Helm
- **Monitoring:** Prometheus, Grafana, Loki

***REMOVED******REMOVED*** 🔒 Security Features

- ✅ **OIDC Authentication** with enterprise providers
- ✅ **JWT Token Management** with secure storage
- ✅ **CORS Configuration** for cross-origin requests
- ✅ **Rate Limiting** and request throttling
- ✅ **Input Validation** and sanitization
- ✅ **Audit Logging** for all operations
- ✅ **Role-Based Access Control** (RBAC)

***REMOVED******REMOVED*** 🚢 Deployment

***REMOVED******REMOVED******REMOVED*** Staging Deployment (Docker Desktop on Windows)

**Quick-Start:**
```powershell
***REMOVED*** Deploy Staging-Stack
.\scripts\staging-deploy.ps1

***REMOVED*** Run Smoke-Tests
.\scripts\smoke-tests-staging.sh

***REMOVED*** Access Frontend
***REMOVED*** http://localhost:3001
***REMOVED*** Login: test-admin / Test123!
```

**Auto-Deploy via GitHub Actions:**
```bash
***REMOVED*** Push to develop branch triggers automatic deployment
git push origin develop

***REMOVED*** Or manually trigger via GitHub UI:
***REMOVED*** https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/workflows/deploy-staging.yml
```

**Dokumentation:**
- [STAGING-DEPLOYMENT.md](./STAGING-DEPLOYMENT.md) - Vollständige Staging-Anleitung
- [GITHUB-ACTIONS-STAGING-SETUP.md](./GITHUB-ACTIONS-STAGING-SETUP.md) - Auto-Deploy Setup
- [scripts/README.md](./scripts/README.md) - Scripts-Dokumentation

***REMOVED******REMOVED******REMOVED*** Production Deployment
```bash
***REMOVED*** Build and deploy with Docker
docker-compose -f docker-compose.prod.yml up -d

***REMOVED*** Or deploy to Kubernetes
kubectl apply -f k8s/
```

**Dokumentation:**
- [DEPLOYMENT-PLAN.md](./DEPLOYMENT-PLAN.md) - Production-Deployment-Plan
- [PRODUCTION-AUTH-SETUP.md](./PRODUCTION-AUTH-SETUP.md) - Authentication-Setup

***REMOVED******REMOVED******REMOVED*** Environment Configuration
- **Development:** `.env` with local configuration (`API_DEV_TOKEN`, `API_URL`, database DSN)
- **Frontend Dev:** `packages/frontend-web/env.example` (`VITE_API_DEV_TOKEN`, `VITE_API_BASE_URL`)
- **Staging:** `env.example.staging` - Docker Desktop (Windows)
- **Production:** Environment variables or Kubernetes secrets
- **Feature Flags:** `VITE_FEATURE_SSE`, `VITE_FEATURE_COMMAND_PALETTE`, `VITE_FEATURE_AGRAR` (remote overrides via `VITE_FLAGS_URL`, fallback to `/flags.json`)

***REMOVED******REMOVED******REMOVED*** Database Init & Seed Data
```bash
***REMOVED*** Initialize database schema (runs SQLAlchemy Base metadata)
python scripts/init_db.py

***REMOVED*** Insert sample inventory data for POS/Inventory views
python -m app.seeds.inventory_seed
```

> Playwright API checks require `API_URL` (and optionally `API_DEV_TOKEN`) to be exported before running `pnpm playwright test`.

***REMOVED******REMOVED******REMOVED*** OIDC / Auth Setup
- Schnelleinführung: siehe `docs/setup/oidc_dev_setup.md` für Dev-Token, Keycloak-Docker und Provider-spezifische Hinweise.
- Für produktive Tenants Dev-Token deaktivieren und Tokens per JWT verifizieren (siehe Roadmap Phase 2).

***REMOVED******REMOVED*** 📈 Monitoring & Observability

- **Metrics:** Prometheus metrics at `/metrics`
- **Logging:** Structured JSON logging with Loki
- **Tracing:** OpenTelemetry distributed tracing
- **Dashboards:** Grafana dashboards for system monitoring
- **Health Checks:** `/healthz` and `/readyz` endpoints

***REMOVED******REMOVED*** 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

***REMOVED******REMOVED*** 📄 License

Proprietary - VALEO Internal Use Only

***REMOVED******REMOVED*** 🆘 Support

For technical support or questions:
- **Documentation:** See `/docs` folder
- **API Documentation:** Visit `/docs` when running
- **Health Check:** Use `/healthz` endpoint

---

**🆕 Latest Updates:**
- ✅ **Staging-Deployment vollständig automatisiert** (Docker Desktop + GitHub Actions)
- ✅ **18 automatisierte Smoke-Tests** für Staging-Umgebung
- ✅ **Production-ready authentication system** with OIDC
- ✅ **Real API integration** (no more mocks)
- ✅ **Complete frontend-backend integration**
- ✅ **Enterprise security features**
- ✅ **Docker and Kubernetes deployment ready**
- ✅ **Auto-Deploy bei Push auf develop-Branch**

**VALEO NeuroERP 3.0 - Production Ready! 🚀**

**Repository:** https://github.com/JochenWeerda/VALEO-NeuroERP-3.0
