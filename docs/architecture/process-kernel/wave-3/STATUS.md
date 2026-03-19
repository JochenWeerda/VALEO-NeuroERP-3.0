# Wave 3 - Specialized Domain Enablement

**Status:** abgeschlossen
**Datum:** 2026-03-11

## Scope

Wave 3 fuehrt spezialisierte Domain-Bausteine fuer UI-Klassifikation, Audit-Evidence, IoT, Pricing, Qualitaetsdaten und Import-Pipelines ein.

## Zielbild

Spezifische Fachdomanen sollen formal an den Process Kernel angeschlossen werden, ohne Sonderpfade ausserhalb der Kernvertraege.

## Lieferumfang

| AP | Thema | Status |
|----|-------|--------|
| AP1 | UI-Maskenklassifizierung A/B/C | abgeschlossen |
| AP2 | Dokument- und Audit-Evidence-Modell | abgeschlossen |
| AP3 | IoT- und Telemetriepfade | abgeschlossen |
| AP4 | Pricing- und Marktdatenquellen | abgeschlossen |
| AP5 | Qualitaets- und Labordatenmodell | abgeschlossen |
| AP6 | Import-, Staging- und Pruefpipelines | abgeschlossen |

## Abnahmekriterien

- Klasse-A-Masken sind als Kernprozesse mit Explainability-Anforderungen klassifiziert.
- Audit-Evidence verknuepft Belege und Audit-Log-Eintraege GoBD-konform.
- IoT-, Pricing- und Qualitaetsdaten liegen als formale Kernmodelle vor.
- Import-Pipelines bilden einen standardisierten Zustands- und Validierungspfad.

## Tests

- `pytest tests/test_process_kernel_wave3_ap1_ap2.py tests/test_process_kernel_wave3_specialized.py -q`
- Compile-Check fuer die betroffenen Kernmodule

## Status

`abgeschlossen`
Stand: 2026-03-11
