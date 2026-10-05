# Ackerschlagkartei — Umsetzungsplan

Stand: 2026-07-16
Lastenheft: `lastenheft-ackerschlagkartei-lwk-2017-plus-valeo.md`
Methode: TDD (Unit → API → UI)

## Inkrement 1 — Betrieb/WJ → Schlag → Plan → Aussaat → Schlaginfo → Bericht

Status: **Kern umgesetzt 2026-07-16** (Slice `ACKER-INK1-GAPS-008`)

| Baustein | Status |
|---|---|
| Arbeitskontext WJ | done |
| Wirtschaftsjahr am Schlag | done |
| Schlaginfo + DFL | done |
| Jahreswechsel | done |
| Sammeldüngung | done |
| ANDI setzt WJ | done |
| Druckbares PDF-Schlagdossier | Text-Export done (PDF-Layout Folge) |

## Inkrement 2 — Betriebsmittelstämme → Düngung → Lager/Kosten

Status: **Kern umgesetzt 2026-07-16** (`ACKER-OPEN-GAPS-009`)

- Stammdaten-Resolver + `/stammdaten`
- Lagerverbrauch-Buchungsplan + Persistenz an Maßnahme

## Inkrement 3 — PSM-Stamm → Zulassung → mobil Ausführung

Status: **Kern umgesetzt 2026-07-16**

- Sachkundenachweis Domain+UI
- Offline-Queue `/offline/sync` (idempotent client_ref)

## Inkrement 4 — Bodenhistorie → Beregnung → Erntecharge

Status: **Beregnung done**; Bodenhistorie/Erntecharge PARTIAL (Einzelwerte am Schlag bleiben)

## Inkrement 5 — QS/AUM → Auditpaket → NÄON/ENNI → Precision Farming

- QS-Checkliste + AUM Register: **done**
- NÄON/ENNI / Precision Farming: **BLOCKED** (externe Gates)

## DoD je Inkrement

Tests grün, Migration Single-Head, OpenAPI/Traceability, Workboard, keine Regression AS-W1…W10.
