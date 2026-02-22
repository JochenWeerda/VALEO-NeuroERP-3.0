# Lieferschein-Erfassung: Datenfeld-Analyse & Verknüpfungen

## Übersicht

Diese Dokumentation kategorisiert alle Datenfelder der Lieferschein-Erfassungsmaske nach:
- **Eingabedaten**: Manuelle Benutzereingabe
- **Verknüpfte Daten**: Aus Stammdaten/DB vorbelegt
- **Berechnete Daten**: Durch Formeln errechnet

---

## 1. Header-Bereich (Lieferschein-Grunddaten)

### 1.1 Liefersch.-Nr.
- **Typ**: Verknüpft (Backend-generiert)
- **Quelle**: Backend generiert beim POST
- **CRUD**: READ (Auto-Generierung beim Erstellen)
- **Logik**: 
  - Neuer LS: Wird automatisch im Backend generiert beim `POST /api/v1/sales/delivery-notes`
  - Bestehender LS: Aus DB laden
  - Browse-Button: Öffnet Dialog zur Suche nach bestehenden Lieferscheinen

### 1.2 Niederlassung
- **Typ**: Verknüpft (Auswahl)
- **Quelle**: `domain_shared.branches` oder `tenant.settings.branches`
- **CRUD**: READ (Auswahl aus Liste)
- **Logik**:
  - Muss im Admin/Mandantenbereich eingerichtet werden
  - Beispiel: 0 = Hauptniederlassung, 10 = Streckengeschäft, etc.
  - Default: Hauptniederlassung (0)
  - API: `/api/v1/admin/branches` oder `/api/v1/tenant/branches`

### 1.3 Vertreter
- **Typ**: Verknüpft (Aus Debitoren-Konto)
- **Quelle**: `domain_crm.customers.vertreter` oder `domain_crm.customers.sales_rep_id`
- **CRUD**: READ (wird beim Kundenauswahl gesetzt)
- **Logik**:
  - Wird automatisch ausgewählt, wenn Kunde gewählt wird
  - Kann manuell überschrieben werden
  - API: `/api/v1/crm/contacts/{customer_id}` oder `/api/v1/crm/business-partners/{customer_id}` → `sales_rep_id` oder `vertreter`

### 1.4 Bediener
- **Typ**: Verknüpft (Aus Session)
- **Quelle**: Aktueller eingeloggter User
- **CRUD**: READ (aus `useAuth()` Hook)
- **Logik**:
  - Wird automatisch aus Session/Token geladen
  - Format: User-Kürzel (z.B. "JW")
  - API: `/api/v1/users/me` → `username` oder `short_name`
  - Frontend: `const { user } = useAuth()` → `user.username`

### 1.5 Liefer-Datum
- **Typ**: Eingabe (mit Default)
- **Quelle**: Heute (Default), manuell änderbar
- **CRUD**: CREATE/UPDATE
- **Logik**: 
  - Default: `new Date()`
  - Format: `yyyy-MM-dd` für Input-Feld

### 1.6 Uhrzeit
- **Typ**: Eingabe (mit Default)
- **Quelle**: Aktuelle Uhrzeit (Default), manuell änderbar
- **CRUD**: CREATE/UPDATE
- **Logik**: 
  - Default: `new Date().toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' })`

### 1.7 Kostenstelle
- **Typ**: Verknüpft (Auswahl)
- **Quelle**: `domain_finance.cost_centers` oder `domain_erp.kostenstellen`
- **CRUD**: READ (Auswahl)
- **Logik**:
  - Optional, kann leer bleiben (0)
  - API: `/api/v1/finance/cost-centers`

### 1.8 Lkw-Nr.
- **Typ**: Eingabe
- **Quelle**: Manuelle Eingabe
- **CRUD**: CREATE/UPDATE
- **Logik**: Optional, Default: 0

### 1.9 Gutschrift kennzeichnen
- **Typ**: Eingabe (Checkbox)
- **Quelle**: Manuelle Eingabe
- **CRUD**: CREATE/UPDATE
- **Logik**: Boolean, Default: false

### 1.10 Selbstabholung
- **Typ**: Eingabe (Checkbox)
- **Quelle**: Manuelle Eingabe
- **CRUD**: CREATE/UPDATE
- **Logik**: Boolean, Default: false

### 1.11 Frühbezug-Rechnung
- **Typ**: Eingabe (Checkbox)
- **Quelle**: Manuelle Eingabe
- **CRUD**: CREATE/UPDATE
- **Logik**: Boolean, Default: false

### 1.12 Re.-Nr. (Bezug)
- **Typ**: Eingabe (Optional)
- **Quelle**: Manuelle Eingabe oder Verknüpfung zu Rechnung
- **CRUD**: CREATE/UPDATE
- **Logik**: Referenz zu bestehender Rechnung (optional)

