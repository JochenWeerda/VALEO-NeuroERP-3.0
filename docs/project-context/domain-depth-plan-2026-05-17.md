# Domain-Tiefe: Ist-Soll-Vergleich und Umsetzungsplan

**Erstellt:** 2026-05-17
**Massstab:** Marktführende ERP-Systeme, etablierte ERP-Plattformen, Odoo 17 Enterprise
**Zielmarkt:** Agrarhandel / Landhandel / Genossenschaften

> Dieses Dokument ist die **operative Source-of-Truth** fuer alle Ausbauvorhaben
> zur fachlichen Vertiefung der Domains. Es ersetzt keine Wave-STATUS.md,
> sondern fuehrt den Auftrag und den Fortschritt auf Domain-Ebene.

## Aktualisierung 2026-05-17: Repo-seitige Closure-Welle

Die grossen fachlichen Luecken aus dem Vergleich gegen marktführende ERP-Systeme, Odoo und Branchenspezifische Agrarsoftware sind repo-seitig in einer ersten Closure-Welle adressiert. Der Stand ersetzt nicht externe UAT-, Steuerberater-, TSE-, DMS- oder Rechtsfreigaben.

| Domain | Geschlossene Repo-Lieferung | Nachweis |
|--------|-----------------------------|----------|
| Verkauf | Rahmenauftraege/Abrufe, Kreditlimit, Sammelbelege | `sales_blanket_orders.py`, `credit_management.py`, `collective_documents.py` |
| Einkauf | 3-Wege-Match, ERS, RFQ, Einkaufs-KPIs | `purchase_invoice_verification.py`, `ers_settlement.py`, `rfq.py`, `einkauf_kpis.py` |
| Finance | Anlagenbuchhaltung, Budgetierung, Liquiditaetsplanung | `asset_accounting.py`, `budget_planning.py`, `liquidity_planning.py` |
| CRM | Pipeline, Forecast, 360-Grad-Sicht, Account-Hierarchie, SLA | `opportunities.py`, `crm_360.py`, `crm_account_hierarchy.py`, `cases.py` |
| Logistik | Tourenplanung, Frachtkosten, Track & Trace, ePOD, Statistik | `logistics_tours.py`, `logistics_freight.py` |
| HRM | Organigramm, Arbeitszeitkonto, Bewerberpipeline | `personal.py` |
| Compliance | DSGVO-Loeschantrag, Whistleblower, LkSG-Risikobewertung | `compliance_dsgvo.py`, `compliance_whistleblower_lksg.py` |
| Futtermittel | Rohwaren, Rezepturen, Naehrstoffanalyse, Deklaration, Etikett | `futtermittel_rohwaren.py`, `futtermittel_rezepte.py` |
| POS | Split-Payment- und Promotions-Preview | `pos_payments_promotions.py` |
| Kontrakte | Zentrale Contract Engine mit Versionen, Obligations und Renewals | `central_contracts.py` |

Fokussierter Teststand: 70 Tests gruen fuer CRM, Einkauf, Finance, Logistik, Router-Registrierung, HRM, Compliance/POS und bestehende Settlement-/DQ-Regressionspfade.

---

## Aktualisierung 2026-06-26: Konsolidierungsstand

Verbindliche offene Punkte liegen in `docs/project-context/open-gaps-and-known-issues.md`.
Dieser Plan ist **historischer Soll-Katalog**; der aktuelle Lieferstand steht in den Aktualisierungsblöcken.

| Domain | Repo-Resttiefe (echte Lücken, nicht extern blockiert) |
|---|---|
| Lager/WMS | FEFO-Pick-Listen, Bestandsbewertung FIFO/Durchschnitt, Permanente Inventur, Multi-Lager-Konsolidierung |
| Futtermittel | HACCP-Grundstruktur, VLOG-Meldung, QS-Leitfaden vollständig |
| CRM | RAG-/Intent-Panel im Kunden-Stamm, Legacy-API-Pfade `/api/crm/` |
| Finance | Finanz-Abschluss-Stubs (calculate/lock/run); ELSTER vollständig (ERiC extern) |
| Logistik | CMR-Frachtbrief-Druck vollständig; `/api/v1/logistik/frachtbriefe` **geschlossen 2026-06-26** (LOG-FRACHTBRIEF-001: `domain_logistics.frachtbriefe` Alembic + GET/POST/PATCH + Tests); Track & Trace / ePOD noch offen |
| WF-Cockpit | Persistente Cockpit-Tabellen, Outbox-/NATS-Projektor, UI-Leitstand, Dead-Letter-Sicht |
| Agrar/Silo | Zielzellen-Regelengine (automatischer Vorschlag aus WE/Waage) |

Extern blockiert (nicht repo-seitig schliessbar): DATEV-Steuerberater-Cutover, DMS-Live-Probe,
TSE-/DSFinV-K-Pruefwerkzeug, ATLAS-Zertifikat, ERiC-Zertifikat, UAT-Unterschriften.

---

## Aktualisierung 2026-06-12: Welle „Physische Kette” — Task 0 + Logistik-Audit

- **Playwright @smoke / Dev:** SSO-only-Login ersetzt durch Dev-`localStorage`-Session und
  `X-Tenant-ID`-Default auf Dev-Tenant-UUID (`playwright-tests/helpers/api.ts`,
  `playwright-tests/fixtures/testSetup.ts`). Doku: `docs/quality-assurance/playwright-smoke-auth.md`.
- **Logistik Tiefen-Audit:** Ist-Inventar, Bruchstellen, empfohlene Slice-Reihenfolge
  (`docs/workflows/wave-physical-chain-logistics-audit-2026-06-12.md`).
- **LOG-PROD-001 (2026-06-12):** Alembic `log_logistics_core_20260612` für
  `domain_logistics` (Touren, Stopps, Events, Frachttarife); Runtime-DDL in
  `logistics_tours.py` / `logistics_freight.py` entfernt; Integrationstests
  `tests/test_logistics_integration.py`. Nächster Schritt laut Audit: **LOG-SPINE-001**.

---

## Aktualisierung 2026-05-18: Einordnung der urspruenglichen Gap-Zusammenfassung

Die urspruengliche Management-Zusammenfassung mit den Klassen `Vollstaendig`, `Teilweise` und `Basis` sowie dem 3-Phasen-Plan ueber ca. 183 Entwicklungstage ist als **Ausgangsbefund vom 2026-05-17** zu lesen. Sie beschreibt die damals identifizierte Ziel-Luecke gegen marktfuehrende ERP-Systeme, nicht mehr den aktuellen offenen Repo-Backlog.

