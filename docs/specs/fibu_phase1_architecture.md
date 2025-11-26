# FiBu Phase 1 – Zielarchitektur & Foundations
> **Status**: In Umsetzung  
> **Datum**: 2025-11-14  
> **Referenz**: `docs/specs/fibu_architektur_spezifikation.md`, `docs/adr/adr-001-fibu-domain-reuse-vs-rewrite.md`, `docs/adr/adr-002-fibu-frontend-api-layer.md`

## 1. Microservice-Zerlegung

### Core Services
- **fibu-core**: PRIMANOTA, Verbuchung, Periodeninfo
- **fibu-master-data**: Kontenrahmen, Debitoren/Kreditoren, Konstanten
- **fibu-gateway**: Anti-Corruption-Layer & API-Gateway

### Shared Libraries
- **fibu-shared**: GoBD-Compliance, Hash-Chains, Event-Schema
- **fibu-auth**: Rollenbasierte AuthZ (FiBu-Rollenmodell)
- **fibu-events**: Standardisierte Event-Definitionen

## 2. Event-Schema & Kommunikation

### FiBu-Events (NATS)
```yaml
# Buchungs-Events
fibu.booking.created:
  booking_id: uuid
  account_id: string
  amount: decimal
  period: string
  document_id: uuid

# Stammdaten-Events
fibu.master_data.account.updated:
  account_id: string
  account_number: string
  account_name: string

# OP-Events
fibu.op.created:
  op_id: uuid
  customer_id: string
  amount: decimal
  due_date: date
```

### Anti-Corruption-Layer
- **Sales → FiBu**: `sales.invoice.created` → `fibu.booking.create`
- **Inventory → FiBu**: `inventory.stock.changed` → `fibu.booking.adjust`
- **Workflow → FiBu**: `workflow.approval.granted` → `fibu.booking.approve`

## 3. API-Spezifikation

### fibu-gateway Endpoints
```yaml
POST /api/v1/bookings
  - Transformiert externe Events
  - Validiert gegen GoBD-Regeln
  - Erzeugt FiBu-Events

GET /api/v1/accounts/{id}/balance
  - Liefert kontextabhängige Salden
  - Berücksichtigt Freigaben

POST /api/v1/documents
  - Upload mit document_id
  - Verknüpfung mit Buchungen
```

## 4. GoBD-Compliance Framework

### Audit-Trail
- Write-Ahead-Logging für alle Buchungen
- Hash-Chains über Perioden
- Unveränderliche Speicherung

### Rollenmodell
- **Sachbearbeiter**: Erfassung, keine Freigabe
- **Freigeber**: Buchungen > X EUR freigeben
- **Steuerberater**: Lesend, Reports
- **Admin**: Konfiguration, Stornos

## 5. Infrastructure as Code

### Docker Compose (Development)
```yaml
services:
  fibu-core:
    build: ./services/finance/fibu-core
    environment:
      - DATABASE_URL=postgresql://fibu:fibu@postgres:5432/fibu
      - NATS_URL=nats://nats:4222
  
  fibu-gateway:
    build: ./services/finance/fibu-gateway
    ports:
      - "8000:8000"
    depends_on:
      - fibu-core
      - nats
```

### Helm Charts (Production)
- Separate Charts pro Service
- ConfigMaps für Event-Schemas
- Secrets für DB/Auth