### 1.13 Status: gedruckt
- **Typ**: Berechnet/Verknüpft
- **Quelle**: Wird beim Drucken auf `true` gesetzt
- **CRUD**: UPDATE (nur beim Drucken)
- **Logik**: 
  - Wird automatisch auf `true` gesetzt, wenn Lieferschein gedruckt wird
  - Bei gebuchten LS: Read-only, Änderung nur mit Attestierung

### 1.14 Status: ausgeliefert
- **Typ**: Eingabe/Berechnet
- **Quelle**: Manuell oder automatisch beim Drucken
- **CRUD**: UPDATE
- **Logik**: 
  - Kann manuell gesetzt werden
  - Wird optional beim Drucken automatisch gesetzt

### 1.15 Status: fakturiert: Rechn.-Nr.
- **Typ**: Verknüpft
- **Quelle**: Wird gesetzt, wenn Lieferschein fakturiert wird
- **CRUD**: UPDATE (automatisch bei Fakturierung)
- **Logik**: 
  - Wird automatisch gefüllt, wenn aus diesem LS eine Rechnung erstellt wird
  - API: `/api/v1/sales/invoices?delivery_note_id={id}`

---

## 2. Kunden-Bereich

### 2.1 Debitor-Kto.
- **Typ**: Verknüpft (Auswahl)
- **Quelle**: `domain_crm.customers` (Dialog)
- **CRUD**: READ (Auswahl), CREATE (wenn neuer Kunde)
- **Logik**:
  - Button "..." öffnet `CustomerSelectionDialog`
  - API: `/api/v1/crm/contacts` (wie in `CustomerSelectionDialog.tsx` verwendet)
  - Alternative: `/api/v1/crm/business-partners` für erweiterte Kunden-Daten
  - Nach Auswahl werden alle Kundenfelder automatisch gefüllt

### 2.2 Kundenadresse (Name, Straße, PLZ, Ort, Telefon, Fax)
- **Typ**: Verknüpft (Aus Debitoren-Konto)
- **Quelle**: `domain_crm.customers` → `address` (JSONB)
- **CRUD**: READ (wird beim Kundenauswahl geladen)
- **Logik**:
  - Wird automatisch aus Kunden-Stammdaten geladen
  - Kann in Tabs überschrieben werden (LIEFER-ANSCHR., RECHN.-ANSCHRIFT)

### 2.3 Kredit-Limit
- **Typ**: Verknüpft (Aus Debitoren-Konto)
- **Quelle**: `domain_crm.customers.credit_limit`
- **CRUD**: READ (nur Anzeige)
- **Logik**: Wird beim Kundenauswahl angezeigt, Read-only

### 2.4 Offene Aufträge/LS-Betrag
- **Typ**: Berechnet
- **Quelle**: Aggregation aus `domain_sales.orders` und `domain_sales.delivery_notes`
- **CRUD**: READ (berechnet)
- **Logik**:
  - **Hinweis**: API-Endpunkt `/api/v1/sales/customers/{customer_id}/open-amounts` existiert noch nicht
  - Muss implementiert werden: Summe aller offenen Aufträge und Lieferscheine
  - Alternative: Frontend-seitige Aggregation über `/api/v1/sales/orders?customer_id={id}&status=open` und `/api/v1/sales/delivery-notes?customer_id={id}&status=posted`

### 2.5 "wie vorheriger LS (F11)"
- **Typ**: Verknüpft (Funktion)
- **Quelle**: Letzter Lieferschein des Kunden
- **CRUD**: READ (kopiert Daten)
- **Logik**:
  - API: `/api/v1/sales/delivery-notes?customer_id={id}&limit=1&order_by=created_at DESC`
  - Kopiert alle Felder vom letzten LS des Kunden

---

## 3. Positionen-Grid

### 3.1 Pos.-Nr.
- **Typ**: Berechnet
- **Quelle**: Auto-Increment pro Position
- **CRUD**: CREATE (automatisch)
- **Logik**: Startet bei 10, erhöht sich um 10 pro Position

### 3.2 Artikel-Nr.
- **Typ**: Verknüpft (Auswahl)
- **Quelle**: `domain_inventory.articles` (Dialog)
- **CRUD**: READ (Auswahl)
- **Logik**:
  - Button "..." öffnet `ArtikelSuchDialog`
  - API: `/api/v1/articles?search={query}&limit=50` (tatsächlicher Pfad im Backend)
  - Alternative: `/api/v1/articles/search?q={query}&limit=50` für erweiterte Suche
  - Nach Auswahl werden Artikel-Felder automatisch gefüllt