Aktueller repo-seitiger Stand nach den Closure-Wellen:

| Kategorie | Domains | Aktueller Repo-Stand | Verbleibende Grenze |
|-----------|---------|----------------------|---------------------|
| Repo-seitig breit geschlossen | Verkauf, Einkauf, Finance, CRM, Logistik, HRM, Compliance, POS, Kontrakte | Zentrale API-Vertraege, Router-Registrierungen und fokussierte Tests vorhanden | Externe UAT-, Provider-, Rechts-, Steuerberater- und Betriebsfreigaben |
| Weiter auszubauen | Lager/WMS, Futtermittel, Agrar-Feinschliff | Basis- und Vertiefungspfade vorhanden; weitere Prozess- und Integrationshaerte sinnvoll | FEFO/FIFO-Tiefe, Bestandsbewertung, Produktions-/QS-Tiefe, GS1/SSCC und operative UATs |
| Extern blockiert | DATEV/ELSTER/ERiC, TSE/DSFinV-K, DMS-Live, E-Signatur, Shop-/Webhook-Provider | Repo-Vertraege und Stub-/Readiness-Pfade vorhanden oder vorbereitet | Produktive Credentials, Provider-Signaturen, Abnahmeprotokolle und echte Schnittstellentests |

Damit gilt: Die Detailabschnitte 1 bis 15 bleiben als **historischer Soll-Katalog und Resttiefe-Backlog** nuetzlich. Fuer den verbindlichen Lieferstand gelten jedoch `docs/architecture/process-kernel/STATUS.md`, diese Aktualisierungsbloecke und `docs/project-context/open-gaps-and-known-issues.md`.

---

## Aktualisierung 2026-05-18: Phase-2/3-Gap-Closure

Phase 2 und Phase 3 sind repo-seitig als Code-/Vertragsgaps geschlossen. Der urspruengliche 118-Tage-Rest aus CRM, Finance, HRM, Verkauf, Agrar, Compliance, Futtermittel, Einkauf und POS ist damit nicht mehr als offener Implementierungsrueckstand zu fuehren.

| Phase | Urspruengliche Domains | Repo-seitiger Closure-Nachweis | Externe oder fachliche Restgrenze |
|-------|------------------------|--------------------------------|-----------------------------------|
| Phase 2 | CRM, Finance, HRM, Verkauf | CRM-360, Account-Hierarchie, Pipeline, Asset Accounting, Budget, Liquiditaet, HRM-Operating-System, Arbeitszeitkonto, Recruiting/Org, Sales-Rahmenauftraege und Kredit-/Sammelbelegpfade sind registriert und getestet | DATEV-/Payroll-Cutover, Steuerberaterfreigabe, echte Office-/SSO-/DMS-Zugangsdaten |
| Phase 3 | Agrar, Compliance, Futtermittel, Einkauf, POS | eBilanz/ELSTER-Readiness, ATLAS, Saatzucht, Futtermittel-Rohwaren/Rezeptur/Naehrstoffanalyse/Deklaration/Etikett, DSGVO/Whistleblower/LkSG, ERS/RFQ/3-Wege-Match, POS-Split-Payment/Promotions und DSFinV-K-v2.3-ZIP sind repo-seitig abgesichert | ERiC-Zertifikat, ATLAS-Zertifikat, TSE-/DSFinV-K-Pruefwerkzeug, Rechts-/Steuerberaterabnahmen, echte UAT-Daten |
| Querschnitt | GS1/SSCC, Webshop, DMS | GS1-Parser liefert SSCC/GTIN/Charge/MHD/Gewicht; Webshop-B2B-Sync ist idempotent mit Blocker-Sicht; DMS-Redirect-/Upload- und Auditpfade sind in Finance/HRM/Process-Kernel-Tests abgedeckt | Produktive Provider-Signaturen, DMS-Live-Probe, Shop-Credentials und Betriebsfreigaben |

Fokussierte Nachweise:

- `tests/test_phase23_gap_closure_api.py`
- `tests/test_gs1_webhook_ruestliste.py`
- `tests/test_sammelabrechnung_interessent_waagen_vorlage.py`
- `tests/test_webshop_atlas_saatzucht_uat.py`
- `tests/test_compliance_pos_gap_extensions.py`
- `tests/test_futtermittel_complete.py`
- `tests/test_major_domain_router_registration.py`

---

## 0. Gesamtbild

| Domain | Ist-Stufe | Soll-Stufe | Gap | Prioritaet |
|--------|-----------|------------|-----|-----------|
| Verkauf (SD) | Stufe 3 | Stufe 5 | Mittel | P2 |
| Einkauf (MM) | Stufe 3 | Stufe 5 | Mittel | P2 |
| Lager/WMS (WM/EWM) | Stufe 2 | Stufe 5 | **Gross** | **P1** |
| Agrar (Ernte/Settlement) | Stufe 4 | Stufe 5 | Klein | P3 |
| FIBU/Finance (FI/CO) | Stufe 3 | Stufe 5 | Mittel | P2 |
| CRM | Stufe 2 | Stufe 5 | **Gross** | **P1** |
| Logistik (TM) | Stufe 1 | Stufe 4 | **Sehr gross** | **P1** |
| Compliance | Stufe 4 | Stufe 5 | Klein | P3 |
| HRM/Personal (HCM) | Stufe 2 | Stufe 5 | **Gross** | P2 |
| Futtermittel | Stufe 1 | Stufe 4 | **Gross** | **P1** |
| POS | Stufe 2 | Stufe 4 | Mittel | P2 |
| Kontrakte | Stufe 2 | Stufe 5 | **Gross** | **P1** |

**Stufendefinition:** 1 = Datenmodell/Grundstruktur, 2 = Basis-CRUD, 3 = Workflow/Prozesse, 4 = Fachtiefe/Auswertungen, 5 = Enterprise-Reife (ERP-vergleichbar)

---

## 1. VERKAUF (SD — Sales & Distribution)

### Ist-Stand
- Order-to-Cash-Prozess vollstaendig: Angebot → Auftrag → Lieferschein → Rechnung → Gutschrift → Retoure
- Reporting: Top-Kunden, Top-Artikel, Monatsumsatz, Pipeline
- Customer-Service-Layer vorhanden

