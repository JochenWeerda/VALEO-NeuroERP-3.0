# Wave 4 - Operational Hardening and Runtime Closure

**Status:** abgeschlossen
**Datum:** 2026-03-11

## Scope

Wave 4 haertet die in Waves 1 bis 3 eingefuehrten Plattformbausteine mit persistenter Laufzeit, Projektionen, SLA-Beobachtung, operativer Governance und Runtime-Operations.

## Zielbild

Der Process Kernel soll produktionsfest werden: mit persistenter Workflow-Laufzeit, echten Projektionspfaden, Governance-Audit und standardisierten Betriebsmetriken.

## Lieferumfang

| AP | Thema | Status |
|----|-------|--------|
| AP1 | Persistente Workflow-Laufzeit | abgeschlossen |
| AP2 | Asynchrone Projektionen und Consumer | abgeschlossen |
| AP3 | SLA-, Timeout- und Eskalationsbeobachtung | abgeschlossen |
| AP4 | Operative Governance und Audit | abgeschlossen |
| AP5 | Finance-Folgesichten | abgeschlossen |
| AP6 | Runtime-Operations und Rebuild-/Replay-Pfade | abgeschlossen |

## Abnahmekriterien

- Workflow-Instanzen und Checkpoints sind persistent modelliert.
- Read-Models laufen ueber explizite Projektionsbuilder und Projektionsstatus.
- SLA-Policies und Violations sind ueber API auswertbar.
- Governance- und Runtime-Contracts liefern reproduzierbare Betriebsdaten.

## Tests

- Verifikation ueber die Wave-4-Testpfade und Runtime-Checks
- Bestehende Finance- und Runtime-Schnitte bleiben anschlussfaehig

## Status

`abgeschlossen`
Stand: 2026-03-11