### 3.3 Bezeichnung, Bezeichnung2
- **Typ**: Verknüpft (Aus Artikel-Stammdaten)
- **Quelle**: `domain_inventory.articles.name`, `domain_inventory.articles.description`
- **CRUD**: READ (wird beim Artikelauswahl geladen)

### 3.4 Menge
- **Typ**: Eingabe
- **Quelle**: Manuelle Eingabe
- **CRUD**: CREATE/UPDATE
- **Logik**: 
  - Wird in Positions-Details eingegeben
  - Wird beim "Zeile OK" in Grid übernommen

### 3.5 Einheit
- **Typ**: Verknüpft (Aus Artikel-Stammdaten)
- **Quelle**: `domain_inventory.articles.unit`
- **CRUD**: READ (wird beim Artikelauswahl geladen)

### 3.6 Listenpreis
- **Typ**: Verknüpft/Berechnet (Preislogik)
- **Quelle**: Komplexe Preislogik (siehe Abschnitt "Preislogik")
- **CRUD**: READ (berechnet)
- **Logik**: 
  - Basis: `domain_inventory.articles.sales_price`
  - Anpassung durch:
    - Staffelpreislisten (Artikelgruppen)
    - Kunden-Rabatte
    - Mitarbeiter-Rolle-Rabatte
    - Vertragsrabatte

### 3.7 Rabatt
- **Typ**: Eingabe/Berechnet
- **Quelle**: 
  - Basis: Aus Kunden-Stammdaten (`domain_crm.customers.discount`)
  - Oder aus Mitarbeiter-Rolle
  - Oder manuell überschreibbar
- **CRUD**: CREATE/UPDATE
- **Logik**: 
  - Default aus Kunden-Rabatt
  - Kann manuell angepasst werden

### 3.8 Art
- **Typ**: Verknüpft (Aus Artikel-Stammdaten)
- **Quelle**: `domain_inventory.articles.category` oder `domain_inventory.articles.article_type`
- **CRUD**: READ

### 3.9 Netto-Preis
- **Typ**: Berechnet
- **Quelle**: Formel
- **CRUD**: READ (berechnet)
- **Formel**: `listenpreis * (1 - rabatt / 100)`

### 3.10 Netto-Betrag
- **Typ**: Berechnet
- **Quelle**: Formel
- **CRUD**: READ (berechnet)
- **Formel**: `menge * nettoPreis`

### 3.11 Niederlassung (pro Position)
- **Typ**: Verknüpft (aus Header)
- **Quelle**: Wird vom Header übernommen
- **CRUD**: READ (kopiert)

### 3.12 Lagerhalle, Lagerfach
- **Typ**: Verknüpft (Aus Artikel-Stammdaten oder Lagerort)
- **Quelle**: 
  - `domain_inventory.articles.lagerorte` (JSONB Array)
  - Oder `domain_inventory.warehouses` + `domain_inventory.stock_locations`
- **CRUD**: READ/Auswahl
- **Logik**: 
  - Default aus Artikel-Stammdaten
  - Kann manuell geändert werden
  - API: `/api/v1/inventory/warehouses` und `/api/v1/inventory/locations`

### 3.13 Chargen..., Serien-Nr.
- **Typ**: Eingabe/Verknüpft
- **Quelle**: 
  - Wenn `domain_inventory.articles.chargenpflicht = true`: Eingabe erforderlich
  - API: `/api/v1/inventory/lots?article_id={id}`
- **CRUD**: CREATE/UPDATE

### 3.14 Erlöskonto
- **Typ**: Verknüpft (Aus Artikel-Stammdaten oder Konto-Zuordnung)
- **Quelle**: 
  - `domain_inventory.articles.erloskonto` (wenn vorhanden)
  - Oder `domain_finance.account_mappings` (Artikel → Konto)
- **CRUD**: READ
- **Logik**: 
  - API: `/api/v1/finance/account-mappings?article_id={id}`

### 3.15 MWSt. %
- **Typ**: Verknüpft (Aus Artikel-Stammdaten)
- **Quelle**: `domain_inventory.articles.mehrwertsteuer_prozent`
- **CRUD**: READ
- **Logik**: 
  - Default: 19% (Standard-MWSt)
  - Kann aus Artikel-Stammdaten kommen (z.B. 7% für Lebensmittel)

---

## 4. Positions-Details

### 4.1 verfügbar: Menge
- **Typ**: Berechnet/Verknüpft
- **Quelle**: Lagerbestand
- **CRUD**: READ (berechnet)
- **Logik**:
  - API: `/api/v1/inventory/stock?article_id={id}&warehouse_id={warehouse_id}`
  - Berechnet: `current_stock - reserved_stock`

