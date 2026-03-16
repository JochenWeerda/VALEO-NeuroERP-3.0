# Wave-45 Status

## Scope
Feature Flag Contracts + Process Cost Contracts

## Zielbild

Wave 45 ergänzt den Process-Kernel um zwei Querschnittsthemen:

1. **Feature Flag Contracts**: Tenant-spezifische Feature-Flags mit 5 Rollout-Strategien
   (ALLE/PROZENTSATZ/TENANT_LISTE/ROLLE/KILL_SWITCH), A/B-Varianten und
   `pruefe_zugang()`-Evaluierung. KILL_SWITCH übersteuert immer → False.
   Hash-basierter Prozentsatz-Rollout für deterministische Bucket-Zuordnung je Tenant-ID.
   5 Standardflags: FF-001 (ALLE), FF-002 (30% Rollout), FF-003 (Pilot-Tenants),
   FF-004 (Rolle Einkauf), FF-005 (KILL_SWITCH inaktiv).

2. **Process Cost Contracts**: Kostentracking für Workflow-Ausführungen mit
   `KostenPosition.gesamt_eur` (4 Dezimalstellen), `ProzessKostenErfassung.positionen_nach_typ`
   (aggregiert nach KostenTyp), `BudgetUeberwachung.budget_status`
   (IM_RAHMEN/WARNUNG≥80%/UEBERSCHRITTEN=100%/GESPERRT>100%),
   und `pruefe_budget()` als nicht-mutierender Simulations-Check.
   4 Standardbudgets über agrar, finance, compliance und system.

## Lieferumfang

| AP | Zielmodul | Beschreibung | Status |
|----|-----------|--------------|--------|
| AP1 | `app/core/feature_flag_contracts.py` | `FeatureFlag` (ist_aktiv, ist_kill_switch, pruefe_zugang mit 5 Strategien), `FeatureFlagEvaluierung` (hat_zugang) | abgeschlossen |
| AP2 | `app/core/feature_flag_contracts.py` | `evaluiere_flags()`, `get_aktive_flag_ids()`, `get_default_feature_flags()` (5) | abgeschlossen |
| AP3 | `app/core/process_cost_contracts.py` | `KostenPosition` (gesamt_eur), `ProzessKostenErfassung` (gesamt_kosten_eur, positionen_nach_typ), `BudgetUeberwachung` (auslastung_pct, verbleibend_eur, budget_status) | abgeschlossen |
| AP4 | `app/core/process_cost_contracts.py` | `erstelle_kosten_erfassung()`, `pruefe_budget()` (nicht-mutierend), `get_default_budget_ueberwachungen()` (4) | abgeschlossen |
| AP5 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/feature-flags`, `POST /process/feature-flags/evaluiere` | abgeschlossen |
| AP6 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/costs/budget-ueberwachung`, `POST /process/costs/erstelle-erfassung` | abgeschlossen |

## Abnahmekriterien

- `pruefe_zugang()`: KILL_SWITCH immer False unabhängig vom Status
- PROZENTSATZ: `abs(hash(tenant_id)) % 100 < rollout_prozentsatz` — 100% immer True, 0% immer False
- ROLLE: leere `erlaubte_rollen` = alle Rollen erlaubt
- `budget_status`: GESPERRT wenn verbraucht > budget (nicht nur >= 100%)
- `pruefe_budget()` verändert das Original-Budget-Objekt nicht
- Kein Import von `app/api/` in `app/core/`

## Tests

`tests/test_process_kernel_wave45_flags_costs.py` — 78 Tests, alle grün

```bash
pytest tests/test_process_kernel_wave45_flags_costs.py -q --no-cov
# Ergebnis: 78 passed
```

## Status
`abgeschlossen`