### Soll (Marktführende ERP-Systeme: Order Management)
| Funktion | Ist | Gap |
|----------|-----|-----|
| Angebote mit Gueltigkeitsfrist | ✅ | — |
| Rahmenauftraege / Abrufe | ❌ | Offen |
| Intercompany-Verkauf | ❌ | Offen |
| Konditionstechnik (Preisfindung mehrstufig) | Teilweise | Preis-Engine vertiefen |
| Rebattes / Bonusvereinbarungen | ❌ | Offen |
| Erlösrealisierung (IFRS 15 / ASC 606) | ❌ | Offen |
| Kreditlimitpruefung (dynamisch) | ❌ | Offen |
| Seriennummernverfolgung in Lieferschein | ❌ | Offen |
| Chargen-Rueckverfolgung Verkauf | Teilweise | Vollstaendig |
| Frachtkostenermittlung (Frachtkonditionen) | ❌ | Offen |
| Kundenspezifische Preislisten (Vertragspreise) | Teilweise | Vertiefen |
| EDI-Auftragseingang (ORDERS D97A) | Teilweise | Vollstaendig |
| Versandavis (DESADV) an Kunden | ❌ | Offen |
| Sammellieferschein / Sammelrechnung | ❌ | Offen |
| Auftragsbewertung (Deckungsbeitrag je Auftrag) | ❌ | Offen |

### Umsetzungsschritte (Prio-Reihenfolge)
1. **Rahmenauftraege + Abrufe** — `sales_blanket_orders.py`, Alembic-Migration `sales_blanket_orders_*`, Frontend `verkauf/rahmenauftraege.tsx`
2. **Kreditlimitpruefung** — Integration in `create_order`-Flow; Feld `credit_limit` auf Kundenstamm; Block/Warn-Logik
3. **Konditionstechnik vertiefen** — Kundengruppen-Preise, Mengenstaffeln, Zeitfenster-Rabatte in `PricingService`
4. **Rebattes/Bonusvereinbarungen** — `sales_rebate_agreements.py`, Abrechnungslogik am Periodenende
5. **Sammellieferschein/Sammelrechnung** — `POST /sales/collective-invoice` mit n:m zu Lieferscheinen
6. **Frachtkostenermittlung** — Frachtkonditionen-Tabelle, Integration in Lieferschein-Posting
7. **Erlösrealisierung** — Performance-Obligation-Tracking, Umsatzabgrenzung

**Geschaetzte Aufwand:** ~15 Entwicklungstage

---

## 2. EINKAUF (MM — Materials Management Procurement)

### Ist-Stand
- Bestellvorschlaege (Lager/Verkauf/Rohware), Lieferanten, Kontrakte, Frachtauftraege
- EDI-Versand (EDIFACT ORDERS D97A), E-Mail, Fax
- 50+ Endpoints, sehr detailliertes Frontend

### Soll (Marktführende ERP-Systeme: Purchasing)
| Funktion | Ist | Gap |
|----------|-----|-----|
| Bestellungen mit Freigabestrategien (Mehrstufig) | Teilweise | Genehmigungsworkflow ausbauen |
| Rahmenvertraege (Kontraktabrufe) | Teilweise | Vertiefung noetig |
| Evaluated Receipt Settlement (ERS) | ❌ | Offen |
| Dienstleistungseinkauf (Service Entry Sheet) | Teilweise | Vertiefen |
| Lieferantenbewertung (automatisch, mehrdimensional) | Teilweise | Scores automatisieren |
| Wareneingangs-Qualitaetspruefung | Teilweise | QM-Anbindung |
| Rechnungspruefung (3-Wege-Match: PO/GR/IR) | ❌ | **Wichtig** |
| Konsignationslager | ❌ | Offen |
| Unterauftragnehmer-Abwicklung (Subcontracting) | ❌ | Offen |
| Einkaufsstatistik / ABC-Analyse Lieferanten | ❌ | Offen |
| Lieferantenportal (Self-Service Auftragsbestaetigung) | Teilweise | Ausbauen |
| Spot-Einkauf / Rfq-Prozess | ❌ | Offen |
| Einkaufsabteilungs-KPIs (On-Time, Fill-Rate) | ❌ | Offen |

### Umsetzungsschritte
1. **3-Wege-Match** (PO/GR/IR) — `purchase_invoice_verification.py`; Toleranzgruppen; automatische Buchungsvorschlagserzeugung
2. **Mehrstufige Freigabe** — `ApprovalWorkflow` fuer Bestellungen; Schwellwert-basierte Routing-Regeln
3. **ERS (Evaluated Receipt Settlement)** — automatische Rechnungserzeugung bei Wareneingang fuer qualifizierte Lieferanten
4. **Einkaufs-KPIs** — `GET /einkauf/kpis` (On-Time-Delivery, Fill-Rate, Price-Variance, Lead-Time)
5. **RFQ-Prozess** — Anfragen an mehrere Lieferanten, Preisvergleich, Zuschlag
6. **ABC-Analyse** — automatische Lieferanten-Klassifizierung nach Spend-Volumen

**Geschaetzter Aufwand:** ~12 Entwicklungstage

---

## 3. LAGER / WMS (WM/EWM — Warehouse Management) — PRIORITAET P1

### Ist-Stand
- Inventur (Periodenabschluss, Linien)
- Bestandskorrektionen (Schwund, MHD-Abschreibung)
- Basis-Lagerbewegungen

