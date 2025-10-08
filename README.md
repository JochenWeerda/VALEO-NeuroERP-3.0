# VALEO NeuroERP 2.5 - Backup Repository

## Overview

This repository serves as a backup for the VALEO NeuroERP 3.0 development project. It contains the complete codebase for a comprehensive ERP (Enterprise Resource Planning) system built with modern technologies.

## Architecture

The system is built using a modular, domain-driven design with the following key components:

### Core Domains
- **Inventory Domain**: Warehouse management, putaway/slotting, cycle counting, EDI integration
- **ERP Domain**: Order management, financial services (Bankkonto, Buchung, Konto, etc.)
- **Finance Domain**: AI-powered bookkeeping, bank reconciliation, tax compliance
- **HR Domain**: Employee management, time tracking, payroll
- **Production Domain**: Recipe management, quality control, batch tracking
- **Sales Domain**: Quote and invoice management
- **Analytics Domain**: KPI calculation, forecasting, reporting
- **Regulatory Domain**: Compliance checking, GHG calculations, labeling
- **Logistics Domain**: Dispatch, routing, telematics
- **Quality Domain**: CAPA management, non-conformities, quality plans
- **Procurement Domain**: Supplier risk management
- **Weighing Domain**: Weighing ticket management
- **Notifications Domain**: Multi-channel notifications
- **Audit Domain**: Audit logging and integrity checks
- **Integration Domain**: External system integrations
- **Scheduler Domain**: Task scheduling and automation

### Technical Stack
- **Backend**: Node.js, TypeScript, Express.js
- **Database**: PostgreSQL with Drizzle ORM
- **Event Bus**: Custom event-driven architecture
- **Observability**: Prometheus, Grafana, OpenTelemetry
- **Testing**: Jest, Testcontainers
- **Frontend**: React, Vite, TypeScript (in development)
- **Infrastructure**: Docker, Kubernetes

### Key Features
- Domain-driven design with clean architecture
- Event-sourcing and CQRS patterns
- AI-powered analytics and decision making
- Multi-tenant architecture
- Comprehensive audit trails
- Real-time notifications
- Regulatory compliance automation
- Advanced inventory optimization

## Development Status

This is a backup snapshot of the VALEO NeuroERP 3.0 development. The system is under active development with focus on:

- Backend domain services completion
- Frontend development (React-based)
- Integration testing
- Performance optimization
- Security hardening

## Getting Started

### Prerequisites
- Node.js 18+
- PostgreSQL 15+
- Docker & Docker Compose
- GitHub CLI (for deployment)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/JochenWeerda/VALEO-NeuroERP-2.5.git
cd VALEO-NeuroERP-2.5
```

2. Install dependencies:
```bash
pnpm install
```

3. Set up environment variables (copy from `.env.example`)

4. Start databases:
```bash
docker-compose up -d
```

5. Run migrations and build:
```bash
pnpm run build
```

### Running the Application

```bash
# Start all services
pnpm run start:all

# Or start individual domains
pnpm --filter inventory-domain run dev
```

## Project Structure

```
packages/
├── inventory-domain/          # Warehouse & inventory management
├── erp-domain/               # Core ERP functionality
├── finance-domain/           # Financial services
├── hr-domain/               # Human resources
├── production-domain/        # Manufacturing & quality
├── analytics-domain/         # Business intelligence
├── frontend-web/            # React frontend (WIP)
├── shared/                  # Shared utilities & contracts
└── ...

docs/                        # Architecture documentation
k8s/                        # Kubernetes manifests
observability/              # Monitoring & logging
```

## Contributing

This is a backup repository. For active development, please refer to the main development repository.

## License

Proprietary - VALEO Internal Use Only

## Contact

For questions about this backup, please contact the development team.
