# VALEO NeuroERP 3.0 Development Map

**Zweck:** Historische und `abgeleitete Sicht` fuer Setup, Beitragspfad und Orientierung. Nicht der operative Lieferstand.

## Einordnung

Der aktuelle operative Wahrheitsstand liegt in [STATUS.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/architecture/process-kernel/STATUS.md), den `wave-*/STATUS.md` und in [PLAN_GAPS_023_024_043_049.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/PLAN_GAPS_023_024_043_049.md). Diese Datei dient nur als Onboarding- und Referenzdokument und ist daher `historisch` beziehungsweise abgeleitet.

This document outlines the development workflow, key reference documents, and processes for contributing to the VALEO NeuroERP 3.0 project.

## Table of Contents
1. [Setup](#setup)
2. [Contribution Guidelines](#contribution-guidelines)
3. [Architecture Overview](#architecture-overview)
4. [Release Process](#release-process)
5. [Key Reference Documents](#key-reference-documents)

## Setup

### Prerequisites
- Node.js >= 18
- Python >= 3.9
- Docker & Docker Compose
- PostgreSQL >= 14
- Redis >= 7
- Git

### Local Development Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/VALEO-NeuroERP-3.0.git
   cd VALEO-NeuroERP-3.0
   ```

2. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install frontend dependencies:
   ```bash
   cd packages/frontend-web
   pnpm install
   cd ../..
   ```

4. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your local configuration
   ```

5. Initialize database:
   ```bash
   alembic upgrade head
   ```

6. Start services:
   ```bash
   docker-compose -f docker-compose.dev.yml up
   ```

7. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Contribution Guidelines

### Code Contributions
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Ensure all tests pass:
   ```bash
   # Backend tests
   pytest -q

   # Frontend tests
   cd packages/frontend-web
   pnpm test
   cd ../..
   ```
5. Submit a Pull Request with detailed description
6. Follow the [AI Contribution Policy](docs/AI_CONTRIBUTION_POLICY.md) if using AI tools

### Commit Message Format
```
[type]: Brief description (max 50 chars)

[Optional] Detailed explanation
[Optional] Related issue references

[AI-Assisted] or [AI-Generated] if applicable (see AI_CONTRIBUTION_POLICY.md)
```

### Pull Request Requirements
- Description must include purpose and approach
- Screenshots for UI changes
- Test coverage for new functionality
- Documentation updates if applicable
- Review by at least one maintainer

## Architecture Overview

VALEO NeuroERP 3.0 follows a modular monolith architecture with clear domain boundaries. The system is organized into several layers:

### Core Layers
1. **Canonical Domain Model** - Single source of truth for all business entities
2. **Workflow/Policy Layer** - Business rules, process orchestration, and decision engines
3. **Agent/Action Layer** - NeuroASSIST framework for AI-assisted workflows
4. **Mask/Process Builder** - UI composition and process visualization
5. **Read-Model/Analytics Layer** - Optimized views for reporting and dashboards

### Key Architectural Principles
- Canonical Domain Model before API breadth
- Business Commands before UI-centric CRUD
- Workflows configurable instead of hard-coded
- Read Models for performance, not second source of truth
- Policies, approvals, and audit in product core
- Plugins only at stable domain boundaries

### Domain Boundaries
The system maintains strict separation between domains:
- CRM (Customer Relationship Management)
- ERP (Enterprise Resource Planning)
- Finance (Financial Accounting)
- Inventory (Stock Management)
- Agrar (Agricultural-specific processes)
- HR (Human Resources)
- Document Management (DMS)

See the [Architecture Documentation](docs/architecture/) for detailed specifications.

## Release Process

### Versioning
We follow Semantic Versioning (MAJOR.MINOR.PATCH):
- MAJOR: Incompatible API changes
- MINOR: Backward-compatible functionality
- PATCH: Backward-compatible bug fixes

### Release Cycle
1. **Development**: Features developed in feature branches
2. **Staging**: Release candidate deployed to staging environment
3. **Testing**: QA and performance testing
4. **Production**: Deployment to production via approved release branch

### Release Branches
- `main`: Production-ready code
- `develop`: Integration branch for next release
- `release/*`: Preparation for specific release
- `hotfix/*`: Critical fixes for production

### Deployment Process
1. Create release branch from `develop`: `git checkout -b release/v1.2.0 develop`
2. Update version numbers in relevant files
3. Run full test suite
4. Deploy to staging for validation
5. Merge release branch into `main` and `develop`
6. Tag release: `git tag -a v1.2.0 -m "Release v1.2.0"`
7. Deploy to production
8. Clean up release branch

## Key Reference Documents

### Administrative Guides
- [Administrator Guide](docs/admin-guide.md) - System administration procedures
- [Auth and Tenant Concept](docs/AUTH-AND-TENANT-CONCEPT.md) - Multi-tenancy and authentication
- [Agent Integration](docs/AGENT-INTEGRATION.md) - External agent integration guidelines

### AI & Research
- [AI Contribution Policy](docs/AI_CONTRIBUTION_POLICY.md) - Guidelines for AI-assisted development
- [AI & Research Vision](docs/AI-VISION.md) - AI orientation and extensibility
- [NeuroASSIST Target Architecture](docs/architecture/neuroassist-target-architecture.md) - AI orchestration layer

### Domain-Specific Documentation
- [Annnahme LKW Modul](docs/ANNAHME_LKW_MODUL.md) - Truck acceptance workflow
- [Complete Module List](docs/complete-module-list.md) - Inventory of all system modules
- [CRM Domain Architecture](docs/crm_domain_architecture.md) - Customer relationship management
- [CRM Reuse Inventory](docs/crm_reuse_inventory.md) - CRM module reuse strategy
- [CRM SuiteCRM Gap Analysis](docs/crm_suitecrm_gap_analysis.md) - CRM enhancement roadmap
- [CRM UI Mapping](docs/crm_ui_mapping.md) - CRM interface transition plan

### Architecture Documentation
- [Architecture Decision Map](docs/architecture/architecture-decision-map.md) - Overview of architectural decisions
- [Business Logic Architecture](docs/architecture/business-logic-architecture.md) - Core business logic structure
- [Context Architecture Revolution](docs/architecture/context-architecture-revolution.md) - Architectural evolution
- [Current Processes](docs/architecture/current-processes.md) - Existing business processes
- [DMS Paperless Integration](docs/architecture/dms-paperless-integration.md) - Document management integration
- [Fundamental Architecture Principles](docs/architecture/fundamental-architecture-principles.md) - Core architectural tenets
- [Index](docs/architecture/index.md) - Architecture documentation index
- [KI Usability Microservices](docs/architecture/KI-USABILITY-MICROSERVICES.md) - AI usability layer
- [Module Resolution Architecture](docs/architecture/module-resolution-architecture.md) - Dependency resolution
- [NeuroASSIST Compatibility Deprecation Plan](docs/architecture/neuroassist-compat-deprecation-plan.md) - Legacy system migration
- [NeuroASSIST Target Architecture](docs/architecture/neuroassist-target-architecture.md) - AI orchestration layer
- [React Lifecycle Architecture](docs/architecture/react-lifecycle-architecture.md) - Frontend lifecycle management
- [Target Processes](docs/architecture/target-processes.md) - Desired business processes
- [Target State Landhandel ERP](docs/architecture/target-state-landhandel-erp.md) - ERP target state
- [TypeScript Generic Architecture](docs/architecture/typescript-generic-architecture.md) - Frontend architecture

### Process Kernel
- [Process Kernel Status](docs/architecture/process-kernel/STATUS.md) - Current state of process kernel implementation
- [Process Kernel Delivery Map](docs/architecture/process-kernel/DELIVERY-MAP.md) - Process kernel delivery timeline

### Strategic Planning
- [VALEO Wettbewerbsanalyse Spitzenposition](.cursor/plans/valeo_wettbewerbsanalyse_spitzenposition_79027aec.plan.md) - Strategic positioning plan
- [Deployment Plan](DEPLOYMENT-PLAN.md) - Deployment strategies and procedures

### Compliance & Security
- [GoBD Compliance](docs/GOBD-COMPLIANCE.md) - German accounting compliance
- [GoBD Vorgehensplan](docs/GOBD-VORGEHENSPLAN.md) - GoBD implementation plan
- [Security Foundation Audit](docs/SECURITY-FOUNDATION-AUDIT.md) - Security assessment
- [GDPR Compliance](docs/GDPR-COMPLIANCE.md) - Data protection guidelines

### Module-Specific Documentation
- [ANNAHME_LKW_MODUL](docs/ANNAHME_LKW_MODUL.md) - Truck acceptance procedures
- [CRM Domain Architecture](docs/crm_domain_architecture.md) - CRM domain design
- [CRM Reuse Inventory](docs/crm_reuse_inventory.md) - CRM reuse strategy
- [CRM SuiteCRM Gap Analysis](docs/crm_suitecrm_gap_analysis.md) - CRM enhancement roadmap
- [CRM UI Mapping](docs/crm_ui_mapping.md) - CRM UI transition plan

## Development Workflow Summary

1. **Issue Creation**: Create detailed issue describing feature/bug
2. **Planning**: Reference relevant architecture documents and strategic plans
3. **Implementation**: Follow coding standards and contribution guidelines
4. **Testing**: Write and run tests, ensure no regressions
5. **Review**: Submit PR for review, address feedback
6. **Integration**: Merge to develop branch after approval
7. **Release**: Follow release process for production deployment

## Getting Help

- Technical questions: #development Slack channel
- Architecture questions: #architecture Slack channel
- AI/NeuroASSIST questions: #ai-assistance Slack channel
- Documentation: Refer to this document and linked resources
- Emergency: Contact on-call engineer via PagerDuty

---
*Last updated: March 2026*

## Referenzen

- [STATUS.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/architecture/process-kernel/STATUS.md)
- [DELIVERY-MAP.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/architecture/process-kernel/DELIVERY-MAP.md)
- [PLAN_GAPS_023_024_043_049.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/PLAN_GAPS_023_024_043_049.md)