### 4.2 Kontrakt-Nr.
- **Typ**: Verknüpft (Aus Verträgen)
- **Quelle**: `domain_contracts.contracts` (Kunden-Verträge)
- **CRUD**: READ (Auswahl)
- **Logik**:
  - API: `/api/v1/contracts?customer_id={id}&status=active`
  - Optional: Kann manuell eingegeben werden

### 4.3 skontierf. (Checkbox)
- **Typ**: Eingabe/Verknüpft
- **Quelle**: 
  - Default: Aus Artikel-Stammdaten oder Kunden-Stammdaten
  - Kann manuell überschrieben werden
- **CRUD**: CREATE/UPDATE

### 4.4 Fremdware (Checkbox)
- **Typ**: Eingabe
- **Quelle**: Manuelle Eingabe
- **CRUD**: CREATE/UPDATE

---

## 5. Summen-Bereich

### 5.1 Gewicht: __ kg
- **Typ**: Berechnet
- **Quelle**: Aggregation
- **CRUD**: READ (berechnet)
- **Formel**: `SUM(menge * artikel.weight)` über alle Positionen

### 5.2 Netto Gesamt
- **Typ**: Berechnet
- **Quelle**: Aggregation
- **CRUD**: READ (berechnet)
- **Formel**: `SUM(nettoBetrag)` über alle Positionen

### 5.3 MWSt.
- **Typ**: Berechnet
- **Quelle**: Aggregation
- **CRUD**: READ (berechnet)
- **Formel**: 
  - Pro Position: `nettoBetrag * (mwstProzent / 100)`
  - Gesamt: `SUM(MWSt pro Position)`

### 5.4 Brutto
- **Typ**: Berechnet
- **Quelle**: Aggregation
- **CRUD**: READ (berechnet)
- **Formel**: `nettoGesamt + mwstGesamt`

---

## 6. Preislogik (Komplex)

### 6.1 Basis-Preis
- **Quelle**: `domain_inventory.articles.sales_price`
- **API**: `/api/v1/inventory/articles/{id}`

### 6.2 Staffelpreislisten (Artikelgruppen)
- **Quelle**: `domain_pricing.price_lists`
- **Logik**:
  - Suche nach Preisliste für:
    - Artikelgruppe (`domain_inventory.articles.warengruppe`)
    - Kunde (`domain_crm.customers.price_group`)
    - Gültigkeitsdatum
  - API: `/api/v1/pricing/price-lists?article_group={group}&customer_id={id}&date={date}`
- **CRUD**: READ (Auswahl)

### 6.3 Kunden-Rabatte
- **Quelle**: `domain_crm.customers.discount` oder `domain_crm.business_partner_pricing_rules`
- **Logik**:
  - Basis-Rabatt aus Kunden-Stammdaten
  - Zusätzliche Rabatte aus Pricing-Rules
  - API: `/api/v1/crm/customers/{id}/pricing-rules`
- **CRUD**: READ

### 6.4 Mitarbeiter-Rolle-Rabatte
- **Quelle**: `domain_shared.users.roles` → Rabatt-Regeln
- **Logik**:
  - Prüfe Rolle des aktuellen Users
  - Suche Rabatt-Regel für diese Rolle
  - API: `/api/v1/pricing/discount-rules?role={role}`
- **CRUD**: READ

### 6.5 Vertragsrabatte
- **Quelle**: `domain_contracts.contracts` → Rabatt-Bedingungen
- **Logik**:
  - Wenn Kontrakt-Nr. gesetzt: Lade Vertrag
  - Prüfe Rabatt-Bedingungen im Vertrag
  - API: `/api/v1/contracts/{contract_id}/discounts`
- **CRUD**: READ

### 6.6 Preisberechnung (Hierarchische Kaskade)
**Wichtig**: Rabatte werden **nicht additiv** angewendet, sondern **hierarchisch** (wie in zvoove/Landhandel üblich).

**Priorität (Kaskade)**:
1. **Staffelpreisliste** (höchste Priorität, wenn vorhanden) → **ersetzt** Basis-Preis
2. **Vertragsrabatt** (wenn Kontrakt-Nr. gesetzt) → **einzelner Rabatt** wird angewendet
3. **Kunden-Rabatt** (aus Stammdaten) → **einzelner Rabatt** wird angewendet (nur wenn kein Vertragsrabatt)
4. **Mitarbeiter-Rolle-Rabatt** → **einzelner Rabatt** wird angewendet (nur wenn kein Kunden-Rabatt)
5. **Basis-Preis** (Fallback) → `artikel.sales_price`

