# PKP-03 Override-Prioritätsmodell

## Zweck
- eindeutige Priorität für globale, tenant-, rollen- und prozessbezogene Overrides

## Status
- erstes Backend-Kernmodell angelegt
- Code-Artefakt: `app/core/policy_decisions.py`

## Priorität
1. `global`
2. `tenant`
3. `role`
4. `process`

## Kernobjekte
- `PolicyOverrideLayer`
- `PolicyOverrideResolution`
- `resolve_policy_override_layers(...)`

## Kerngedanke
- jede Entscheidung wird aus expliziten Layern aufgelöst
- Ergebnis enthält wirksame Ebene, Grund, Quelle und effektive Parameter
- das Modell ist direkt für Explainability und Audit nutzbar

## Nächster Schritt
- bestehende Tenant-Overrides aus `app/core/policy_overrides.py` auf dieses Modell abbilden
