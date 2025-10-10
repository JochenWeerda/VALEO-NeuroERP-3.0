# VALEO NeuroERP 3.0 🚀

## Production-Ready Enterprise Resource Planning System

**Status:** ✅ **Production Ready** | **Version:** 3.0.0 | **Authentication:** ✅ OIDC Enabled

A comprehensive, production-ready ERP system with modern authentication, real-time capabilities, and enterprise-grade security.

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
- **Production Backend APIs** (not mocks)
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

3. **Configure Authentication:**
```bash
# Copy environment template
cp .env.example .env

# Configure your OIDC provider in .env:
# VITE_OIDC_DISCOVERY_URL=https://your-provider.com/.well-known/openid_configuration
# VITE_OIDC_CLIENT_ID=your-client-id
```

4. **Access the application:**
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
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

### Production Deployment
```bash
# Build and deploy with Docker
docker-compose -f docker-compose.prod.yml up -d

# Or deploy to Kubernetes
kubectl apply -f k8s/
```

### Environment Configuration
- **Development:** `.env` with local configuration
- **Production:** Environment variables or Kubernetes secrets
- **Staging:** Separate environment with test data

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

## 📄 License

Proprietary - VALEO Internal Use Only

## 🆘 Support

For technical support or questions:
- **Documentation:** See `/docs` folder
- **API Documentation:** Visit `/docs` when running
- **Health Check:** Use `/healthz` endpoint

---

**🆕 Latest Updates:**
- ✅ **Production-ready authentication system** with OIDC
- ✅ **Real API integration** (no more mocks)
- ✅ **Complete frontend-backend integration**
- ✅ **Enterprise security features**
- ✅ **Docker and Kubernetes deployment ready**

**VALEO NeuroERP 3.0 - Production Ready! 🚀**