**Formel (Hierarchisch)**:
```
// Schritt 1: Listenpreis bestimmen
listenpreis = staffelpreis (wenn vorhanden) ODER artikel.sales_price

// Schritt 2: EINEN Rabatt anwenden (höchste Priorität)
rabatt = vertragsrabatt (wenn Kontrakt-Nr. gesetzt)
       ODER kundenrabatt (wenn vorhanden)
       ODER mitarbeiterrabatt (wenn vorhanden)
       ODER 0

// Schritt 3: Netto-Preis berechnen
nettoPreis = listenpreis * (1 - rabatt / 100)
```

**Beispiel**:
- Basis-Preis: 100€
- Staffelpreis: 95€ (ersetzt Basis-Preis)
- Vertragsrabatt: 5% → Netto: 95€ * 0.95 = 90,25€
- (Kunden-Rabatt wird NICHT zusätzlich angewendet, da Vertragsrabatt höhere Priorität hat)

---

## 7. Gebuchte Lieferscheine (Attestierung)

### 7.1 Wiederaufruf gebuchter LS
- **Typ**: Verknüpft (READ mit Attestierung)
- **Quelle**: `domain_sales.delivery_notes` mit `status = 'posted'`
- **CRUD**: READ (mit Dialog), UPDATE (nur mit Attestierung)
- **Logik**:
  - Wenn LS bereits gebucht: Alle Felder Read-only
  - Änderungen nur mit Attestierungs-Dialog möglich
  - Dialog muss enthalten:
    - **Begründung** (Pflichtfeld)
    - **Änderungstyp** (Korrektur, Stornierung, Nachträgliche Änderung)
    - **Genehmigung** (optional, je nach Rolle)
  - Alle Änderungen werden im Audit-Log gespeichert

### 7.2 Nachträglicher Druck
- **Typ**: Eingabe (mit Dialog)
- **Quelle**: Manuelle Aktion
- **CRUD**: UPDATE (mit Attestierung)
- **Logik**:
  - Dialog: "Begründung für nachträglichen Druck"
  - Wird im Audit-Log gespeichert
  - API: `/api/v1/sales/delivery-notes/{id}/print?attestation={reason}`

### 7.3 Audit-Log
- **Typ**: Automatisch
- **Quelle**: Alle Änderungen an gebuchten LS
- **CRUD**: CREATE (automatisch)
- **Logik**:
  - Tabelle: `domain_audit.audit_log`
  - Felder: `user_id`, `action`, `entity_type`, `entity_id`, `changes`, `reason`, `timestamp`
  - API: `/api/v1/audit/logs?entity_type=delivery_note&entity_id={id}`

---

## 8. Benötigte Datenbank-Verknüpfungen & CRUD

### 8.1 Kunden/Debitoren
- **Tabelle**: `domain_crm.customers`
- **CRUD**: READ (Auswahl), CREATE (wenn neuer Kunde)
- **API-Endpoints**:
  - `GET /api/v1/crm/contacts` - Liste (wie in `CustomerSelectionDialog.tsx` verwendet)
  - `GET /api/v1/crm/contacts/{id}` - Details
  - `POST /api/v1/crm/contacts` - Neuer Kunde
  - `GET /api/v1/crm/business-partners/{id}` - Erweiterte Kunden-Daten (inkl. Rabatte)
  - `GET /api/v1/crm/business-partners/{id}/discount-items` - Rabatte

### 8.2 Artikel
- **Tabelle**: `domain_inventory.articles`
- **CRUD**: READ (Auswahl)
- **API-Endpoints**:
  - `GET /api/v1/articles?search={query}&limit=50` - Suche (tatsächlicher Pfad)
  - `GET /api/v1/articles/search?q={query}&limit=50` - Erweiterte Suche
  - `GET /api/v1/articles/{id}` - Details
  - `GET /api/v1/inventory/stock?article_id={id}` - Lagerbestand (falls vorhanden)

### 8.3 Niederlassungen
- **Tabelle**: `domain_shared.branches` (neu anzulegen) oder `domain_shared.tenants.settings.branches`
- **CRUD**: READ (Auswahl), CREATE/UPDATE (Admin)
- **API-Endpoints**:
  - `GET /api/v1/admin/branches` - Liste
  - `POST /api/v1/admin/branches` - Neue Niederlassung (Admin)
  - `PUT /api/v1/admin/branches/{id}` - Update (Admin)

### 8.4 Vertreter
- **Tabelle**: `domain_crm.customers.vertreter` oder `domain_crm.contacts` (Typ: Sales Rep)
- **CRUD**: READ (wird beim Kundenauswahl geladen)
- **API-Endpoints**:
  - Wird automatisch aus Kunden-Daten geladen

### 8.5 Bediener (User)
- **Tabelle**: `domain_shared.users`
- **CRUD**: READ (aus Session)
- **API-Endpoints**:
  - `GET /api/v1/users/me` - Aktueller User
  - Frontend: `useAuth()` Hook

