# Wave 89 - Multilingual + Fachsprache Landhandel konsistent

## Scope

Explizite Fachsprachen-Schicht fuer Landhandel-Terminologie, damit mehrsprachige Oberflaechen, Admin-Sichten und Agentenpfade gegen denselben Glossarstandard arbeiten.

## Zielbild

Landhandel soll eine zentrale, maschinenlesbare DE/EN-Terminologie erhalten, damit Fachsprache, UI-Begriffe und API-Sicht konsistent bleiben.

## Lieferumfang

| AP | Zielmodul | Beschreibung | Status |
|----|-----------|--------------|--------|
| AP1 | `app/core/terminology_registry.py` | Bilingualer Terminologie-Katalog mit kanonischen DE/EN-Begriffen, Synonymen und Avoid-Regeln | abgeschlossen |
| AP2 | `app/api/v1/endpoints/terminology.py` | Read-only API fuer Registry und Einzelbegriffe | abgeschlossen |
| AP3 | `packages/frontend-web/src/pages/admin/terminologie.tsx` | Admin-Sicht fuer Suche, Domain-Filter und zentrale Fachsprache | abgeschlossen |
| AP4 | `tests/test_process_kernel_wave89_terminology_registry.py` | Contract-Tests fuer Registry und API | abgeschlossen |

## Abnahmekriterien

- Der Katalog ist fuer Landhandel-Fachsprache maschinenlesbar abrufbar.
- DE/EN-Begriffe sind als kanonische Paare dokumentiert.
- Domain- und Suchfilter funktionieren deterministisch.
- Die Admin-Sicht zeigt den Katalog ohne Sonderlogik oder manuelle Datenpflege.

## Tests

- `python -m pytest tests/test_process_kernel_wave89_terminology_registry.py -q --no-cov`

## Status

`abgeschlossen` - 2026-03-20 - Terminologie-Registry, API und Admin-Sicht fuer konsistente DE/EN-Landhandel-Fachsprache produktiv.
