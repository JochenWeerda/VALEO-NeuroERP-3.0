# Customer Picker - Plan (2026-04-14)

## Ziel

Im Dialog "Neuen Vertriebsvorgang starten" und spaeter ueberall, wo Kunden gewaehlt werden, soll die Kundenauswahl schnell, inline und UX-konsistent erfolgen - mit Option, bei Bedarf einen neuen Kunden anzulegen.

## Problem

Der alte Defaultpfad nutzte `CustomerSelectionDialog`: Modal, Suche, Tabelle, Row-Klick plus OK-Klick. Das war fuer den schnellen Order-to-Cash-Einstieg zu traege, vor allem wegen grosser Response-Payloads und Suche ohne gezielten Typeahead-Pfad.

## Vorbilder

- Odoo Many2one-Feld: Inline-Combobox, wenige Live-Treffer, letzter Eintrag "+ Neu anlegen", separater Suchdialog fuer Power-User.
- SAP / Business Central: Value Help mit serverseitig optimierten Indizes.
- Salesforce / HubSpot: Typeahead mit Prefetch zuletzt genutzter Datensaetze.

## Umsetzung

### 1. Backend schneller machen

- Alembic-Migration `crm_customers_search_index_20260414`:
- `CREATE EXTENSION IF NOT EXISTS pg_trgm`
- GIN-Index `ix_customers_company_name_trgm` auf `domain_crm.customers.company_name gin_trgm_ops`
- GIN-Index `ix_customers_customer_number_trgm` auf `customer_number gin_trgm_ops`
- Zusatzindex `ix_customers_updated_at` fuer den Recent-Pfad
- Neuer Endpoint `GET /api/v1/crm/customers/quick-search?q=...&limit=8`:
- Nur minimale Felder: `id`, `customer_number`, `company_name`, `city`, `postal_code`, `is_active`
- Prefix-Boost: Kundennummer vor Name, danach alphabetisch
- Neuer Endpoint `GET /api/v1/crm/customers/recent?limit=10`:
- MVP: Sortierung nach `updated_at DESC` je Tenant, bis ein echtes User-Last-Used-Log existiert

### 2. Frontend: `CustomerCombobox`

- Datei: `packages/frontend-web/src/components/crm/CustomerCombobox.tsx`
- `cmdk` Command plus Popover
- 250 ms Debounce
- Bei leerem Input wird `/recent` genutzt
- Ab zwei Zeichen wird `/quick-search` genutzt
- Eintrag "+ Neuen Kunden anlegen" navigiert in den kanonischen Verkaufs-Neuanlagepfad:
- `/verkauf/kunde-neu?returnTo=<currentHref>&initialName=<input>`

### 3. Integration in FlowSpineWorkspace

- Datei: `packages/frontend-web/src/components/workflow/FlowSpineWorkspace.tsx`
- Nur `order-to-cash` nutzt die neue `CustomerCombobox`; andere Prozesse behalten das freie Partner-Textfeld.
- Der Flow haelt neben `partner_name` auch `customerId` und `customerNumber`.
- Nach Vorgangsanlage uebergibt der Order-to-Cash-Handover `customerId` und `customerNumber` an den Order-Editor.
- Der Order-Editor liest `customerId`/`customerNumber` beim Workflow-Einstieg und prefilled den Kunden direkt aus `/api/v1/crm/customers/{id}`; faellt der Read kurzfristig aus, bleibt ein minimaler Fallback aus den Query-Parametern erhalten.
- Der Flow-Spine-Workspace loest den kompakten Kundenkontext fuer bestehende Instanzen ueber `domain_crm.customers.business_partner_id` auf, statt `customer_id` faelschlich als `partner_id` zu interpretieren.

### 4. Ruecksprung aus der Kundenanlage

- Alias-Route `packages/frontend-web/src/pages/verkauf/kunde-neu.tsx` erhaelt Query-Parameter beim Redirect auf `/verkauf/kunde/neu`.
- Kanonische Maske `packages/frontend-web/src/pages/verkauf/kunden-stamm.tsx` liest `initialName` und `returnTo`.
- Nach erfolgreichem Speichern navigiert die Maske zu `returnTo` mit:
- `newCustomerId`
- `newCustomerName`
- `newCustomerNumber`
- `openNewInstance=1`
- `FlowSpineWorkspace` liest diese Query-Parameter, oeffnet den Dialog erneut und selektiert den neuen Kunden.

### 5. Erweiterte Suche

- Die Combobox bleibt der Defaultweg.
- "Erweiterte Suche ..." oeffnet weiterhin den bestehenden `CustomerSelectionDialog`.
- Auswahl aus dem Dialog wird in denselben `CustomerLite`-State gemappt.

## Nicht im Scope

- Article-Picker im gleichen Stil.
- Echtes User-Last-Used-Log mit `domain_crm.customer_usage`.
- Elasticsearch/OpenSearch; Trigram reicht als erster Schritt.

## Definition of Done

- `GET /api/v1/crm/customers/quick-search?q=ab` liefert schlanke Typeahead-Daten.
- `GET /api/v1/crm/customers/recent` liefert Recent-Daten fuer den Prefetch.
- Im `FlowSpineWorkspace`-Dialog laesst sich ein Kunde per Typeahead auswaehlen.
- "+ Neuen Kunden anlegen" oeffnet die kanonische Kundenanlage.
- Nach dem Speichern springt die App zurueck in den Flow-Spine-Dialog mit dem neuen Kunden vorausgewaehlt.
- `CustomerSelectionDialog` bleibt als "Erweiterte Suche ..." erreichbar.
- Frontend-Typecheck ist gruen.

## Verifikation 2026-04-15

- Browser-Use: `/workflow/flow-spine-order-to-cash` -> `Neuer Vorgang` -> `Neuen Kunden anlegen` -> Kunden speichern -> Rueckkehr in den Dialog mit vorausgewaehltem Kunden -> `Vorgang anlegen` -> `/sales/order-editor?...&customerId=...&customerNumber=...`.
- Typecheck: `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`.
- API-Regression: `pytest tests/test_flow_spines_api.py tests/test_customers_picker_api.py -q --no-cov`.
