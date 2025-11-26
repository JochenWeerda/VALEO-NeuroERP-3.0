# Sales & Order-to-Cash Capability Model - Reference Taxonomy

Dieses Dokument definiert die Referenz-Taxonomie für Sales/Order-to-Cash-Funktionalitäten, basierend auf SAP SD, Oracle Sales Cloud, Odoo Sales und anderen führenden ERP-Systemen.

## 1. CRM / Lead-to-Opportunity

### 1.1 Lead-Erfassung & Quellen (SALES-CRM-01)
- Lead Erfassung (Webform, Import, API)
- Lead Quellen (Website, Event, Referral, etc.)
- Lead Qualifizierung (BANT: Budget, Authority, Need, Timeline)
- Lead Scoring (automatisch/manuell)
- Lead Conversion zu Opportunity/Kontakt
- Lead Duplikatserkennung
- Lead Status-Workflow (New, Qualified, Contacted, Converted, Lost)

### 1.2 Kunden-/Kontaktstamm (Sales-Sicht) (SALES-CRM-02)
- Kundenstamm (Customer Master: Name, Adresse, Kontaktdaten)
- Kundenadressen (Billing Address, Shipping Address, Contact Addresses)
- Kontaktstamm (Contact Master: Name, Role, Email, Phone)
- Kontaktzuordnung (Contacts zu Kunden)
- Kundenklassifizierung (Customer Groups, Customer Types, Segments)
- Kreditlimit (Credit Limit, Credit Check)
- Zahlungsbedingungen (Payment Terms, Discount Terms)
- Preisgruppe (Price Group, Customer Price List)
- Steuerinformationen (Tax ID, VAT ID, Tax Category)

### 1.3 Opportunities / Pipeline (SALES-CRM-03)
- Opportunity Erstellung (aus Lead oder manuell)
- Opportunity Pipeline (Stages: Prospecting, Qualification, Proposal, Negotiation, Closed Won/Lost)
- Opportunity Wahrscheinlichkeit & Forecast
- Opportunity Value & Revenue Recognition
- Opportunity Team Assignment (Sales Rep, Manager)
- Opportunity Products/Items
- Opportunity Quotes (Angebote verknüpfen)

### 1.4 Aktivitäten & Aufgaben (SALES-CRM-04)
- Aktivitäten (Calls, Meetings, Emails, Tasks)
- Aktivitätszuordnung (zu Lead, Opportunity, Customer, Contact)
- Aktivitätshistorie (Activity History, Interaction Log)
- Aufgabenverwaltung (Task Management, Reminders, Follow-ups)
- Kalenderintegration (Calendar Sync)

### 1.5 Forecasting & Ziele (SALES-CRM-05)
- Sales Forecast (Revenue Forecast, Pipeline Forecast)
- Zielvorgaben (Sales Targets, Quotas)
- Performance-Tracking (Sales Rep Performance, Team Performance)
- Forecast-Analyse (Forecast Accuracy, Variance Analysis)

## 2. Produkt / Preis

### 2.1 Produktkatalog Verkauf (SALES-PRD-01)
- Produktstamm (Product Master: Name, Beschreibung, EAN, SKU)
- Produktvarianten (Product Variants: Größe, Farbe, etc.)
- Produktkategorien (Product Categories, Hierarchie)
- Produktbilder (Product Images, Media)
- Produktverfügbarkeit (Stock Status, Availability)
- Produktpreise (Product Prices, Price Lists)

### 2.2 Preislisten & Preisfindung (SALES-PRC-01)
- Preislisten (Customer Price Lists, Product Price Lists)
- Preisregeln (Condition Records: Kunde, Material, Menge, Datum)
- Preisfindung (Price Determination, Price Calculation)
- Sonderpreise (Special Prices, Contract Prices)
- Preisvalidierung (Minimum Price, Maximum Discount)
- Preisauskunft (Price Inquiry API)

### 2.3 Rabatte/Gutschriften/Bonifikationen (SALES-PRC-02)
- Rabattregeln (Customer Discounts, Volume Discounts, Promotions)
- Positionsrabatte (Line Item Discounts)
- Header-Rabatte (Header Discounts)
- Kundenrabatte (Customer-Specific Discounts)
- Volumenrabatte (Volume-Based Discounts)
- Rabattfreigabe (Discount Approval Workflow)
- Gutschriften (Credit Notes, Bonuses)

