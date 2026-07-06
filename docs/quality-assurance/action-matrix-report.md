---
title: Action-Matrix-Report (SEMANTIC-ACTION-MATRIX-002)
description: Übersicht aller semantischen Prozessketten und E2E-Coverage-Status.
type: reference
audience: [qa, entwickler]
owner: Claude Code
status: aktiv
last_reviewed: 2026-07-05
version: 3.0.0
---

# Action-Matrix-Report

> Generiert via `scripts/generate_action_matrix_report.py` · 2026-07-05 05:22:18 UTC

## Übersicht

| Metrik | Wert |
|---|---|
| Prozessketten | 8 |
| Aktionen gesamt | 38 |
| Green (E2E @critical/@smoke grün) | 2 |
| Partial (E2E vorhanden, nicht @critical) | 4 |
| Gap (keine E2E) | 32 |

## Administration & Betrieb (`admin`)

> Mandanten-Admin, RBAC, Monitoring, Integrationen — Top-50-In-App-Routen
> Priorität: **MEDIUM**

| ID | Aktion | Route | Status | E2E-Tag |
|---|---|---|---|---|
| `admin-001` | Administration (Stammdaten, Setup, Monitoring) | `admin` | GAP | `-` |
| `admin-002` | Executive Dashboard | `management/executive-dashboard` | GAP | `-` |
| `admin-003` | Live-Monitoring | `system/live-monitor` | GAP | `-` |
| `admin-004` | Artikel-Stammdaten | `stammdaten/artikel` | GAP | `-` |
| `admin-005` | Mobile Scanner | `mobile/scanner` | GAP | `-` |
| `admin-006` | Public Verify | `public/verify` | GAP | `-` |
| `admin-007` | Firmeneinrichtung | `setup/firma` | GAP | `-` |

**Offene Gaps:**

- Admin-Routen: bewusst Admin-Handbuch statt Endnutzer-E2E; Matrix-Eintrag fuer Top-50-Coverage

## Agrar-Stammdaten & Feldarbeit (`agrar`)

> Aussaat, Dünger, Bodenproben, Biostimulanzien — Ergänzung zur Ernteannahme-Kette
> Priorität: **HIGH**

| ID | Aktion | Route | Status | E2E-Tag |
|---|---|---|---|---|
| `agrar-001` | Agrar-Stammdaten und Feldarbeit | `agrar` | GAP | `@smoke` |

**Offene Gaps:**

- agrar-001: Dedizierte E2E fuer Aussaat/Dünger/Bodenproben noch offen (Annahme-Kette separat in WMS/O2C)

## Finanzbuchhaltung (FiBu) (`fibu`)

> Buchung → OP-Verwaltung → Periodenabschluss → DATEV-Export
> Priorität: **HIGH**

| ID | Aktion | Route | Status | E2E-Tag |
|---|---|---|---|---|
| `fibu-001` | Buchungssatz erfassen | `fibu/buchungen` | GAP | `@smoke` |
| `fibu-002` | Offene Posten anzeigen / ausziffern | `fibu/offene-posten` | GAP | `@smoke` |
| `fibu-003` | Periodenabschluss durchführen | `fibu/periodenabschluss` | GAP | `@smoke` |
| `fibu-004` | DATEV-Export erstellen | `fibu/datev` | GAP | `@smoke` |
| `fibu-005` | Umsatzsteuervoranmeldung exportieren | `export/umsatzsteuervoranmeldung` | GAP | `-` |
| `fibu-006` | UStVA Kurzroute exportieren | `export/ustva` | GAP | `-` |

**Offene Gaps:**

- fibu-001/002/003/004: Alle FiBu-Aktionen noch ohne E2E (externe Assessoren für DATEV)

## Order-to-Cash (O2C) (`o2c`)

> Verkaufsauftrag → Lieferschein → Ausgangsrechnung → Zahlung
> Priorität: **CRITICAL**

| ID | Aktion | Route | Status | E2E-Tag |
|---|---|---|---|---|
| `o2c-001` | Verkaufsauftrag anlegen | `verkauf/auftrag` | GREEN | `@critical` |
| `o2c-002` | Lieferschein aus Auftrag generieren | `verkauf/lieferschein` | GREEN | `@critical` |
| `o2c-003` | Ausgangsrechnung stellen | `verkauf/rechnung` | PARTIAL | `@smoke` |
| `o2c-004` | Zahlung buchen / OP ausziffern | `fibu/offene-posten` | GAP | `@smoke` |
| `o2c-005` | Vertreterprovisionen pruefen | `crm/vertreterprovisionen` | GAP | `-` |
| `o2c-006` | Vertreterstamm pflegen | `crm/vertreterstamm` | GAP | `-` |

