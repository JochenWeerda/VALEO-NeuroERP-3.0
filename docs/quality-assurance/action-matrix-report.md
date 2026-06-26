---
title: Action-Matrix-Report (SEMANTIC-ACTION-MATRIX-002)
description: Übersicht aller semantischen Prozessketten und E2E-Coverage-Status.
type: reference
audience: [qa, entwickler]
owner: Claude Code
status: aktiv
last_reviewed: 2026-06-26
version: 3.0.0
---

# Action-Matrix-Report

**Konsolidierungsstatus 2026-06-26:** Diese Datei ist ein generierter
QA-Heuristikreport. `GAP` bedeutet fehlende oder nicht erkannte E2E-Verknuepfung,
nicht automatisch fehlende Implementierung. Fuer echten Restbacklog gelten
Open-Gaps und der Konsolidierungsbericht.

> Generiert via `scripts/generate_action_matrix_report.py` · 2026-06-26 09:37:16 UTC

## Übersicht

| Metrik | Wert |
|---|---|
| Prozessketten | 6 |
| Aktionen gesamt | 24 |
| Green (E2E @critical/@smoke grün) | 2 |
| Partial (E2E vorhanden, nicht @critical) | 4 |
| Gap (keine E2E) | 18 |

## Finanzbuchhaltung (FiBu) (`fibu`)

> Buchung → OP-Verwaltung → Periodenabschluss → DATEV-Export
> Priorität: **HIGH**

| ID | Aktion | Route | Status | E2E-Tag |
|---|---|---|---|---|
| `fibu-001` | Buchungssatz erfassen | `fibu/buchungen` | GAP | `@smoke` |
| `fibu-002` | Offene Posten anzeigen / ausziffern | `fibu/offene-posten` | GAP | `@smoke` |
| `fibu-003` | Periodenabschluss durchführen | `fibu/periodenabschluss` | GAP | `@smoke` |
| `fibu-004` | DATEV-Export erstellen | `fibu/datev` | GAP | `@smoke` |

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

## Top-50-Routen ohne Matrix-Eintrag

- `admin/agenten-integration`
- `admin/ai-approvals`
- `admin/externe-gates`
- `admin/audit-log`
- `admin/benutzer`
- `admin/benutzer-liste`
- `admin/benutzer/neu`
- `admin/command-monitor`
- `admin/compliance`
- `admin/compliance-dashboard`
- `admin/control-center`
- `admin/control-center/agent-ops`
- `admin/control-center/superglue`
- `admin/data-quality`
- `admin/gap-pipeline`
- `admin/integrationen-quarantaene`
- `admin/monitoring/alerts`
- `admin/monitoring/regeln`
- `admin/nummernkreise`
- `admin/report-berechtigungen`
- `admin/rolle/neu`
- `admin/rollen-verwaltung`
- `admin/setup`
- `admin/setup/dms-integration`
- `admin/terminologie`
- `admin/voice-channel`
- `admin/webhooks`
- `admin/webshop`
- `agrar/aussaat`
- `agrar/aussaat/liste`
- `agrar/aussaat/neu`
- `agrar/biostimulanzien`
- `agrar/biostimulanzien-liste`
- `agrar/biostimulanzien-stamm`
- `agrar/bodenprobe/neu`
- `agrar/bodenproben`
- `agrar/bodenproben/liste`
- `agrar/duenger`
- `agrar/duenger-liste`
- `agrar/duenger-stamm`
- `agrar/duenger/bedarfsrechner`
- `agrar/duenger/liste`

*Stand: 2026-06-26 09:37:16 UTC · 24 Aktionen · Slice: SEMANTIC-ACTION-MATRIX-002*