### 2.4 Steuern im Verkauf (SALES-PRC-03)
- Steuerschlüssel (Tax Codes, Tax Categories)
- Steuerberechnung (Tax Calculation: VAT, Sales Tax)
- Steuerregeln (Tax Rules: Country, Region, Product Type)
- Reverse Charge (Reverse Charge Mechanism)
- Steuerausweis (Tax Display, Tax Breakdown)
- Steuerberichte (Tax Reports, Tax Returns)

## 3. Angebot / Quote-to-Order

### 3.1 Angebotsmanagement (SALES-QTN-01)
- Angebotserstellung (manuell, aus Opportunity, aus Template)
- Angebotspositionen (Items, Mengen, Preise, Rabatte)
- Angebotsvalidierung (Preise, Verfügbarkeit, Kreditlimit)
- Angebotsversionierung (Revisionen, Version History)
- Angebotsablauf (Expiry Date, Auto-Expiry)
- Angebotskonvertierung zu Auftrag

### 3.2 Angebotsdokumente (SALES-QTN-02)
- Angebotsversand (PDF, Email)
- Angebotsvorlagen (Quote Templates, Layouts)
- Angebotsdruck (Print Quotes)
- Angebotsarchivierung (Quote Archive)

### 3.3 Angebotsvergleich & Verhandlungsstatus (SALES-QTN-03)
- Angebotsvergleich (Quote Comparison, Competitive Analysis)
- Verhandlungsstatus (Negotiation Status, Stages)
- Angebotshistorie (Quote History, Revisions)

## 4. Order Management

### 4.1 Auftragserfassung (Sales Order) (SALES-ORD-01)
- Auftragserstellung (aus Quote, manuell, Import)
- Auftragspositionen (Items, Mengen, Preise, Rabatte)
- Auftragsvalidierung (Kreditlimit, Verfügbarkeit, Preise)
- Auftragsstatus (Draft, Confirmed, In Delivery, Delivered, Invoiced, Cancelled)
- Auftragsbestätigung (Order Confirmation PDF/Email)
- Auftragskopie (Copy Order, Repeat Order)

### 4.2 Auftragsänderung & Storno (SALES-ORD-02)
- Auftragsänderungen (Change Management, Amendments)
- Änderungshistorie (Change History, Audit Trail)
- Auftragsstorno (Cancellation, Reason Codes)
- Stornobestätigung (Cancellation Confirmation)

## 5. Fulfillment

### 5.1 Lieferabwicklung (SALES-DLV-01)
- Lieferungserstellung (aus Auftrag, manuell)
- Teil-/Restlieferungen (Partial Delivery, Backorder)
- Lieferpositionen (Items, Mengen, Lagerort)
- Lieferstatus (Draft, Picked, Shipped, Delivered)
- Lieferbestätigung (Delivery Note PDF)
- Lieferstorno (Return Delivery)

### 5.2 Versandarten & Tracking (SALES-DLV-02)
- Versandarten (Shipping Methods: Standard, Express, Pickup)
- Versandkosten (Shipping Costs, Freight Calculation)
- Spediteur-Integration (Carrier API: DHL, UPS, etc.)
- Versandetikett (Shipping Label Generation)
- Versandverfolgung (Tracking Integration, Tracking Numbers)

### 5.3 Dropship / Direktversand (SALES-DLV-03)
- Dropship-Integration (Drop Shipping, Direct Shipping)
- Lieferantenversand (Supplier Shipping)
- Direktversand (Direct Delivery to Customer)

## 6. Billing-to-Cash

### 6.1 Rechnungsstellung (SALES-BIL-01)
- Rechnungserstellung (aus Lieferung, aus Auftrag, manuell)
- Rechnungspositionen (Items, Mengen, Preise, Rabatte, Steuern)
- Rechnungsvalidierung (Preise, Steuern, Kreditlimit)
- Rechnungsstatus (Draft, Posted, Paid, Cancelled)
- Rechnungsversand (PDF, Email)
- Rechnungsstorno (Credit Memo, Reversal)
- Rechnungsänderungen (Corrections, Amendments)

### 6.2 E-Rechnung & Formate (SALES-BIL-02)
- E-Rechnung Export (XRechnung, ZUGFeRD, PEPPOL)
- E-Rechnung Validierung (Schema Validation)
- E-Rechnung Versand (Email, Portal, API)
- E-Rechnung Status (Sent, Delivered, Read, Accepted, Rejected)

### 6.3 Forderungsmanagement / Mahnung (SALES-COL-01)
- Mahnstufen (Dunning Levels: Reminder 1, Reminder 2, Final Notice)
- Mahngebühren (Dunning Fees, Late Payment Fees)
- Mahnversand (Dunning Letter PDF/Email)
- Mahnsperre (Dunning Block: keine Lieferung bei offenen Forderungen)
- Inkasso-Integration (Collection Agency Integration)

