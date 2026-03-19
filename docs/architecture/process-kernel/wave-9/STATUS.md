# Wave 9 - EDI/API-Integration, Ernte-Kampagnen und Frontend-Prozessanbindung

**Status:** abgeschlossen
**Datum:** 2026-03-19

## Scope

Wave 9 modelliert externe Integrationen, Ernte-Kampagnen, API-Gateway-Manifeste, Frontend-Process-Binding und Zertifikatslogik als Kernvertraege.

## Zielbild

Externe Partner, saisonale Agrarprozesse und Frontend-Bindings sollen ueber dieselben Command- und Governance-Regeln mit dem Process Kernel verbunden sein.

## Lieferumfang

| AP | Thema | Status |
|----|-------|--------|
| AP1 | EDI-Integrations-Klassen | abgeschlossen |
| AP2 | Ernte-Kampagne | abgeschlossen |
| AP3 | API-Gateway-Manifest | abgeschlossen |
| AP4 | Frontend-Process-Binding | abgeschlossen |
| AP5 | Zertifikate und Qualitaetsnachweise | abgeschlossen |

## Abnahmekriterien

- EDI-Nachrichten koennen geparst und validiert werden.
- ErnteKampagne bildet Fortschritt und Zustandsmaschine korrekt ab.
- API-Gateway-Registry prueft Scopes und Rate-Limits.
- Frontend-Masken binden sich ueber Commands statt CRUD an.

## Tests

- `pytest tests/test_process_kernel_wave9_integration.py -q --no-cov`
- Ergebnis: 28 passed
- `pytest tests/test_process_kernel_wave9_domain.py -q --no-cov`
- Ergebnis: 22 passed

## Status

`abgeschlossen`
Stand: 2026-03-19