**Offene Gaps:**

- o2c-003: Rechnungs-PDF-Generierung noch ohne @critical
- o2c-004: Zahlungseingang-Buchung noch ohne E2E

## Procure-to-Pay (P2P) (`p2p`)

> Bestellanforderung → Bestellung → Wareneingang → Eingangsrechnung → Zahlung
> Priorität: **HIGH**

| ID | Aktion | Route | Status | E2E-Tag |
|---|---|---|---|---|
| `p2p-001` | Bestellung anlegen | `einkauf/bestellung` | PARTIAL | `@smoke` |
| `p2p-002` | Wareneingang buchen | `einkauf/wareneingang` | GAP | `@smoke` |
| `p2p-003` | Eingangsrechnung prüfen / freigeben | `einkauf/rechnung` | GAP | `@smoke` |
| `p2p-004` | Zahlungslauf ausführen (SEPA) | `fibu/zahlungslaeufe` | GAP | `@smoke` |

**Offene Gaps:**

- p2p-002/003/004: WE-Buchung, Rechnungsprüfung, SEPA-Lauf ohne E2E

## POS / Kasse (`pos`)

> Kassenvorgang → TSE-Signatur → DSFinV-K → Tagesabschluss
> Priorität: **MEDIUM**

| ID | Aktion | Route | Status | E2E-Tag |
|---|---|---|---|---|
| `pos-001` | Kassenbon erstellen | `pos` | GAP | `@smoke` |
| `pos-002` | TSE-Signatur prüfen | `pos` | GAP | `@smoke` |
| `pos-003` | Tagesabschluss (Z-Bericht) | `pos` | GAP | `@smoke` |

**Offene Gaps:**

- pos-001/002/003: POS-Kette ohne E2E (TSE-Simulation erforderlich)
- TSE-Simulation via /dev/external-mocks/tse

## Qualitätssicherung (QS) (`qs`)

> Labor-Probe → Analyse → Freigabe/Sperrung → Reklamation
> Priorität: **HIGH**

| ID | Aktion | Route | Status | E2E-Tag |
|---|---|---|---|---|
| `qs-001` | QS-Probe anlegen | `lager/qs-leitstand` | GAP | `@smoke` |
| `qs-002` | Laborergebnis erfassen | `lager/qs-leitstand` | GAP | `@smoke` |
| `qs-003` | Charge freigeben / sperren | `lager/qs-leitstand` | GAP | `@smoke` |
| `qs-004` | Reklamation anlegen | `lager/qs-leitstand` | GAP | `@smoke` |
| `qs-005` | Datenschutz-Compliance pruefen | `compliance/datenschutz` | GAP | `-` |
| `qs-006` | GoBD-Compliance pruefen | `compliance/gobd` | GAP | `-` |

**Offene Gaps:**

- qs-001/002/003/004: QS-Kette komplett ohne E2E

## Warehouse Management / Agrar-Materialfluss (`wms`)

> Wareneingang → Einlagerung → QS-Prüfung → Auslagerung
> Priorität: **CRITICAL**

| ID | Aktion | Route | Status | E2E-Tag |
|---|---|---|---|---|
| `wms-001` | Wareneingang erfassen | `lager/einlagerung` | PARTIAL | `@smoke` |
| `wms-002` | Einlagerung durchführen | `lager/einlagerung` | PARTIAL | `@smoke` |
| `wms-003` | QS-Probe anlegen / Labor | `lager/qs-leitstand` | GAP | `@smoke` |
| `wms-004` | Freigabe / Sperrung nach QS | `lager/qs-leitstand` | GAP | `@smoke` |
| `wms-005` | Auslagerung / Kommissionierung | `lager/auslagerung` | GAP | `@smoke` |

**Offene Gaps:**

- wms-003/004/005: QS-Freigabe und Auslagerung ohne E2E

*Stand: 2026-07-05 05:22:18 UTC · 38 Aktionen · Slice: SEMANTIC-ACTION-MATRIX-002*