### 8.6 Preislisten
- **Tabelle**: `domain_pricing.price_lists`
- **CRUD**: READ (Auswahl)
- **API-Endpoints**:
  - `GET /api/v1/pricing/price-lists?article_group={group}&customer_id={id}` - Suche

### 8.7 Rabatte
- **Tabellen**: 
  - `domain_crm.business_partner_pricing_rules`
  - `domain_pricing.discount_rules`
- **CRUD**: READ (Auswahl)
- **API-Endpoints**:
  - `GET /api/v1/pricing/discount-rules?role={role}` - Mitarbeiter-Rabatte
  - `GET /api/v1/crm/customers/{id}/pricing-rules` - Kunden-Rabatte

### 8.8 Verträge
- **Tabelle**: `domain_contracts.contracts`
- **CRUD**: READ (Auswahl)
- **API-Endpoints**:
  - `GET /api/v1/contracts?customer_id={id}&status=active` - Aktive Verträge

### 8.9 Lagerorte
- **Tabellen**: 
  - `domain_inventory.warehouses`
  - `domain_inventory.stock_locations`
- **CRUD**: READ (Auswahl)
- **API-Endpoints**:
  - `GET /api/v1/inventory/warehouses` - Lagerhäuser
  - `GET /api/v1/inventory/locations?warehouse_id={id}` - Lagerplätze

### 8.10 Kostenstellen
- **Tabelle**: `domain_finance.cost_centers` oder `domain_erp.kostenstellen`
- **CRUD**: READ (Auswahl)
- **API-Endpoints**:
  - `GET /api/v1/finance/cost-centers` - Liste

### 8.11 Lieferscheine (Speichern/Buchen)
- **Tabelle**: `domain_sales.delivery_notes` + `domain_sales.delivery_note_positions`
- **CRUD**: CREATE, READ, UPDATE (mit Attestierung)
- **API-Endpoints**:
  - `POST /api/v1/sales/delivery-notes` - Neuer LS (Backend generiert LS-Nr. automatisch)
    - Payload: Header-Daten + `positions: Position[]` Array
    - Backend erstellt Header + Positionen in separaten Tabellen
  - `GET /api/v1/sales/delivery-notes/{id}` - Laden (inkl. Positionen)
  - `PUT /api/v1/sales/delivery-notes/{id}` - Update (mit Attestierung bei gebuchten)
  - `POST /api/v1/sales/delivery-notes/{id}/post` - Buchen
  - `POST /api/v1/sales/delivery-notes/{id}/print?attestation={reason}` - Drucken (mit Attestierung)
  - `POST /api/v1/sales/delivery-notes/{id}/positions` - Position hinzufügen
  - `PATCH /api/v1/sales/delivery-notes/{id}/positions/{pos_id}` - Position aktualisieren
  - `DELETE /api/v1/sales/delivery-notes/{id}/positions/{pos_id}` - Position löschen

---

## 9. Implementierungs-Prioritäten

### Phase 1: Grundfunktionalität (Sofort)
1. ✅ Kundenauswahl (Dialog)
2. ✅ Artikelsuche (Dialog)
3. ✅ Positions-Verwaltung
4. ✅ Basis-Berechnungen (Netto, MWSt, Brutto)
5. ⚠️ Bediener aus Session (noch hardcoded)
6. ⚠️ Vertreter aus Kunden (noch hardcoded)

### Phase 2: Verknüpfungen (Kurzfristig)
1. Bediener aus Session laden
2. Vertreter aus Kunden-Stammdaten
3. Niederlassungen aus Admin-Bereich
4. Preislogik (Basis-Preis aus Artikel)
5. MWSt. aus Artikel-Stammdaten

### Phase 3: Erweiterte Preislogik (Mittelfristig)
1. Staffelpreislisten (Artikelgruppen)
2. Kunden-Rabatte
3. Mitarbeiter-Rolle-Rabatte
4. Vertragsrabatte
5. Preisberechnung mit Priorität

### Phase 4: Attestierung (Mittelfristig)
1. Dialog für Änderungen an gebuchten LS
2. Audit-Log-Integration
3. Begründungs-Pflicht
4. Genehmigungs-Workflow (optional)

---

## 10. Fehlende Datenbank-Tabellen (müssen angelegt werden)

### 10.1 Niederlassungen
```sql
CREATE TABLE domain_shared.branches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES domain_shared.tenants(id),
    branch_number INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    address JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(tenant_id, branch_number)
);
```