### Soll (Marktführende ERP-Systeme: Warehouse Management)
| Funktion | Ist | Gap |
|----------|-----|-----|
| Lagerstruktur (Lager/Zone/Gang/Fach) | Teilweise | Gang-Ebene + Zuordnung Fach→Gang (**WM-STRUCT-001**); Lese-UI auf Lagerplätze; Kapazität/Sequenz/RF weiterhin Lücken |
| Einlagerungs-/Auslagerungsstrategien | ❌ | **Kritisch** |
| Transferauftraege (Umlagerung intern) | ❌ | Wichtig |
| FEFO/FIFO-Steuerung | ❌ | **Kritisch** fuer Agrar |
| Chargen-Management vollstaendig | Teilweise | Vertiefen |
| MHD-Verwaltung mit Ampelfunktion | Teilweise | Ausbauen |
| Pick-Liste (kommissionieren) | ❌ | Wichtig |
| Packliste / Versandvorbereitung | ❌ | Wichtig |
| Silo-Management (Schuettgut) | Teilweise | **WM-AGRI-SILO-001** — `silo_systems` / `silo_cells` / `material_flow_nodes|edges` in `domain_inventory`, API `/lager/wms/agri`, Route-Validierung; Bird-View (**WM-AGRI-MAP-001**), PLC (**WM-AGRI-PLC-005**) folgen |
| Gefahrstoff-Lager (TRGS 510) | ❌ | Compliance-relevant |
| Lagerplatzbelegung / Kapazitaet | Teilweise | `capacity_kg` + Summenprüfung bei Buchung (**WM-WMS-BIN-001**); Belegungs-Visualisierung/Optimierung offen |
| RF-/Barcode-Unterstuetzung (Schnittstelle) | ❌ | Wichtig |
| Jahresinventur (Stichtagsinventur) | Teilweise | Vollstaendig |
| Permanente Inventur | ❌ | Wichtig |
| Bestandsbewertung (FIFO/Durchschnitt) | ❌ | **Kritisch** |
| Lagerauswertungen (Umschlag, Reichweite, ABC) | Teilweise | Ausbauen |
| Multi-Lager-Konsolidierung | ❌ | Wichtig |

### Umsetzungsschritte
1. **Lagerstruktur-Datenmodell** — Tabellen `warehouses`, `warehouse_zones`, `warehouse_bins` (bestehend); **`warehouse_aisles`** + optional **`warehouse_bins.aisle_id`** (Alembic `wms_warehouse_aisles_20260612`, Slice **WM-STRUCT-001**); Service/API unter `/lager/wms` (`WarehouseService`). *(Benennung „WarehousingService“ im Plan = fachliche Rolle; Implementierung: `warehouse_service`.)*
2. **Bin-Location-Management** — `GET/POST /lager/wms/bins`, `GET/PATCH /lager/wms/bins/{id}`, `PATCH /lager/wms/bins/{id}/stock-lines/{line_id}` (**WM-WMS-BIN-001**); Kapazitätsprüfung bei Buchungen und Zeilenkorrektur; Demo-Seed `scripts/seed_demo_wms_structure.py`
3. **FEFO-Steuerung** — Charge-Attribut `best_before_date`; `pick_fefo()` in `InventoryService`; automatische Empfehlung in Pick-Listen
4. **Einlagerungs-/Auslagerungsstrategien** — konfigurierbare Regeln (FEFO, FIFO, fester Platz, near-item, Kapazitaet) in `PutawayStrategy` + `PickStrategy`
5. **Pick-Listen** — `POST /lager/pick-lists` aus Lieferschein; Optimierung nach Lagerplatz-Sequenz
6. **Transferauftraege** — `POST /lager/transfer-orders` (Bin-to-Bin, Zone-to-Zone)
7. **Bestandsbewertung** — FIFO-/Durchschnitts-Kostenberechnung auf Buchungsebene; `GET /lager/stock-valuation`
8. **Silo-Management vertiefen** — Fuellstand, Qualitaetsparameter pro Silo, Siloprotokoll-Export; Datenbasis **WM-AGRI-SILO-001** (Alembic `agri_silo_material_flow_20260612`) + UI `/lager/materialfluss`
9. **MHD-Ampel** — Dashboard-Widget `GET /lager/mhd-alert` (rot/gelb/gruen nach Verfalldatum-Abstand)
10. **Permanente Inventur** — rollende Inventur je Lagerbereich ohne Betriebsunterbrechung

**Geschaetzter Aufwand:** ~25 Entwicklungstage

---

## 4. AGRAR (Ernteannahme, Kontrakte, Settlement)

### Ist-Stand
- Sehr umfassend: Kontrakte, Ernteannahme, Trocknungsregeln, Settlement mit Freigabe/FIBU-Posting
- Feldbuch, Cross-Compliance, DueV, FLIK, Maschinen, Wetter
- 60+ Endpoints — staerkste Domain im Repo

### Soll (Agrar-Spezialsoftware / Odoo Agriculture / eigene Landhandel-Anforderungen)
| Funktion | Ist | Gap |
|----------|-----|-----|
| Mehrstufige Trocknungsabrechnung | ✅ | — |
| Preisfindung Spot/Termin/Basis | Teilweise | PTBF vertiefen |
| Preissicherungsgeschaefte (Hedging) | Teilweise | Ausbauen |
| Kontraktmonitoring (Abruf-Fortschritt) | ✅ | — |
| Qualitaets-Lot-Management | Teilweise | GS1-128 Codes |
| Ernte-Kampagnenplanung | Teilweise | Kapazitaetsplanung |
| Zertifikat-Verwaltung (QS, Bio, IP-Suisse) | Teilweise | Vollstaendig |
| GVO-Trennhaltung (Identitaetssicherung) | Teilweise | Ausbauen |
| Satellitendaten (NDVI, Ertragserwartung) | ❌ | Optional/Langfristig |
| Selbstanlieferungs-Portal (Landwirt) | Teilweise | Ausbauen |
| Duengebilanz Digital (DueV §10) | Teilweise | Vollstaendig |

### Umsetzungsschritte
1. **PTBF-Preisfindung vertiefen** — Basis-Kontrakt, Preisfixierungsprotokoll, Marktpreisanbindung
2. **GVO-Trennhaltung** — Identitaetssicherungs-Protokoll, Silo-Zuweisung nach GVO-Status, Kontaminationsrisiko-Check
3. **Zertifikat-Verwaltung** — `certificates` Tabelle (QS, Bio, IP-Suisse, Rainforest), Gueltigkeit, Upload, Verknuepfung zu Charge
4. **Duengebilanz vollstaendig** — Berechnung nach DueV §10 mit Nachweis-PDF, elektronische Meldung

**Geschaetzter Aufwand:** ~8 Entwicklungstage

---

## 5. FIBU / FINANCE (FI/CO — Financial Accounting & Controlling)

### Ist-Stand
- VAT Multi-Regime (Inland, Agrar §24, EU, Export)
- Bank-Reconciliation, Direct-Debit, Mahnwesen, Cash-Closing, Journal
- Kostenstellenrechnung, Controlling-KPIs

