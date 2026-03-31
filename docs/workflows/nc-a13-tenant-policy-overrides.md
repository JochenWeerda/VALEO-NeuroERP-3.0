# NC-A13 - Tenant Policy Overrides

## Ziel

Tenant-spezifische Policy-Overrides sollen nicht nur dokumentiert oder administrativ gepflegt werden, sondern in der Runtime-Auswertung von Verification und Policy Engine tatsaechlich wirksam sein.

## Ablauf

```mermaid
flowchart TD
    A[Plan / Step] --> B{tenant_policy_overrides?}
    B -- Ja --> C[normalize_tenant_policy_overrides()]
    B -- Nein --> D[DB Settings policy_overrides laden]
    C --> E[resolve_tenant_policy_sets()]
    D --> E
    E --> F[apply_tenant_overrides()]
    F --> G[evaluate_policy_set()]
    G --> H[Violations / Warnings / Eskalation]
```

## Umsetzung

- `normalize_tenant_policy_overrides()` akzeptiert jetzt explizite `TenantPolicyOverride`-Payloads, `policy_set_id`-gemappte Dicts und bestehende regelzentrierte Tenant-Settings mit `enabled` und `params_override`
- `apply_tenant_overrides()` kann neben deaktivierten und zusaetzlichen Regeln jetzt auch regelweise Parameter-Schwellen ueberschreiben
- `check_policy_conformity()` und `verify_plan()` reichen Tenant-Overrides auf Plan- und Step-Level durch und laden bei DB-gestuetzter Auswertung bestehende Tenant-Settings nach

## Betroffene Dateien

- `app/core/policy_code_engine.py`
- `app/services/neuro_verification_engine.py`
- `tests/test_neuro_verification_engine.py`
- `tests/test_process_kernel_wave29_policy_query.py`

## Ergebnis

- Die bisherige Luecke zwischen Admin-Policy-Overrides und Runtime-Verifikation ist geschlossen
- Tenant-Ausnahmen beeinflussen jetzt die wirksame Policy-Entscheidung produktiv im Verification-Pfad
- Offen bleiben nur weitergehende Nutzung dieser Overrides in tieferen Broker-/Execution- und UI-Flows
