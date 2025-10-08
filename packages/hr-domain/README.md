***REMOVED*** VALEO NeuroERP 3.0 - HR Domain

Human Resources Domain für Mitarbeiterverwaltung, Rollen & Berechtigungen, Zeiterfassung, Abwesenheiten/Urlaub, Schichtplanung und Payroll-Vorbereitung.

***REMOVED******REMOVED*** 🏗️ Architektur

***REMOVED******REMOVED******REMOVED*** Domain-Driven Design (DDD) + Microservices
- **Domain Layer**: Geschäftslogik und Entitäten
- **Application Layer**: Use Cases und Services
- **Infrastructure Layer**: Repository-Implementierungen, Database, Messaging
- **Presentation Layer**: REST API mit Fastify

***REMOVED******REMOVED******REMOVED*** Technologie-Stack
- **Runtime**: Node.js 20+ mit TypeScript
- **Framework**: Fastify mit OpenAPI/Swagger
- **Database**: PostgreSQL mit Drizzle ORM
- **Authentication**: JWT mit JWKS
- **Messaging**: NATS/Kafka (Event-Driven Architecture)
- **Observability**: OpenTelemetry, Pino Logging

***REMOVED******REMOVED*** 📦 Domänenmodell

***REMOVED******REMOVED******REMOVED*** Entities (Aggregate Roots)
- **Employee**: Mitarbeiter mit Personaldaten, Kontakt, Organisation
- **Role**: HR-spezifische Rollen (separat von Systemrollen)
- **TimeEntry**: Zeiterfassung mit Validierung und Genehmigungsworkflow
- **Shift**: Schichtplanung mit Mitarbeiterzuweisungen
- **LeaveRequest**: Urlaubs-/Abwesenheitsanträge
- **PayrollRun**: Payroll-Vorbereitung und Export (keine FiBu-Buchungen)

***REMOVED******REMOVED******REMOVED*** Wichtige Invarianten
- TimeEntry.end > start, breakMinutes >= 0
- Überlappungsprüfung für Shift-Zuweisungen und TimeEntry
- LeaveRequest blockiert Arbeitszeit; Genehmigungspfad
- PayrollRun.status=Locked → keine Änderungen an TimeEntries

***REMOVED******REMOVED*** 🌐 API-Endpunkte

***REMOVED******REMOVED******REMOVED*** Base URL: `/hr/api/v1`

***REMOVED******REMOVED******REMOVED******REMOVED*** Employees
- `POST /employees` - Mitarbeiter erstellen
- `GET /employees/:id` - Mitarbeiter abrufen
- `GET /employees` - Mitarbeiter auflisten (mit Filterung/Pagination)
- `PATCH /employees/:id` - Mitarbeiter aktualisieren
- `POST /employees/:id/roles` - Rolle zuweisen
- `DELETE /employees/:id/roles/:roleId` - Rolle entfernen
- `POST /employees/:id/deactivate` - Mitarbeiter deaktivieren
- `POST /employees/:id/reactivate` - Mitarbeiter reaktivieren

***REMOVED******REMOVED******REMOVED******REMOVED*** Time Entries
- `POST /time-entries` - Zeiteintrag erstellen
- `GET /time-entries/:id` - Zeiteintrag abrufen
- `GET /time-entries` - Zeiteinträge auflisten
- `PATCH /time-entries/:id` - Zeiteintrag aktualisieren
- `POST /time-entries/:id/approve` - Zeiteintrag genehmigen
- `POST /time-entries/:id/reject` - Zeiteintrag ablehnen
- `GET /employees/:employeeId/time-entries` - Mitarbeiter-Zeiteinträge
- `GET /time-entries/pending` - Ausstehende Genehmigungen

***REMOVED******REMOVED******REMOVED******REMOVED*** Health & Monitoring
- `GET /health` - Health Check
- `GET /ready` - Readiness Check (DB-Verbindung)
- `GET /live` - Liveness Check
- `GET /docs` - OpenAPI Dokumentation

***REMOVED******REMOVED*** 🔐 Sicherheit & Berechtigung

***REMOVED******REMOVED******REMOVED*** Authentication
- JWT-Token mit JWKS-Validierung
- Mandantenfähigkeit über `x-tenant-id` Header
- Token-Expiration und Refresh-Handling

***REMOVED******REMOVED******REMOVED*** Authorization (RBAC/ABAC)
- **HR-spezifische Permissions**:
  - `hr:employee:read|write|delete`
  - `hr:time:read|write|approve`
  - `hr:leave:read|write|approve`
  - `hr:shift:read|write`
  - `hr:payroll:read|write|export`
  - `hr:role:read|write`

***REMOVED******REMOVED******REMOVED*** DSGVO-Compliance
- Datenminimierung: Sensible Felder nur bei Bedarf
- Audit-Trail: createdBy/updatedBy, Change-Logs
- Right to be forgotten: Soft-Delete + Anonymisierung
- Export/Deletion APIs

***REMOVED******REMOVED*** 🚀 Entwicklung

***REMOVED******REMOVED******REMOVED*** Voraussetzungen
- Node.js 20+
- PostgreSQL 14+
- pnpm (empfohlen)