### Soll (Marktführende ERP-Systeme: Financials)
| Funktion | Ist | Gap |
|----------|-----|-----|
| Anlagenbuchhaltung (AfA, Anlagespiegel) | ❌ | **Wichtig** |
| Jahresabschluss-Assistent | ❌ | Wichtig |
| Ergebnisrechnung (CO-PA) | Teilweise | Ausbauen |
| Profit-Center-Rechnung | Teilweise | Vollstaendig |
| Innenauftraege (Kostentraeger) | ❌ | Wichtig |
| Prozesskostenrechnung | ❌ | Mittel |
| Budgetierung / Forecast | ❌ | Wichtig |
| Konzernkonsolidierung | ❌ | Langfristig |
| Elster-Schnittstelle (UStVA elektronisch) | Teilweise | Vollstaendig |
| GoBD-Archivierung (unveraenderlich) | Teilweise | Ausbauen |
| DATEV-Export (vollstaendig) | Teilweise | Vollstaendig |
| Zahlungsspiegelrechnung | ❌ | Wichtig |
| Liquiditaetsplanung | ❌ | Wichtig |
| FX-Bewertung (Fremdwaehrungs-Neubewertung) | Teilweise | Vollstaendig |

### Umsetzungsschritte
1. **Anlagenbuchhaltung** — Migration `asset_accounting_*`; Modell: `FixedAsset`, `AssetDepreciation`; AfA-Laeufe; Anlagespiegel-Report; `GET /finance/asset-accounting/*`
2. **Budgetierung/Forecast** — `budget_plans` Tabelle; Soll/Ist-Vergleich je Kostenstelle/Periode; `GET /finance/budget-vs-actual`
3. **Liquiditaetsplanung** — Zahlungsein-/-ausgangs-Vorschau aus offenen Posten + Kontrakten; 13-Wochen-Rolling-Forecast
4. **CO-PA vertiefen** — Ergebnisrechnung je Kunde/Produkt/Region; Deckungsbeitrags-Hierarchie
5. **Profit-Center vollstaendig** — Profit-Center-Zuordnung auf allen Belegen; PC-Saldo-Auswertung
6. **DATEV-Export vollstaendig** — DATEV-Format EXTF-Buchungen komplett; Debitorenstamm + Kreditorenstamm-Export
7. **Elster vollstaendig** — UStVA XML-Erzeugung; Voranmeldung + Jahreserklarung; ERiC-Integration (Schnittstellen-Spec)

**Geschaetzter Aufwand:** ~20 Entwicklungstage

---

## 6. CRM (Customer Relationship Management) — PRIORITAET P1

### Ist-Stand
- Kundenstamm, Leads, Aktivitaeten, Basis-Reports
- 7 API-Endpoints, 33 Frontend-Seiten (Frontend bereits sehr detailliert)

### Soll (Etablierte CRM-Systeme / Odoo CRM)
| Funktion | Ist | Gap |
|----------|-----|-----|
| Opportunity-Management (Stufen/Pipeline) | Teilweise | Vollstaendig |
| Sales-Pipeline-Visualisierung (Kanban) | ❌ | **Kritisch** |
| Sales-Forecast (Umsatzprognose) | Teilweise | Vollstaendig |
| Territory-Management | ❌ | Wichtig |
| Account-Hierarchien (Konzernstruktur) | ❌ | Wichtig |
| Aktivitaeten-Planung mit Kalender-Sync | Teilweise | Ausbauen |
| E-Mail-Integration (Korrespondenz-Tracking) | ❌ | Wichtig |
| Marketing-Kampagnen | ❌ | Mittel |
| Service-Cases / Tickets | Teilweise | Vollstaendig |
| SLA-Verwaltung (Reaktionszeiten) | ❌ | Wichtig |
| 360°-Kundensicht (alle Belege je Kunde) | Teilweise | Vollstaendig |
| Kundensegmentierung (RFM, ABC) | Teilweise | Ausbauen |
| Duplikat-Erkennung (Stammdaten) | ❌ | Wichtig |
| DSGVO-Loeschkonzept | Teilweise | Vollstaendig |
| Bewertungsmodul (Net Promoter Score) | ❌ | Optional |

### Umsetzungsschritte
1. **Opportunity-Pipeline vollstaendig** — `opportunities` Tabelle mit Stage, Probability, Expected-Close, Amount; `GET/POST/PATCH /crm/opportunities`; KanbanView-Endpoint `GET /crm/pipeline`
2. **360°-Kundensicht** — `GET /crm/customers/{id}/360` aggregiert: Auftraege, Rechnungen, Zahlungen, Kontrakte, Aktivitaeten, offene Reklamationen, letzte Lieferung
3. **Service-Cases vollstaendig** — `cases` Tabelle; SLA-Tracking; Eskalationsregeln; `GET/POST /crm/cases`; Integration in Auftrags-Workflow
4. **E-Mail-Integration** — Outbound via SMTP (bereits vorhanden); Inbound-Parsing via IMAP/Webhook; automatische Zuordnung zu Kunde/Opportunity
5. **Account-Hierarchien** — `parent_id` auf `business_partners`; Konzern-Rollup in Auswertungen
6. **Territory-Management** — PLZ/Region-Zuordnung zu Aussendienstmitarbeiter; automatische Leads-Zuweisung
7. **Duplikat-Erkennung** — Fuzzy-Match auf Name + PLZ + Ort bei Neuanlage; Merge-Workflow

**Geschaetzter Aufwand:** ~18 Entwicklungstage

---

## 7. LOGISTIK (TM — Transportation Management) — PRIORITAET P1

### Ist-Stand
- Frachtauftraege unter Einkauf; Verladungs-Seiten; Tourenplanung rudimentaer
- Nur 2 dedizierte Logistik-Seiten

### Soll (Marktführende ERP-Systeme: Transportation Management)
| Funktion | Ist | Gap |
|----------|-----|-----|
| Tourenplanung (Route Optimization) | ❌ | **Kritisch** |
| Kapazitaetsplanung (Fahrzeuge/Fahrer) | Teilweise | Vollstaendig |
| Frachtauftrag-Verwaltung | Teilweise | Vertiefen |
| Carrier-Management (Spediteure) | Teilweise | Ausbauen |
| Frachtkostenberechnung | ❌ | **Kritisch** |
| Proof of Delivery (ePOD) | ❌ | Wichtig |
| Track & Trace (Sendungsverfolgung) | ❌ | Wichtig |
| Wiegeschein-Integration | Teilweise | Vollstaendig |
| Gefahrgut-Dokumentation (ADR) | ❌ | Compliance |
| Laderaum-Optimierung | ❌ | Wichtig |
| Lieferanten-Transportfreigabe | ❌ | Wichtig |
| Frachtbrief-Druck (CMR) | Teilweise | Vollstaendig |
| Hafenlogistik / Seefracht | ❌ | Optional |
| Transportstatistik | ❌ | Wichtig |

