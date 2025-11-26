# ERP Capability Model - Reference Taxonomy

Dieses Dokument definiert die Referenz-Taxonomie für ERP-Funktionalitäten, basierend auf SAP, Oracle, Odoo und anderen führenden ERP-Systemen.

## 1. Finance (Finanzwesen)

### 1.1 General Ledger (Hauptbuch)
- Chart of Accounts
- Journal Entries
- Period Closing
- Financial Statements (P&L, Balance Sheet)
- Multi-Currency
- Consolidation

### 1.2 Accounts Receivable (Debitoren)
- Customer Master Data
- Invoice Management
- Payment Processing
- Dunning
- Credit Management
- Aging Reports

### 1.3 Accounts Payable (Kreditoren)
- Supplier Master Data
- Invoice Receipt
- Payment Processing
- Payment Terms & Discounts
- Three-Way Matching
- Aging Reports

### 1.4 Assets (Anlagenbuchhaltung)
- Asset Master Data
- Depreciation Methods
- Asset Transfers
- Asset Retirement
- Asset Reports

### 1.5 Treasury (Treasury)
- Bank Accounts
- Bank Reconciliation
- Cash Management
- Payment Runs
- Bank Statements Import

### 1.6 Tax (Steuern)
- Tax Codes
- Tax Calculation
- Tax Reports (UStVA, etc.)
- ELSTER Integration

## 2. Procurement (Einkauf)

**Detailliertes Capability Model:** Siehe [procurement-capability-model.md](./procurement-capability-model.md)

### 2.1 Requisition (Bedarf)
- Purchase Requisition
- Approval Workflows
- Budget Check

### 2.2 RFQ (Anfrage)
- Request for Quotation
- Supplier Comparison
- Quotation Evaluation

### 2.3 Purchase Order (Bestellung)
- Purchase Order Creation
- Purchase Order Approval
- Purchase Order Confirmation
- Goods Receipt
- Invoice Receipt
- Three-Way Matching

### 2.4 Supplier Management
- Supplier Master Data
- Supplier Evaluation
- Supplier Performance
- Contract Management

**Hinweis:** Das vollständige Procurement Capability Model mit 28 Capabilities (PROC-SUP-01 bis PROC-INT-03) ist in `procurement-capability-model.md` dokumentiert und in `matrix.csv` für die GAP-Analyse verfügbar.

## 3. Sales & CRM (Verkauf & Kundenbeziehung)

### 3.1 Sales Process
- Lead Management
- Opportunity Management
- Quotation
- Sales Order
- Delivery
- Invoice
- Credit Note

### 3.2 Customer Management
- Customer Master Data
- Contact Management
- Customer Segmentation
- Customer History

### 3.3 Service
- Service Orders
- Service Contracts
- Warranty Management

## 4. Inventory / WMS (Lagerverwaltung)

### 4.1 Warehouse Management
- Warehouse Structure
- Storage Locations
- Bin Management
- Stock Movements
- Stock Transfers
- Stock Counts

### 4.2 Inventory Valuation
- Valuation Methods (FIFO, LIFO, Average)
- Cost Calculation
- Inventory Reports

## 5. Manufacturing / MRP (Produktion / Materialbedarfsplanung)

### 5.1 Production Planning
- Bill of Materials (BOM)
- Routing
- Production Orders
- Capacity Planning

### 5.2 Production Execution
- Production Order Release
- Material Issue
- Production Confirmation
- Goods Receipt from Production

## 6. HR / Payroll / Time (Personalwesen)

### 6.1 Human Resources
- Employee Master Data
- Organizational Structure
- Position Management
- Employee History

### 6.2 Payroll
- Payroll Calculation
- Salary Components
- Tax Calculation
- Social Security

### 6.3 Time Management
- Time Recording
- Leave Management
- Attendance Tracking

## 7. Projects (Projektmanagement)

### 7.1 Project Structure
- Project Definition
- WBS (Work Breakdown Structure)
- Project Phases
- Milestones

### 7.2 Project Execution
- Project Planning
- Resource Allocation
- Project Costs
- Project Billing

## 8. BI / Reporting (Business Intelligence / Berichtswesen)

### 8.1 Standard Reports
- Financial Reports
- Operational Reports
- Custom Reports

### 8.2 Analytics
- Dashboards
- KPIs
- Data Visualization
- Ad-hoc Analysis

## 9. Workflow / BPM / Roles (Workflow / Geschäftsprozessmanagement / Rollen)

### 9.1 Workflow Engine
- Workflow Definition
- Approval Workflows
- Task Management
- Notification System

### 9.2 Role Management
- Role Definition
- Permission Management
- User Assignment

## 10. Integration / EDI / API (Integration)

### 10.1 EDI (Electronic Data Interchange)
- EDI Standards (EDIFACT, X12)
- EDI Mapping
- EDI Communication

### 10.2 API
- REST API
- GraphQL API
- Webhooks
- API Documentation

### 10.3 External Systems
- Bank Integration
- Tax Authority Integration (ELSTER)
- DMS Integration
- E-Commerce Integration

## Reifegrad-Bewertung

- **SAP-ähnlich**: Vollständige Funktionalität auf Enterprise-Level
- **Odoo-ähnlich**: Gute Funktionalität für mittelständische Unternehmen
- **Basic**: Grundlegende Funktionalität vorhanden
- **Partial**: Teilweise implementiert
- **Missing**: Nicht vorhanden