### 10.2 Lieferscheine
```sql
CREATE TABLE domain_sales.delivery_notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES domain_shared.tenants(id),
    delivery_note_number VARCHAR(50) UNIQUE NOT NULL,
    customer_id UUID REFERENCES domain_crm.customers(id),
    branch_id UUID REFERENCES domain_shared.branches(id),
    sales_rep_id UUID REFERENCES domain_shared.users(id),
    operator_id UUID REFERENCES domain_shared.users(id),
    delivery_date DATE NOT NULL,
    delivery_time TIME,
    cost_center_id UUID,
    truck_number INTEGER,
    is_credit_note BOOLEAN DEFAULT FALSE,
    is_self_pickup BOOLEAN DEFAULT FALSE,
    is_early_payment BOOLEAN DEFAULT FALSE,
    reference_invoice_number VARCHAR(50),
    status VARCHAR(20) DEFAULT 'draft', -- draft, printed, delivered, invoiced
    is_printed BOOLEAN DEFAULT FALSE,
    is_delivered BOOLEAN DEFAULT FALSE,
    invoice_number VARCHAR(50),
    -- HINWEIS: positions NICHT als JSONB, sondern separate Tabelle (siehe 10.3)
    totals JSONB, -- {netto, mwst, brutto, weight}
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES domain_shared.users(id),
    updated_by UUID REFERENCES domain_shared.users(id)
);
```

### 10.3 Lieferschein-Positionen (Separate Tabelle)
**Wichtig**: Positionen werden **nicht als JSONB** gespeichert, sondern in einer **separaten Tabelle** (wie bei `einkauf_lieferschein_positionen`). Dies ermöglicht:
- Indexierung und Suche
- Referentielle Integrität
- Normale Datenbankabfragen
- Reports und Analysen

```sql
CREATE TABLE domain_sales.delivery_note_positions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    delivery_note_id UUID NOT NULL REFERENCES domain_sales.delivery_notes(id) ON DELETE CASCADE,
    pos_nr INTEGER NOT NULL,
    artikel_id UUID REFERENCES domain_inventory.articles(id),
    artikel_nr VARCHAR(50),
    bezeichnung VARCHAR(255),
    bezeichnung2 VARCHAR(255),
    menge DECIMAL(14, 3) NOT NULL,
    einheit VARCHAR(20),
    listenpreis DECIMAL(14, 4),
    rabatt DECIMAL(5, 2) DEFAULT 0,
    art VARCHAR(50), -- Artikel-Art/Kategorie
    netto_preis DECIMAL(14, 4),
    netto_betrag DECIMAL(14, 2),
    niederlassung INTEGER,
    lagerhalle VARCHAR(80),
    lagerfach VARCHAR(80),
    charge VARCHAR(80),
    serien_nr VARCHAR(80),
    erloskonto VARCHAR(20),
    mwst_prozent DECIMAL(5, 2) DEFAULT 19,
    kontrakt_nr VARCHAR(50),
    skontierf BOOLEAN DEFAULT FALSE,
    fremdware BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT uq_delivery_note_pos_nr UNIQUE (delivery_note_id, pos_nr)
);

CREATE INDEX ix_delivery_note_positions_delivery_note ON domain_sales.delivery_note_positions(delivery_note_id);
CREATE INDEX ix_delivery_note_positions_artikel ON domain_sales.delivery_note_positions(artikel_id);
```

