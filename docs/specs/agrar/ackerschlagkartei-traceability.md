# Ackerschlagkartei — Traceability (ASK-*)

Stand: 2026-07-16
Statuswerte: NOT_IMPLEMENTED | PARTIAL | IMPLEMENTED_UNVERIFIED | VERIFIED | BLOCKED

| ID | Thema | Status | Nachweis |
|---|---|---|---|
| ASK-BUS-001 | Betriebsstamm / Snapshot | VERIFIED | `betrieb.py` + `/portal/feldbuch/betrieb`; Unit-Test |
| ASK-BUS-002 | Arbeitskontext WJ/Rolle/Sync | VERIFIED | `arbeitskontext.py` + Endpoints; Ink1-Tests |
| ASK-MST-001 | Dünger-/PSM-/Kultur-Stämme Portal | VERIFIED | `stammdaten.py` + `/stammdaten`; Open-Gaps-Tests |
| ASK-FLD-001 | Schlag CRUD + FLIK/GIS | PARTIAL | Portal CRUD; ERP GeoJSON/MapLibre (GIS-Versionierung folgt) |
| ASK-FLD-002 | Schlaginfo + DFL + Drucktext | VERIFIED | `schlaginfo.py`/`schlaginfo_export.py` + `.txt`-Export |
| ASK-PLAN-001 | Anbauplan-Übersicht | VERIFIED | AS-W7 |
| ASK-PLAN-002 | ANDI-Import | VERIFIED | AS-W8 |
| ASK-PLAN-003 | Jahreswechsel | VERIFIED | `jahreswechsel.py` |
| ASK-SEED-001 | Aussaat-Register | VERIFIED | `aussaat.py` + Register-Validierung Create |
| ASK-SOIL-001 | Nmin/Boden | VERIFIED | AS-W5 |
| ASK-FERT-001 | Reinnährstoff-Düngung / 170 kg | VERIFIED | AS-W1 |
| ASK-FERT-002 | Düngebedarf | VERIFIED | AS-W2 |
| ASK-FERT-003 | Sammelbuchung Düngung | VERIFIED | `sammelbuchung.py` |
| ASK-PPP-001 | PSM-Dokumentation PflSchG/CC | VERIFIED | AS-W4 |
| ASK-PPP-002 | Sachkundenachweis-Freigabe | VERIFIED | `sachkunde.py` + Portal-UI-Felder + Spalten |
| ASK-IRR-001 | Beregnung | VERIFIED | `beregnung.py` + Typ `beregnung` |
| ASK-HARV-001 | Ernte + DFL | VERIFIED | AS-W6 |
| ASK-QS-001 | QS-Checkliste | VERIFIED | `qs_checkliste.py` + `/qs-checkliste` |
| ASK-ENV-001 | AUM | VERIFIED | `aum.py` + Typ `aum` |
| ASK-COST-001 | Lagerverbrauch je Maßnahme | VERIFIED | `lagerverbrauch.py` + `/lagerverbrauch` (ERP-Bestandsbuchung folgt) |
| ASK-MOB-001 | Offline-Queue Sync | VERIFIED | `offline_queue.py` + `/offline/sync` (PWA-Runtime folgt) |
| ASK-INT-001 | NÄON/ENNI | BLOCKED | Partner-/Behördenvertrag erforderlich |
| ASK-NFR-001 | Aggregate-Modell Kap. 41 | PARTIAL | flaches Journal + Register-JSONB bewusst |

## Externe Gates (nicht repo-schließbar)

- **ASK-INT-001 NÄON/ENNI:** amtliche Schnittstelle / Partnervertrag
- **Precision Farming / Telemetrie:** Maschinenhersteller-Verträge
- **Native Offline-App:** ASK-MOB Queue/Sync-Kern ist da; Store-Distribution/Service-Worker-App = Folgeprojekt

## Testnachweis Open-Gaps

`pytest tests/test_feldbuch_open_gaps.py` (+ Ink1/Sachkunde-Regression)
