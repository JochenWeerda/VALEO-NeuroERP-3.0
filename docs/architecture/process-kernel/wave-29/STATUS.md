# Wave-29 Status

## Scope
Policy-as-Code Engine (Gap 014) + Query-Vertrags-Registry (Gap 031)

## Zielbild

Wave 29 schliesst zwei P0-Luecken:
Gap 014 (Policy-as-Code mit Tenant Overrides — 100% Ausnahmen regelbasiert dokumentiert)
und Gap 031 (Query-Contracts fuer Frontend — keine undefinierten Query-Ergebnisse).

Die Policy-as-Code Engine macht Geschaeftsregeln als versionierte, pruefbare
Regelsets explizit; Tenant-Overrides erlauben genossenschaftsspezifische
Ausnahmen ohne Code-Aenderung. Die Query-Vertrags-Registry typisiert alle
Read-Model-Abfragen des Process-Kernels, sodass Frontend-Clients nie
undefinierte Felder erhalten.

## Lieferumfang

| AP | Zielmodul | Beschreibung | Status |
|----|-----------|--------------|--------|
| AP1 | `app/core/policy_code_engine.py` | `PolicyBedingungsTyp`, `PolicyRegel`, `PolicySet`; `evaluate_policy_set(policy_set, kontext)` → `PolicyEvaluationResult` | geplant |
| AP2 | `app/core/policy_code_engine.py` | `TenantPolicyOverride`; `apply_tenant_overrides(base, override)` → merged `PolicySet`; `validate_policy_set()` | geplant |
| AP3 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/policy-rules/{prozess_key}` + `POST /process/policy-rules/evaluate` | geplant |
| AP4 | `app/core/query_contracts.py` | `QueryResultFeld`, `QueryContract`, `QueryRegistry`; `get_process_kernel_queries()` | geplant |
| AP5 | `app/core/query_contracts.py` | `validate_query_result(contract, result)` → `QueryValidationResult` | geplant |
| AP6 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/query-registry[?prozess_key=]` | geplant |

## Abnahmekriterien

- `evaluate_policy_set()` wertet ERLAUBT/ABGELEHNT/WARNUNG/ESKALATION deterministisch aus
- Tenant-Overrides koennen Regeln hinzufuegen oder deaktivieren; Basis-Pflichtregeln bleiben unberueehrt
- `validate_policy_set()` erkennt Konflikte (z.B. ERLAUBT + ABGELEHNT fuer gleiche Bedingung)
- Query-Contracts definieren Felder typsicher; `validate_query_result()` prueft nullable-Verletzungen
- Kein Import von `app/api/` in `app/core/`
- Alle Query-Contracts maschinell pruefbar (keine undefined-Felder moeglich)

## Tests

| Datei | Tests | Scope |
|-------|-------|-------|
| `tests/test_process_kernel_wave29_policy_query.py` | 52 | AP1: PolicyBedingung.evaluate() (10 Tests); evaluate_policy_set() (7 Tests, alle Aktionen + Prioritaet); AP2: apply_tenant_overrides() (5 Tests, Pflichtregeln, Immutabilitaet); validate_policy_set() (5 Tests); Default-Sets valid (1 Test); AP4: QueryRegistry (8 Tests); AP5: validate_query_result() (8 Tests, alle Violation-Codes); AP3/AP6: API-Endpoints (8 Tests) |

**Gesamt Wave 29: 52 Tests gruen**

## Gaps geschlossen

| Gap-ID | Beschreibung | Massnahme |
|--------|-------------|-----------|
| Gap 014 | Policy-as-Code mit Tenant Overrides | `policy_code_engine.py`: `evaluate_policy_set()` (ERLAUBT/ABGELEHNT/WARNUNG/ESKALATION), `apply_tenant_overrides()` (Pflichtregeln sicher), `validate_policy_set()`, Default-PolicySets fuer agrar_settlement + wareneingang; API GET /process/policy-rules + POST /process/policy-rules/evaluate |
| Gap 031 | Query-Vertraege (keine undefined) | `query_contracts.py`: `QueryContract` + `QueryResultFeld` + `validate_query_result()` (strict + non-strict), 6 Contracts (agrar_settlement×2, wareneingang, ap_invoice, workflow, intrastat); API GET /process/query-registry |

## Status
`abgeschlossen` — 2026-03-15 — 52 Tests gruen, Gaps 014 + 031 geschlossen