### 10.3 Audit-Log für Attestierung
```sql
CREATE TABLE domain_audit.attestations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES domain_shared.tenants(id),
    entity_type VARCHAR(50) NOT NULL, -- 'delivery_note', 'invoice', etc.
    entity_id UUID NOT NULL,
    action VARCHAR(50) NOT NULL, -- 'print', 'modify', 'cancel'
    reason TEXT NOT NULL,
    changes JSONB, -- Vorher/Nachher-Vergleich
    approved_by UUID REFERENCES domain_shared.users(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    created_by UUID REFERENCES domain_shared.users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## 11. API-Endpoints (zu implementieren)

### 11.1 Niederlassungen
- `GET /api/v1/admin/branches` - Liste aller Niederlassungen
- `POST /api/v1/admin/branches` - Neue Niederlassung (Admin)
- `PUT /api/v1/admin/branches/{id}` - Update (Admin)
- `DELETE /api/v1/admin/branches/{id}` - Löschen (Admin)

### 11.2 Preislogik
- `GET /api/v1/pricing/calculate?article_id={id}&customer_id={id}&quantity={qty}` - Preisberechnung (hierarchische Kaskade)
  - **Wichtig**: Gibt **einen** Listenpreis und **einen** Rabatt zurück (nicht additiv)
  - Priorität: Staffelpreis → Vertragsrabatt → Kunden-Rabatt → Mitarbeiter-Rabatt → Basis-Preis
- `GET /api/v1/pricing/price-lists?article_group={group}&customer_id={id}` - Preislisten
- `GET /api/v1/pricing/discount-rules?role={role}` - Rabatt-Regeln

### 11.3 Attestierung
- `POST /api/v1/sales/delivery-notes/{id}/attest` - Attestierung für Änderung
- `GET /api/v1/audit/attestations?entity_type=delivery_note&entity_id={id}` - Attestierungs-Historie

---

## 12. Frontend-Integration

### 12.1 useAuth Hook erweitern
```typescript
const { user } = useAuth()
// user.username oder user.short_name für Bediener
// user.roles für Rabatt-Berechnung
```

### 12.2 Preisberechnung-Service
```typescript
// services/pricing-service.ts
async function calculatePrice(
  articleId: string,
  customerId: string,
  quantity: number,
  userId: string
): Promise<{
  listPrice: number
  discount: number
  netPrice: number
  source: 'base' | 'price_list' | 'contract' | 'customer_discount'
}>
```

### 12.3 Attestierungs-Dialog
```typescript
// components/sales/AttestationDialog.tsx
- Begründung (Pflichtfeld)
- Änderungstyp (Dropdown)
- Genehmigung (optional)
```

---

## Zusammenfassung

### Eingabedaten (Manuell)
- Liefer-Datum, Uhrzeit
- Kostenstelle, Lkw-Nr.
- Checkboxen (Gutschrift, Selbstabholung, etc.)
- Re.-Nr. (Bezug)
- Menge, Rabatt (kann überschrieben werden)
- Chargen, Serien-Nr.
- Kontrakt-Nr.

### Verknüpfte Daten (Aus DB)
- Liefersch.-Nr. (Backend)
- Niederlassung (Admin)
- Vertreter (Kunden-Stammdaten)
- Bediener (Session)
- Kunde (Dialog)
- Artikel (Dialog)
- Preise (Artikel + Preislogik)
- MWSt. % (Artikel)
- Lagerorte (Artikel/DB)
- Erlöskonto (Artikel/DB)

### Berechnete Daten (Formeln)
- Netto-Preis = `listenpreis * (1 - rabatt / 100)`
- Netto-Betrag = `menge * nettoPreis`
- MWSt. = `nettoBetrag * (mwstProzent / 100)`
- Netto Gesamt = `SUM(nettoBetrag)`
- MWSt. Gesamt = `SUM(MWSt pro Position)`
- Brutto Gesamt = `nettoGesamt + mwstGesamt`
- Gewicht = `SUM(menge * artikel.weight)`

### CRUD-Operationen
- **READ**: Kunden, Artikel, Niederlassungen, Preise, Rabatte, Verträge
- **CREATE**: Lieferschein, Attestierungen
- **UPDATE**: Lieferschein (mit Attestierung bei gebuchten)
- **DELETE**: Nicht vorgesehen (nur Stornierung)

---

## 13. Korrekturen (Review-Update)

Diese Dokumentation wurde basierend auf Codebase-Review korrigiert:

### 13.1 API-Pfade korrigiert
- ✅ `/api/v1/inventory/articles` → `/api/v1/articles` (tatsächlicher Pfad)
- ✅ `/api/v1/crm/contacts` bleibt (wird bereits verwendet)
- ✅ Alternative: `/api/v1/crm/business-partners` für erweiterte Kunden-Daten

### 13.2 Positionen-Struktur korrigiert
- ❌ **Entfernt**: `positions JSONB` in `delivery_notes` Tabelle
- ✅ **Hinzugefügt**: Separate Tabelle `domain_sales.delivery_note_positions`
- ✅ **Begründung**: Wie bei `einkauf_lieferschein_positionen` - ermöglicht Indexierung, Suche, referentielle Integrität

### 13.3 Rabattlogik korrigiert
- ❌ **Entfernt**: Additive Rabatte (`rabatt = vertragsrabatt + kundenrabatt + mitarbeiterrabatt`)
- ✅ **Hinzugefügt**: Hierarchische Kaskade (wie in zvoove/Landhandel)
  - Staffelpreis ersetzt Basis-Preis
  - **EIN** Rabatt wird angewendet (höchste Priorität)
  - Priorität: Vertragsrabatt → Kunden-Rabatt → Mitarbeiter-Rabatt

### 13.4 LS-Nr. Generierung korrigiert
- ❌ **Entfernt**: `/api/v1/numbering/generate?type=delivery_note` (existiert nicht)
- ✅ **Hinzugefügt**: Backend generiert LS-Nr. automatisch beim `POST /api/v1/sales/delivery-notes`

### 13.5 Offene Aufträge/LS-Betrag
- ⚠️ **Hinweis**: API-Endpunkt `/api/v1/sales/customers/{customer_id}/open-amounts` existiert noch nicht
- ✅ **Alternative**: Frontend-seitige Aggregation über bestehende Endpunkte

---

**Stand**: Dokumentation aktualisiert nach Codebase-Review (2025-01-XX)