### Umsetzungsschritte
1. **Tourenplanung-Engine** — `tours` Tabelle (Fahrzeug, Fahrer, Datum, Stopps); `POST /logistik/tours`; Stopps mit Reihenfolge + Zeitfenster; einfache TSP-Optimierung (nearest-neighbor)
2. **Frachtkostenberechnung** — Tarifsystem (Entfernung + Gewicht + Zone); `GET /logistik/freight-cost` mit Simulationsmode
3. **Track & Trace** — `tour_events` Tabelle (GPS-Koordinate, Status, Timestamp); `POST /logistik/tours/{id}/events`; Live-Status-Endpoint
4. **ePOD (Proof of Delivery)** — Empfaenger-Unterschrift (Base64-Bild oder PDF); Zeitstempel; Verknuepfung zu Lieferschein
5. **Carrier-Management** — Spediteur-Stamm, Rahmenvertraege, Bewertung (Puenktlichkeit, Schadenquote)
6. **CMR-Frachtbrief vollstaendig** — PDF-Erzeugung nach CMR-Standard; automatische Befuellung aus Tour/Lieferschein
7. **Transportstatistik** — KPIs: Auslastung, Kosten/tkm, Puenktlichkeitsquote, Reklamationsrate

**Geschaetzter Aufwand:** ~22 Entwicklungstage

---

## 8. COMPLIANCE

### Ist-Stand
- Sehr umfassend: GVO, Sachkunde, EUDR, BVL, QS, VVVO, Intrastat, Cross-Compliance
- Produktions-Ready fuer Agrar-Compliance

### Soll-Erweiterungen
| Funktion | Ist | Gap |
|----------|-----|-----|
| GoBD-Archivierung vollstaendig | Teilweise | Ausbauen |
| DSGVO-Auskunft / Loeschantrag | Teilweise | Vollstaendig |
| Whistleblower-Hinweissystem | ❌ | EU-Pflicht ab 50 MA |
| Lieferkettensorgfaltspflichtengesetz (LkSG) | Teilweise | Vollstaendig |
| ISO 9001 / IFS Food-Auditpfad | Teilweise | Ausbauen |
| Risikobeurteilung (HACCP) | ❌ | Fuer Futtermittel relevant |

### Umsetzungsschritte
1. **DSGVO-Loeschkonzept vollstaendig** — `data_erasure_requests` Tabelle; Loeschprotokoll; `POST /compliance/dsgvo/erasure-request`
2. **Whistleblower-System** — anonymes Hinweisformular; verschluesselter Speicher; `POST /compliance/whistleblower/reports`
3. **LkSG vollstaendig** — Sorgfaltspflichten-Checkliste je Lieferant; Risikobewertung; Jahresbericht
4. **HACCP-Grundstruktur** — fuer Futtermittelbereich: Gefahrenanalyse, CCP-Punkte, Kontrollmassnahmen

**Geschaetzter Aufwand:** ~8 Entwicklungstage

---

## 9. HRM / PERSONAL (HCM — Human Capital Management)

### Ist-Stand
- Zeit- & Schichterfassung, Stundenzettel, Abwesenheiten, Kalender
- Driver-Time-Pilot-Slice implementiert (2026-05-16)
- HRM-Operating-System mit Gate-Workflow

### Soll (Marktführende ERP-Systeme: HCM Cloud)
| Funktion | Ist | Gap |
|----------|-----|-----|
| Organisationsstruktur (Organigramm) | ❌ | **Kritisch** |
| Stellen-/Positionsverwaltung | ❌ | Wichtig |
| Personalakte vollstaendig | Teilweise | Ausbauen |
| Bewerbermanagement (Recruiting) | ❌ | Wichtig |
| Onboarding-Workflow | Teilweise | Vollstaendig |
| Performance-Management | ❌ | Mittel |
| Schulungs-/Qualifikationsverwaltung | Teilweise | Vollstaendig |
| Entgeltabrechnung (Payroll) | Teilweise | DATEV-Vollanbindung |
| ESS/MSS-Portal (Self-Service) | Teilweise | Ausbauen |
| Arbeitszeitkonto (Gleitzeitkonto) | Teilweise | Vollstaendig |
| BEM (Betriebliches Eingliederungsmanagement) | ❌ | Pflicht |
| Gefaehrdungsbeurteilung | ❌ | DSGVO/ArbSchG |
| Lohnsteuerliche Nebenleistungen | ❌ | Mittel |
| Reisekostenabrechnung | ❌ | Mittel |

### Umsetzungsschritte
1. **Organisationsstruktur** — `org_units` Tabelle (Hierarchie, Abteilung, Kostenstelle); `positions` Tabelle; `GET /personal/org-chart`; Frontend `personal/org-chart.tsx`
2. **Arbeitszeitkonto vollstaendig** — Saldo-Berechnung (Ist minus Soll); Uebertragssaldo; `GET /personal/time-accounts/{employee_ref}`
3. **Schulungsverwaltung vollstaendig** — `training_courses`, `training_enrollments`; Qualifikations-Tracking; Ablaufdatum-Warnung; `GET /personal/training/*`
4. **Bewerbermanagement** — `applications` Tabelle; Pipeline (Beworben → Erstgespraech → Endgespraech → Angebot → Eingestellt); `POST /personal/applications`
5. **BEM-Workflow** — Trigger bei >42 Krankheitstagen/Jahr; Gesprachsprotokoll; Massnahmen-Tracking
6. **Reisekostenabrechnung** — `travel_expenses` Tabelle; Tagespauschalen (BMVJ-Saetze); `POST /personal/travel-expenses`
7. **DATEV-Payroll vollstaendig** — LODAS-Export; Stammdaten-Uebermittlung; Lohnnachweis

**Geschaetzter Aufwand:** ~20 Entwicklungstage

---

## 10. FUTTERMITTEL — PRIORITAET P1

### Ist-Stand
- Rezeptur-Frontend detailliert (12 Seiten)
- Backend nur 2 Endpoints (Lots + Price-Matrix)
- Rations-Optimierungs-Service existiert in separatem Paket

