# NC-G4 -- Policy Registry Ausbau

**Lane:** Neuro-Core
**Prioritaet:** P2
**Status:** umgesetzt

## Kontext
Policy-Versionierung war vorhanden, aber A/B-Varianten und Selektion
fehlten. Ohne Varianten-Handling ist kontrolliertes Testing unmoeglich.

## Loesung
Variant-Key + Traffic-Weight im Registry-Entry, Auswahl-API und Liste
aktiver Varianten. Rollback bleibt erhalten.

## Dateien
- `app/services/policy_registry.py`
- `app/api/v1/endpoints/neuro_event_policy.py`
- `tests/test_policy_registry.py`
- `docs/workflows/nc-g4-policy-registry.md`