***REMOVED******REMOVED******REMOVED*** Installation
```bash
***REMOVED*** Dependencies installieren
pnpm install

***REMOVED*** Environment konfigurieren
cp env.example .env
***REMOVED*** .env bearbeiten mit lokalen Werten

***REMOVED*** Database Setup
pnpm run migrate:gen  ***REMOVED*** Generiere Migrations
pnpm run migrate:up   ***REMOVED*** Führe Migrations aus
```

***REMOVED******REMOVED******REMOVED*** Entwicklung
```bash
***REMOVED*** Development Server
pnpm run dev

***REMOVED*** Build
pnpm run build

***REMOVED*** Tests
pnpm run test
pnpm run test:watch
pnpm run test:coverage

***REMOVED*** Linting
pnpm run lint
pnpm run lint:fix
```

***REMOVED******REMOVED******REMOVED*** Docker
```bash
***REMOVED*** Build Image
docker build -t valeo-neuroerp-hr-domain .

***REMOVED*** Run Container
docker run -p 3030:3030 \
  -e POSTGRES_URL=postgres://user:pass@host:5432/hr_domain \
  -e JWKS_URL=https://auth.example.com/.well-known/jwks.json \
  valeo-neuroerp-hr-domain
```

***REMOVED******REMOVED*** 📊 Domain Events

***REMOVED******REMOVED******REMOVED*** Event-Driven Architecture
Alle wichtigen Business-Events werden publiziert:

- `hr.employee.created|updated|deactivated|reactivated`
- `hr.role.created|updated|deleted`
- `hr.time_entry.created|approved|rejected`
- `hr.leave.requested|approved|rejected`
- `hr.shift.created|assigned|unassigned`
- `hr.payroll.prepared|locked|exported`

***REMOVED******REMOVED******REMOVED*** Event-Consumer (Finance-Domain)
Finance-Domain hört insbesondere auf:
- `hr.payroll.exported` - Payroll-Daten für FiBu-Integration
- Enthält Summen je Mitarbeiter/Periode + Referenzen
- **Keine doppelte Steuer-/Kontenlogik in HR**

***REMOVED******REMOVED*** 🔌 Abgrenzung zu anderen Domains

***REMOVED******REMOVED******REMOVED*** Finance-Domain
- Finance erstellt Buchungssätze, Zahlläufe, Kontenabgleiche
- HR liefert Payroll-Export-Daten via Events
- **Keine doppelte Steuer-/Kontenlogik in HR**

***REMOVED******REMOVED******REMOVED*** CRM-Domain
- Personendaten der Mitarbeiter nicht in CRM pflegen
- HR ist authoritative für Mitarbeiterdaten
- CRM kann via BFF "Mitarbeiterkontakt" anzeigen

***REMOVED******REMOVED******REMOVED*** Auth/Shared
- Systemweite Rollen/Permissions aus `@valero-neuroerp/auth`
- HR-Role dient fachlicher HR-Rollenvergabe
- Duplikate vermeiden, Mappings vorsehen

***REMOVED******REMOVED*** 🧪 Testing

***REMOVED******REMOVED******REMOVED*** Unit Tests
- Domain-Entitäten und Business Logic
- Repository-Implementierungen
- Service-Layer Use Cases

***REMOVED******REMOVED******REMOVED*** Integration Tests
- API-Endpunkte mit Supertest
- Database-Integration mit Test-Container
- Event-Publishing und -Consumption

***REMOVED******REMOVED******REMOVED*** Contract Tests
- Zod-Schemas für Type Safety
- OpenAPI-Schema Snapshots
- Event-Schema Validation

***REMOVED******REMOVED*** 📈 Observability

***REMOVED******REMOVED******REMOVED*** Logging
- Strukturierte Logs mit Pino
- Request-ID für Tracing
- Sensible Daten maskiert

***REMOVED******REMOVED******REMOVED*** Metrics
- OpenTelemetry Integration
- Custom HR-Metrics (Employee Count, Time Tracking Stats)
- Performance-Monitoring

***REMOVED******REMOVED******REMOVED*** Health Checks
- `/health` - Service Status
- `/ready` - Database + Dependencies
- `/live` - Basic Liveness

***REMOVED******REMOVED*** 🚀 Deployment

***REMOVED******REMOVED******REMOVED*** Production Checklist
- [ ] Environment Variables konfiguriert
- [ ] Database Migrations ausgeführt
- [ ] JWKS-URL korrekt gesetzt
- [ ] NATS/Kafka-Verbindung getestet
- [ ] Health Checks funktional
- [ ] OpenAPI-Dokumentation verfügbar
- [ ] Monitoring/Alerting konfiguriert

***REMOVED******REMOVED******REMOVED*** Scaling Considerations
- Horizontal Scaling mit Load Balancer
- Database Connection Pooling
- Event-Queue Partitioning nach Tenant
- Redis für Session/Cache (optional)

***REMOVED******REMOVED*** 📚 API-Dokumentation

Nach dem Start verfügbar unter:
- **Swagger UI**: http://localhost:3030/docs
- **OpenAPI JSON**: http://localhost:3030/docs/json

***REMOVED******REMOVED*** 🤝 Contributing

1. Feature Branch erstellen
2. Tests schreiben/aktualisieren
3. Code-Review durchführen
4. CI/CD Pipeline durchlaufen lassen
5. Merge nach Main Branch

***REMOVED******REMOVED*** 📄 License

Proprietary - VALEO NeuroERP 3.0