### 6.4 Zahlungseingänge & Ausgleich (SALES-PAY-01)
- Zahlungseingang (Payment Receipt, Bank Import)
- Zahlungszuordnung (Payment Matching zu Rechnungen)
- Zahlungsarten (Cash, Bank Transfer, Credit Card, SEPA)
- Zahlungsstatus (Pending, Received, Matched, Overpaid)
- Zahlungsverfolgung (Payment Tracking, Aging)

## 7. Retouren / Reklamation

### 7.1 Retourenprozess (RMA) (SALES-RMA-01)
- RMA-Erstellung (Return Merchandise Authorization)
- Retourengründe (Return Reasons, Return Codes)
- Retourenvalidierung (Original Order/Invoice Reference)
- Retourenstatus (Requested, Approved, Received, Processed)
- Retourenverarbeitung (Return Processing, Refund)

### 7.2 Reklamation & Ersatz (SALES-RMA-02)
- Reklamationserfassung (Complaint Management)
- Reklamationsgründe (Complaint Reasons, Categories)
- Ersatzlieferung (Replacement Delivery)
- Ersatzprodukt (Replacement Product)

## 8. Reporting

### 8.1 Standard-Reports (SALES-REP-01)
- Umsatzberichte (Sales Revenue Reports: by Customer, Product, Region, Period)
- Auftragsberichte (Order Reports: Open Orders, Order Status, Order History)
- Lieferberichte (Delivery Reports: Delivery Status, Delivery Performance)
- Rechnungsberichte (Invoice Reports: Open Invoices, Invoice Status, Invoice History)
- Kundenberichte (Customer Reports: Customer Revenue, Customer Activity)

### 8.2 Drilldown & Belegkette (SALES-REP-02)
- Belegkette (Document Chain: Quote → Order → Delivery → Invoice)
- Drilldown (Drilldown from Summary to Detail)
- Belegverfolgung (Document Tracking, Document Flow)

### 8.3 Sales Analytics / KPI (SALES-REP-03)
- Pipeline-Analyse (Opportunity Pipeline, Conversion Rates)
- Forecast-Analyse (Sales Forecast, Revenue Forecast)
- Performance-Analyse (Sales Rep Performance, Team Performance)
- Trend-Analyse (Sales Trends, Product Trends, Customer Trends)
- KPI-Dashboards (Key Performance Indicators: Revenue, Orders, Conversion)

## 9. Rollen / Workflows

### 9.1 Rollenmodell Sales (SALES-AUTH-01)
- Rollendefinition (Sales Roles: Sales Rep, Sales Manager, Sales Director)
- Berechtigungen (Permissions: Create, Read, Update, Delete, Approve)
- Benutzerzuordnung (User Assignment to Roles)
- Rollenbasierte Sichtbarkeit (Role-Based Visibility)

### 9.2 Freigabeworkflows (SALES-AUTH-02)
- Freigaberegeln (nach Wert, Rabatt, Kunde, Material)
- Freigabestufen (Multi-Level Approval)
- Freigabestatus (Pending, Approved, Rejected)
- Freigabehistorie (Audit Trail)
- Freigabebenen (Sales Rep → Manager → Director)

## 10. Integrationen

### 10.1 API / Import / Export (SALES-INT-01)
- REST API (REST API für Sales-Daten)
- GraphQL API (GraphQL API für Sales-Daten)
- Import/Export (CSV, Excel, JSON)
- Webhooks (Webhooks für Events)

### 10.2 EDI / B2B Integration (SALES-INT-02)
- EDI Standards (EDIFACT, X12)
- EDI Mapping (EDI Mapping, Transformation)
- EDI Communication (EDI Communication, Protocols)
- B2B Integration (B2B Partner Integration)

### 10.3 Shop / POS / Marktplätze (SALES-INT-03)
- Webshop-Integration (Order Import, Product Sync)
- POS-Integration (Point of Sale Integration)
- Marketplace-Integration (Amazon, eBay, etc.)
- Cart-Abandonment (Abandoned Cart Recovery)

## Reifegrad-Bewertung

- **SAP SD-ähnlich**: Vollständige Funktionalität auf Enterprise-Level
- **Odoo Sales-ähnlich**: Gute Funktionalität für mittelständische Unternehmen
- **Basic**: Grundlegende Funktionalität vorhanden
- **Partial**: Teilweise implementiert
- **Missing**: Nicht vorhanden

