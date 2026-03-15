# Wave-35 Status

## Scope
Inline-Validierung mit domain-spezifischen Erklaerungen (Gap 026) + Leitsystem fuer Ausnahmefaelle / Error UX (Gap 028)

## Zielbild

Wave 35 schliesst zwei P1-Luecken:
Gap 026 (Inline-Validierung mit domain-spezifischen Erklaerungen — 35% weniger Eingabefehler)
und Gap 028 (Leitsystem fuer Ausnahmefaelle — 50% weniger Abbruchquote bei Fehlern).

Die Inline-Validierungs-Contracts definieren typisierte Felddefinitionen mit
PFLICHTFELD/FORMAT/BEREICH/LAENGE-Regeln und domain-spezifischen WHY-Erklaerungen.
Das Error-Guidance-System mappt HTTP-Statuscodes + Fehlerklassen determinierst
auf Leitaktionen (EINGABE_KORRIGIEREN, BERECHTIGUNG_ANFRAGEN, WARTEN_UND_WIEDERHOLEN etc.)
mit prozesskontext-spezifischen Handlungsanweisungen.

## Lieferumfang

| AP | Zielmodul | Beschreibung | Status |
|----|-----------|--------------|--------|
| AP1 | `app/core/inline_validation_contracts.py` | `FeldTyp`, `InlineValidierungsRegel`, `InlineValidierungsFeld`, `validate_inline_field()` mit PFLICHTFELD/FORMAT/BEREICH/LAENGE | abgeschlossen |
| AP2 | `app/core/inline_validation_contracts.py` | `get_default_field_validations()` — 6 Felder fuer Agrar/Finance/Compliance mit domain-spezifischen Erklaerungen | abgeschlossen |
| AP3 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/inline-validations[?domain=]` + `POST /process/inline-validations/validate` | abgeschlossen |
| AP4 | `app/core/error_guidance_contracts.py` | `FehlerKategorie`, `LeitAktion`, `ErrorGuidanceRegel`, `evaluate_error_guidance()` mit Kontext-Priorisierung | abgeschlossen |
| AP5 | `app/core/error_guidance_contracts.py` | `get_default_error_guidance_rules()` — 12 Regeln fuer 422/403/409/429/503/500 | abgeschlossen |
| AP6 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/error-guidance[?http_status=]` + `POST /process/error-guidance/evaluate` | abgeschlossen |

## Abnahmekriterien

- `validate_inline_field()` prueft fail-fast in Reihenfolge: PFLICHTFELD -> LAENGE -> FORMAT -> BEREICH
- ReDoS-Schutz: Eingaben >500 Zeichen werden vor `re.fullmatch()` abgelehnt
- NaN/Inf-Schutz bei BEREICH-Regeln
- `evaluate_error_guidance()` bevorzugt kontext-spezifische Regeln gegenueber ALLGEMEIN
- Kein Match -> deterministischer Fallback ohne 500er
- Kein Import von `app/api/` in `app/core/`

## Tests

`tests/test_process_kernel_wave35_validation_guidance.py` — 54 Tests, alle gruen

```bash
pytest tests/test_process_kernel_wave35_validation_guidance.py -q --no-cov
# Ergebnis: 54 passed
```

## Status
`abgeschlossen`
