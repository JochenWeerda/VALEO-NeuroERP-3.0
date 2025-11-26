***REMOVED*** ERP Capability Model - Reference Taxonomy

Dieses Dokument definiert die Referenz-Taxonomie für ERP-Funktionalitäten, basierend auf SAP, Oracle, Odoo und anderen führenden ERP-Systemen.

***REMOVED******REMOVED*** 1. Finance (Finanzwesen)

***REMOVED******REMOVED******REMOVED*** 1.1 General Ledger (Hauptbuch)
- Chart of Accounts
- Journal Entries
- Period Closing
- Financial Statements (P&L, Balance Sheet)
- Multi-Currency
- Consolidation

***REMOVED******REMOVED******REMOVED*** 1.2 Accounts Receivable (Debitoren)
- Customer Master Data
- Invoice Management
- Payment Processing
- Dunning
- Credit Management
- Aging Reports

***REMOVED******REMOVED******REMOVED*** 1.3 Accounts Payable (Kreditoren)
- Supplier Master Data
- Invoice Receipt
- Payment Processing
- Payment Terms & Discounts
- Three-Way Matching
- Aging Reports

***REMOVED******REMOVED******REMOVED*** 1.4 Assets (Anlagenbuchhaltung)
- Asset Master Data
- Depreciation Methods
- Asset Transfers
- Asset Retirement
- Asset Reports

***REMOVED******REMOVED******REMOVED*** 1.5 Treasury (Treasury)
- Bank Accounts
- Bank Reconciliation
- Cash Management
- Payment Runs
- Bank Statements Import

***REMOVED******REMOVED******REMOVED*** 1.6 Tax (Steuern)
- Tax Codes
- Tax Calculation
- Tax Reports (UStVA, etc.)
- ELSTER Integration

***REMOVED******REMOVED*** 2. Procurement (Einkauf)

**Detailliertes Capability Model:** Siehe [procurement-capability-model.md](./procurement-capability-model.md)

***REMOVED******REMOVED******REMOVED*** 2.1 Requisition (Bedarf)
- Purchase Requisition
- Approval Workflows
- Budget Check

***REMOVED******REMOVED******REMOVED*** 2.2 RFQ (Anfrage)
- Request for Quotation
- Supplier Comparison
- Quotation Evaluation

***REMOVED******REMOVED******REMOVED*** 2.3 Purchase Order (Bestellung)
- Purchase Order Creation
- Purchase Order Approval
- Purchase Order Confirmation
- Goods Receipt
- Invoice Receipt
- Three-Way Matching

***REMOVED******REMOVED******REMOVED*** 2.4 Supplier Management
- Supplier Master Data
- Supplier Evaluation
- Supplier Performance
- Contract Management

**Hinweis:** Das vollständige Procurement Capability Model mit 28 Capabilities (PROC-SUP-01 bis PROC-INT-03) ist in `procurement-capability-model.md` dokumentiert und in `matrix.csv` für die GAP-Analyse verfügbar.

***REMOVED******REMOVED*** 3. Sales & CRM (Verkauf & Kundenbeziehung)

***REMOVED******REMOVED******REMOVED*** 3.1 Sales Process
- Lead Management
- Opportunity Management
- Quotation
- Sales Order
- Delivery
- Invoice
- Credit Note

***REMOVED******REMOVED******REMOVED*** 3.2 Customer Management
- Customer Master Data
- Contact Management
- Customer Segmentation
- Customer History

***REMOVED******REMOVED******REMOVED*** 3.3 Service
- Service Orders
- Service Contracts
- Warranty Management

***REMOVED******REMOVED*** 4. Inventory / WMS (Lagerverwaltung)

***REMOVED******REMOVED******REMOVED*** 4.1 Warehouse Management
- Warehouse Structure
- Storage Locations
- Bin Management
- Stock Movements
- Stock Transfers
- Stock Counts

***REMOVED******REMOVED******REMOVED*** 4.2 Inventory Valuation
- Valuation Methods (FIFO, LIFO, Average)
- Cost Calculation
- Inventory Reports

***REMOVED******REMOVED*** 5. Manufacturing / MRP (Produktion / Materialbedarfsplanung)

***REMOVED******REMOVED******REMOVED*** 5.1 Production Planning
- Bill of Materials (BOM)
- Routing
- Production Orders
- Capacity Planning

***REMOVED******REMOVED******REMOVED*** 5.2 Production Execution
- Production Order Release
- Material Issue
- Production Confirmation
- Goods Receipt from Production

***REMOVED******REMOVED*** 6. HR / Payroll / Time (Personalwesen)

***REMOVED******REMOVED******REMOVED*** 6.1 Human Resources
- Employee Master Data
- Organizational Structure
- Position Management
- Employee History

***REMOVED******REMOVED******REMOVED*** 6.2 Payroll
- Payroll Calculation
- Salary Components
- Tax Calculation
- Social Security

***REMOVED******REMOVED******REMOVED*** 6.3 Time Management
- Time Recording
- Leave Management
- Attendance Tracking

***REMOVED******REMOVED*** 7. Projects (Projektmanagement)

***REMOVED******REMOVED******REMOVED*** 7.1 Project Structure
- Project Definition
- WBS (Work Breakdown Structure)
- Project Phases
- Milestones

***REMOVED******REMOVED******REMOVED*** 7.2 Project Execution
- Project Planning
- Resource Allocation
- Project Costs
- Project Billing

***REMOVED******REMOVED*** 8. BI / Reporting (Business Intelligence / Berichtswesen)

***REMOVED******REMOVED******REMOVED*** 8.1 Standard Reports
- Financial Reports
- Operational Reports
- Custom Reports

***REMOVED******REMOVED******REMOVED*** 8.2 Analytics
- Dashboards
- KPIs
- Data Visualization
- Ad-hoc Analysis

***REMOVED******REMOVED*** 9. Workflow / BPM / Roles (Workflow / Geschäftsprozessmanagement / Rollen)

***REMOVED******REMOVED******REMOVED*** 9.1 Workflow Engine
- Workflow Definition
- Approval Workflows
- Task Management
- Notification System

***REMOVED******REMOVED******REMOVED*** 9.2 Role Management
- Role Definition
- Permission Management
- User Assignment

***REMOVED******REMOVED*** 10. Integration / EDI / API (Integration)

***REMOVED******REMOVED******REMOVED*** 10.1 EDI (Electronic Data Interchange)
- EDI Standards (EDIFACT, X12)
- EDI Mapping
- EDI Communication

***REMOVED******REMOVED******REMOVED*** 10.2 API
- REST API
- GraphQL API
- Webhooks
- API Documentation

***REMOVED******REMOVED******REMOVED*** 10.3 External Systems
- Bank Integration
- Tax Authority Integration (ELSTER)
- DMS Integration
- E-Commerce Integration

***REMOVED******REMOVED*** Reifegrad-Bewertung

- **SAP-ähnlich**: Vollständige Funktionalität auf Enterprise-Level
- **Odoo-ähnlich**: Gute Funktionalität für mittelständische Unternehmen
- **Basic**: Grundlegende Funktionalität vorhanden
- **Partial**: Teilweise implementiert
- **Missing**: Nicht vorhanden