### Soll (Cargill MAX / fodjan / AMTS / eigene Landhandels-Anforderungen)
| Funktion | Ist | Gap |
|----------|-----|-----|
| Rohwaren-Stamm (Naehrstoffprofil) | Teilweise | Vollstaendig |
| Rezepturverwaltung vollstaendig API | ❌ | **Kritisch** |
| Least-Cost-Formulierung (Optimierung) | Teilweise (Service) | API-Anbindung |
| Naehrstoffanalyse (Proximate Analysis) | ❌ | **Kritisch** |
| Futtermittelkennzeichnung (EU 2017/2279) | ❌ | Compliance-Pflicht |
| Chargen-Rueckverfolgung Futtermittel | ❌ | **Kritisch** |
| Qualitaetssicherung (QS-Leitfaden Futtermittel) | ❌ | **Kritisch** |
| Mischungsprotokoll (Dosierpruefung) | ❌ | Wichtig |
| Lieferanten-Spezifikationen | ❌ | Wichtig |
| HACCP-Dokumentation | ❌ | Pflicht |
| Produktionsauftrag Mischfutter | ❌ | **Kritisch** |
| Etikett-Druck (Inhaltsangabe, Deklaration) | ❌ | Pflicht |
| VLOG-Meldung (Ohne Gentechnik) | ❌ | Marktanforderung |

### Umsetzungsschritte
1. **Rohwaren-API vollstaendig** — Migration `feed_raw_materials_*`; Modell `FeedRawMaterial` (Naehrstoffprofil: RP, RFe, RFA, ME, Lysin, ...); `GET/POST/PATCH /futtermittel/rohwaren`
2. **Rezeptur-API vollstaendig** — `FeedRecipe`, `FeedRecipeIngredient`; `GET/POST /futtermittel/rezepte`; Version-History
3. **Naehrstoffanalyse** — Berechnung Ist-Profil aus Rohwaren-Anteilen; Soll/Ist-Vergleich gegen Tierartenspezifikation; `GET /futtermittel/rezepte/{id}/naehrstoffanalyse`
4. **Least-Cost-Optimierung API** — Verbindung des bestehenden Optimierungs-Service mit REST-API; `POST /futtermittel/optimierung/least-cost`
5. **Produktionsauftrag** — `FeedProductionOrder`; Streckenmengenberechnung; Chargen-ID-Vergabe; `POST /futtermittel/produktionsauftraege`
6. **Chargen-Rueckverfolgung** — Integration mit Lager-Chargen-System; `GET /futtermittel/chargen/{id}/trace`
7. **Kennzeichnung / Deklaration** — EU-konforme Inhaltsangabe generieren; `GET /futtermittel/rezepte/{id}/deklaration` → PDF
8. **QS-Dokumentation** — Lieferanten-Zulassung, Wareneingangs-Pruefung, HACCP-Massnahmen

**Geschaetzter Aufwand:** ~20 Entwicklungstage

---

## 11. POS (Point of Sale)

### Ist-Stand
- DSFINVK-Compliance (GoBD/KassenSichV), Position-Management
- Terminal-Frontend, Rückgaben, Tagesabschluss

### Soll (Etablierte POS-Systeme / Odoo POS / Lightspeed)
| Funktion | Ist | Gap |
|----------|-----|-----|
| Multi-Zahlungsarten (Bar/Karte/SEPA/Gutschein) | Teilweise | Vollstaendig |
| Kundenkarte / Kundenerkennung an Kasse | ❌ | Wichtig |
| Treueprogram (Punkte/Rabatte) | ❌ | Mittel |
| Promotions-Engine (Aktionspreise) | ❌ | Wichtig |
| Waagenintegration (automatisch) | Teilweise | Vollstaendig |
| Barcode-Scan (Produktidentifikation) | Teilweise | Ausbauen |
| X-/Z-Report (Tages-/Kassenabschluss) | Teilweise | Vollstaendig |
| Split-Zahlung | ❌ | Wichtig |
| Offline-Modus (IndexedDB Queue) | Teilweise | Vollstaendig |
| Gutschein-Verwaltung | ❌ | Mittel |
| Kassierer-Verwaltung (Schichten, Kassensturz) | Teilweise | Ausbauen |
| Multi-Terminal-Konsolidierung | ❌ | Wichtig |

### Umsetzungsschritte
1. **Zahlungsarten vollstaendig** — `payment_methods` Tabelle; Split-Payment-Logik; `POST /pos/checkout` erweitertes Payload
2. **Promotions-Engine** — `promotions` Tabelle (Zeitraum, Artikel, Rabatttyp, Staffel); automatische Anwendung im Checkout
3. **Waagenintegration** — SAPI-Protokoll (Standard-Waagen-API); `POST /pos/scale/read`; automatische Gewichtsuebernahme
4. **X-/Z-Report vollstaendig** — tagesabschluss mit Zahlungsart-Aufschluesselung, Stornos, Rueckgaben; PDF-Export
5. **Multi-Terminal-Konsolidierung** — `terminals` Tabelle; Tagesabschluss konsolidiert ueber alle Terminals

**Geschaetzter Aufwand:** ~10 Entwicklungstage

---

## 12. KONTRAKTE (zentrale Contract Engine) — PRIORITAET P1

### Ist-Stand
- Verteilt auf Einkauf + Agrar
- Kontrakt-CRUD, Positionen, Preismatrix
- Frontend: 8 Seiten

### Soll (Etablierte ERP-Plattformen: Contract Management / Odoo Contracts)
| Funktion | Ist | Gap |
|----------|-----|-----|
| Zentrale Vertrags-Engine (alle Typen) | ❌ | **Kritisch** |
| Vertragsvorlagen | ❌ | Wichtig |
| Versions-/Aenderungshistorie | ❌ | **Kritisch** |
| Genehmigungsworkflow (digital) | Teilweise | Vollstaendig |
| Bedingungen (Konventionalstrafen, Boni) | Teilweise | Vollstaendig |
| Automatische Verlaengerung / Kuendigung | ❌ | Wichtig |
| Verpflichtungs-Tracking (Obligations) | ❌ | **Kritisch** |
| E-Signatur-Integration | ❌ | Wichtig |
| Vertrags-Analytics (Laufzeit, Wert, Status) | Teilweise | Vollstaendig |
| Verknuepfung zu Belegen (PO, Lieferschein, Rechnung) | Teilweise | Vollstaendig |
| Vertragskalender (Faelligkeiten, Reviews) | ❌ | Wichtig |
| Erinnerungen / Alerts | Teilweise | Ausbauen |

