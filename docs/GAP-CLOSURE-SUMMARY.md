# GAP-Closure Umsetzungsübersicht — Stand 2026-03-05

**Referenz:** [.cursor/plans/gap-closure_master_plan_ab0cb3b1.plan.md](../.cursor/plans/gap-closure_master_plan_ab0cb3b1.plan.md)

**Maturity-Fortschritt:** 38% → **~88%**

---

## Phasen-Status

| Phase | Inhalt | Status | Report |
|-------|--------|--------|--------|
| **1** | Finance P0 + Procurement P0 + Agrar P0 | ✅ Abgeschlossen | (Phase 1 vor Summary-Erstellung) |
| **2** | Finance P1 + Agrar P1 + CRM P0/P1 | ✅ Abgeschlossen | [PHASE-2-COMPLETION-REPORT.md](PHASE-2-COMPLETION-REPORT.md) |
| **3** | Sales Domain komplett | ✅ Abgeschlossen | [PHASE-3-COMPLETION-REPORT.md](PHASE-3-COMPLETION-REPORT.md) |
| **4** | CRM/Marketing Erweiterung | ✅ Abgeschlossen | [PHASE-4-COMPLETION-REPORT.md](PHASE-4-COMPLETION-REPORT.md) |
| **5** | Finance + Procurement P2/P3 | ✅ Abgeschlossen | [PHASE-5-COMPLETION-REPORT.md](PHASE-5-COMPLETION-REPORT.md) |
| **6** | Agriculture Backend + Erweiterung | ✅ Abgeschlossen | [PHASE-6-COMPLETION-REPORT.md](PHASE-6-COMPLETION-REPORT.md) |

---

## Abgeschlossene Capabilities (Phasen 1–4)

### Finance
- Kontenplan Hierarchie, Belegprinzip, Nummernkreise
- Debitoren-/Kreditorenstamm mit OP-Saldo
- GL-Buchung, OP-Verwaltung, Bankabstimmung, Steuerschlüssel
- Abschlusschecklisten, Nebenbuch-Abstimmung, Standardreports

### CRM/Marketing
- Opportunities, Consent, DSGVO, Segmente (statisch + dynamisch)
- Lead-Routing, CRM-Reports (Pipeline, Win/Loss, Lead-Sources)
- Customer Timeline, Belegkette Opportunity→Quote→Order
- Kampagnen-KPIs

### Sales
- Preislisten-CRUD, Dokumentenfluss (Angebot→Auftrag→LS→Rechnung)
- Gutschriften, Retouren, Sales-Reports
- Top-Kunden/-Artikel, Pipeline-KPIs

### Procurement
- Tabellen für RFQ, Anlieferavis, Auftragsbestätigungen, Warengruppen, Zahlungsläufe

### Agrar (Phase 1+2+6)
- Wasserschutz-Zonen-API, PSM-Compliance, Portal-Orders
- Düngebilanz, Cross-Compliance, Order-Reconciliation
- Feldkalender, Feldblockfinder-Config, QS/LEA-Export, Low-Stock-Warnung

---

## Geänderte Bereiche (Dateien/Module)

| Domain | Wichtige Dateien |
|--------|------------------|
| Finance | `journal_entries.py`, `debtors.py`, `creditors.py`, `numbering_router.py`, `open_items.py`, `bank_reconciliation.py`, `financial_reports.py` |
| CRM | `app/crm/router.py`, `app/crm/schemas.py`, `crm_reports.py`, `app/domains/crm/models.py` |
| Sales | `price_lists.py`, `sales_credit_notes.py`, `sales_reports.py`, `sales_orders.py`, `sales_offers.py`, `sales_delivery_notes.py` |
| Marketing | `marketing.py` |
| Procurement | `einkauf_missing_tables_20260305.py` (Migration) |
| Agrar | `agrar_feldbuch.py`, `portal_shop.py`, `psm.py`, `quality_rules.py` |

---

## Phase 5 — Abgeschlossen (2026-03-05)

- FIBU-GL-04, AR-04, AP-03, AP-04, BNK-03, TAX-02, CLS-01, GL-06: Bereits vorhanden
- FIBU-REP-02: Drilldown-Endpoint ergänzt
- FIBU-CLS-03: Abgrenzungen/Rückstellungen API neu

## Phase 6 — Abgeschlossen (2026-03-05)

- AGR-OPS-04: Feldkalender
- AGR-FLD-03: Feldblockfinder-Config
- AGR-COM-04/05: QS-Export, LEA-Export (Stubs)
- AGR-INV-04: Low-Stock-Warnung (Saatgut, Dünger, PSM)
