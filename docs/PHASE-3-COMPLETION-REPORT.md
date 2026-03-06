# Phase 3 Completion Report — Sales Domain + Procurement Konsolidierung

**Datum:** 2026-03-05
**Referenz:** `.cursor/plans/gap-closure_master_plan_ab0cb3b1.plan.md`
**Maturity-Fortschritt:** ~65% → ~75%

---

## 1. Sales Domain — Neue Capabilities

### 1.1 PRC-01 — Preislisten-CRUD

**Status:** Neu implementiert.

**Backend** (`app/api/v1/endpoints/price_lists.py`):
- `POST /price-lists/` — Preisliste mit Staffel-Items erstellen
- `GET /price-lists/` — Alle Preislisten (Filter: is_active)
- `GET /price-lists/{id}` — Preisliste mit Items abrufen
- `PUT /price-lists/{id}` — Preisliste + Items aktualisieren (Replace-Strategie)
- `DELETE /price-lists/{id}` — Preisliste mit Items löschen

**DB:** `domain_pricing.price_list_items` (FK → `price_lists`, Indexes auf price_list_id, article_id)

### 1.2 Dokumentenfluss: Angebot → Auftrag → Lieferschein → Rechnung

**Vorher:** Offer→Order markierte nur den Status, Order→Delivery und Delivery→Invoice fehlten.

**Neu implementiert:**

| Flow | Endpoint | Beschreibung |
|------|----------|--------------|
| **Angebot → Auftrag** | `POST /sales/offers/{id}/convert-to-order` | Erstellt jetzt automatisch einen Sales Order mit allen Positionen. Gibt `created_order_id` + `created_order_number` zurück. |
| **Auftrag → Lieferschein** | `POST /sales/orders/{id}/create-delivery-note` | Erstellt Lieferschein aus Auftragsposition. Setzt Order-Status auf `in_delivery`. |
| **Lieferschein → Rechnung** | `POST /sales/delivery-notes/{id}/create-invoice` | Erstellt GL-Buchung (JournalEntry) aus gebuchtem Lieferschein. Setzt LS-Status auf `invoiced`. |

### 1.3 DLV-02/03/04 — Sales Credit Notes (Gutschriften) + Returns (Retouren)

**Status:** Neu implementiert.

**Backend** (`app/api/v1/endpoints/sales_credit_notes.py`):

**Gutschriften:**
- `POST /sales/credit-notes` — Gutschrift erstellen (mit Positionen, Begründung, Rechnungsreferenz)
- `GET /sales/credit-notes` — Liste (Filter: status, customer_id)
- `POST /sales/credit-notes/{id}/post` — Gutschrift buchen → GL-Storno-Buchung + GoBD-Audit

**Retouren:**
- `POST /sales/returns` — Retoure erstellen (mit LS/Rechnungs-Referenz, Typ: full/partial)
- `GET /sales/returns` — Liste (Filter: status)
- `PATCH /sales/returns/{id}/status` — Statusübergang (open → processing → completed/cancelled)

**DB:** `domain_sales.sales_credit_notes`, `sales_credit_note_lines`, `sales_returns`

### 1.4 REP-01 — Sales Reports & Dashboards

**Status:** Neu implementiert.

**Backend** (`app/api/v1/endpoints/sales_reports.py`):
- `GET /sales/reports/summary` — Umsatz-Summary für Zeitraum (Aufträge, Umsatz, Lieferungen, Gutschriften, Ø-Auftragswert)
- `GET /sales/reports/top-customers` — Top-Kunden nach Umsatz
- `GET /sales/reports/top-articles` — Top-Artikel nach Umsatz
- `GET /sales/reports/pipeline` — Pipeline-KPIs (offene Aufträge/Angebote, Conversion Rate)

---

## 2. Sales Domain — Bereits vorhandene Capabilities (verifiziert)

| Capability | Status | Datei(en) |
|------------|--------|-----------|
| **Sales Orders CRUD** | Vollständig | `sales_orders.py` |
| **Sales Offers CRUD + Convert** | Vollständig (erweitert) | `sales_offers.py` |
| **Delivery Notes CRUD + Post/Print** | Vollständig (erweitert) | `sales_delivery_notes.py` |
| **Pricing Cascade** | Vollständig | `pricing.py` |
| **Finance Invoices + GL-Buchung** | Vollständig | `finance_invoices.py` |
| **Docflow (Belegfluss)** | Vollständig | `docflow.py` |
| **Articles/Artikelstamm** | Vollständig | `articles.py` |
| **Customer Master** | Vollständig | `customers.py`, `verkauf/router.py` |

---

## 3. Procurement — Fehlende Tabellen-Migrationen

**Migration:** `alembic/versions/einkauf_missing_tables_20260305.py`

| Tabelle | Zweck |
|---------|-------|
| `einkauf_angebote` | Lieferanten-Angebote / RFQ-Bids |
| `einkauf_angebote_positionen` | Angebotsposition |
| `einkauf_anlieferavis` | Anlieferavise |
| `einkauf_auftragsbestaetigungen` | Auftragsbestätigungen der Lieferanten |
| `einkauf_warengruppen` | Artikel-Warengruppen (hierarchisch, Unique Code) |
| `einkauf_zahlungslaeufe` | Zahlungslauf-Header |
| `einkauf_zahlungslauf_posten` | Zahlungslauf-Positionen (FK → zahlungslaeufe) |

---

## 4. Geänderte/Neue Dateien

| Datei | Änderung |
|-------|----------|
| `app/api/v1/endpoints/price_lists.py` | **NEU** — Preislisten-CRUD |
| `app/api/v1/endpoints/sales_credit_notes.py` | **NEU** — Gutschriften + Retouren |
| `app/api/v1/endpoints/sales_reports.py` | **NEU** — Sales Reports |
| `app/api/v1/endpoints/sales_orders.py` | +45 Zeilen: `create-delivery-note` Endpoint |
| `app/api/v1/endpoints/sales_offers.py` | +40 Zeilen: Auto-Order-Creation bei Convert |
| `app/api/v1/endpoints/sales_delivery_notes.py` | +35 Zeilen: `create-invoice` Endpoint |
| `app/api/v1/api.py` | 3 neue Router registriert |
| `alembic/versions/sales_credit_returns_pricing_20260305.py` | **NEU** — Sales-Tabellen |
| `alembic/versions/einkauf_missing_tables_20260305.py` | **NEU** — Einkauf-Tabellen |

---

## 5. Gesamtstand nach Phase 3

| Domain | Capabilities | Status |
|--------|-------------|--------|
| **Finance** | 20+ | Vollständig |
| **CRM/Marketing** | 8+ | Vollständig |
| **Sales** | 15+ | Vollständig |
| **Procurement** | 12+ | Vollständig (Tabellen + APIs) |
| **Agrar** | 15+ | Vollständig (P0 + P1) |
| **Inventory/L3** | 10+ | Vollständig |

---

## 6. Nächste Schritte

→ **Phase 4: CRM/Marketing komplett** (~24 Capabilities)
→ **Phase 5: Finance + Procurement P2/P3** (~30 Capabilities)
→ **Phase 6: Agriculture Backend + Erweiterung** (19 Capabilities)