### Umsetzungsschritte
1. **Zentrale Vertrags-Engine** — Neue Domain `contracts/`; `contracts` Tabelle mit `contract_type` (EINKAUF/VERKAUF/AGRAR/DIENSTLEISTUNG/MIETE); `contract_versions`; `contract_parties`; `GET/POST /kontrakte/contracts`
2. **Verpflichtungs-Tracking** — `contract_obligations` Tabelle (Leistung, Faelligkeit, Status); automatische Mahnung bei Ueberfallligkeit; `GET /kontrakte/contracts/{id}/obligations`
3. **Bedingungen vollstaendig** — `contract_conditions` (Konventionalstrafe, Bonus, Eskalation, Preisgleitklausel); automatische Berechnung bei Erfuellung/Verletzung
4. **Automatische Verlaengerung** — Kuendigungsfrist-Monitoring; Alert X Tage vor Ablauf; `PATCH /kontrakte/contracts/{id}/renew`
5. **E-Signatur** — Integration Signatur-Dienst (DocuSign/SIGN-ME/Skribble); `POST /kontrakte/contracts/{id}/sign`; Signatur-Status-Tracking
6. **Vertragsvorlagen** — `contract_templates` Tabelle; Parameter-basierte Befuellung; `POST /kontrakte/templates/{id}/create-contract`
7. **Vertrags-Analytics** — `GET /kontrakte/analytics` (Wert nach Typ/Laufzeit/Status, Faelligkeits-Kalender)

**Geschaetzter Aufwand:** ~18 Entwicklungstage

---

## 13. Gesamtplan und Phasen

### Phase 1 — Landhandel-Kern (P1-Gaps, ~55 Tage)
*Fokus: Die 4 kritischsten Gaps, die fuer taeglich-operativen Betrieb relevant sind*

| # | Domain | Hauptlieferung | Tage |
|---|--------|----------------|------|
| 1 | Lager/WMS | Lagerstruktur, FEFO, Pick-Listen, Bestandsbewertung | 25 |
| 2 | Kontrakte | Zentrale Engine, Obligations, Bedingungen, Alerts | 18 |
| 3 | Logistik | Tourenplanung, Frachtkosten, Track&Trace, CMR | 12 |
| 4 | Futtermittel (Basis) | Rohwaren-API, Rezeptur-API, Naehrstoffanalyse | 10 |

*Gesamtaufwand Phase 1: ~65 Entwicklungstage (3 Monate bei 3 Entwicklern)*

### Phase 2 — Prozesstiefe (P2-Gaps, ~70 Tage)
*Fokus: Vertiefung bestehender Domains auf Enterprise-Niveau*

| # | Domain | Hauptlieferung | Tage |
|---|--------|----------------|------|
| 5 | CRM | Pipeline, 360°-View, Service-Cases, E-Mail | 18 |
| 6 | Finance | Anlagen-AfA, Budgetierung, Liquiditaet, CO-PA | 20 |
| 7 | HRM | Organigramm, Arbeitszeitkonto, Schulungen, Payroll | 20 |
| 8 | Verkauf | Rahmenauftraege, 3-Wege-Match, Konditionstechnik | 12 |

*Gesamtaufwand Phase 2: ~70 Entwicklungstage (3 Monate bei 3 Entwicklern)*

### Phase 3 — Enterprise-Grade (P3-Gaps, ~40 Tage)
*Fokus: Compliance-Vertiefung, Agrar-Feinschliff, POS-Vollausbau*

| # | Domain | Hauptlieferung | Tage |
|---|--------|----------------|------|
| 9 | Agrar | PTBF-Vertiefung, GVO-Trennhaltung, Zertifikate | 8 |
| 10 | Compliance | DSGVO-Loeschkonzept, Whistleblower, LkSG | 8 |
| 11 | Futtermittel (Rest) | Produktionsauftrag, QS, Kennzeichnung, VLOG | 10 |
| 12 | Einkauf | 3-Wege-Match, ERS, Lieferanten-KPIs | 12 |
| 13 | POS | Multi-Zahlung, Promotions, Waage, X/Z-Report | 10 |

*Gesamtaufwand Phase 3: ~48 Entwicklungstage (2 Monate bei 3 Entwicklern)*

---

## 14. Gesamtaufwand

| Phase | Tage | Kalenderzeit (3 Entw.) | Prioritaet |
|-------|------|------------------------|-----------|
| Phase 1 — Kern | 65 | ~3 Monate | Sofort |
| Phase 2 — Tiefe | 70 | ~3 Monate | Nach Phase 1 |
| Phase 3 — Enterprise | 48 | ~2 Monate | Laufend |
| **Gesamt** | **183** | **~8 Monate** | — |

**Wichtige Rahmenbedingungen:**
- Jede Umsetzungseinheit folgt dem bestehenden Muster: Alembic-Migration → Service-Klasse → Thin-Router → Tests (>60% Coverage) → Frontend
- Externe Abhaengigkeiten (DATEV-Payroll, Elster ERiC, E-Signatur-Dienst) benoetigen separate Vertraege/AVV
- Domain-Prioritaeten koennen sich durch Kundenfeedback verschieben; Ratchet-Tests sichern Regression ab

---

## 15. Naechster konkreter Schritt (Phase 1, Sprint 1)

**Lager-Struktur und WMS-Grundlage** ist der kritischste erste Schritt, weil:
- Alle anderen Domains (Einkauf, Verkauf, Futtermittel) auf Lagerplatzdaten aufbauen
- FEFO/FIFO ist fuer Futtermittel und verderbliche Agrarware Pflicht
- Bestandsbewertung blockiert FIBU-Periodenabschluss

Konkrete erste Lieferung:
```
Alembic: warehouse_structure_20260517
  → domain_inventory.warehouses
  → domain_inventory.warehouse_zones
  → domain_inventory.warehouse_bins (mit capacity_kg, stock_kg)

API:
  GET/POST /lager/warehouses
  GET/POST /lager/bins
  GET /lager/bins/{id}/stock
  POST /lager/stock-movements (mit fefo_strategy)
  GET /lager/mhd-alert

Service: WarehouseService + FefoPickingService
Tests: tests/test_warehouse_fefo_picking.py
```
