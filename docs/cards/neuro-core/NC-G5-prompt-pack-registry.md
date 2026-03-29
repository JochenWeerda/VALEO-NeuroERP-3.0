# NC-G5 -- Prompt Pack Registry

**Lane:** Neuro-Core
**Prioritaet:** P2
**Status:** umgesetzt

## Kontext
Prompt Packs existieren als Contracts, aber eine versionierte Registry
mit Varianten-Handling fehlte. Dadurch ist kein kontrolliertes A/B
Testing moeglich.

## Loesung
In-memory Registry fuer Prompt Packs mit Variant-Key und Traffic-Weight,
Selection- und Rollback-Mechanik, REST-API fuer Verwaltung.

## Dateien
- `app/services/prompt_pack_registry.py`
- `app/api/v1/endpoints/neuro_prompt_packs.py`
- `tests/test_prompt_pack_registry.py`
- `docs/workflows/nc-g5-prompt-pack-registry.md`
