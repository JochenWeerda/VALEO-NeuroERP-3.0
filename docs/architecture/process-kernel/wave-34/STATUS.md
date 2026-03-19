# Wave-34 Status

## Scope
Tenant-isolierte Caches/Rate-Limits (Gap 038) + Security-Hardening-Contracts (Gap 049)

## Zielbild

Wave 34 schliesst zwei P0/P1-Luecken:
Gap 038 (Tenant-isolierte Caches/Rate Limits — 0 Cross-tenant Performance-Kollisionen)
und Gap 049 (Security-Hardening OIDC/RBAC/Secrets/Audit — 0 kritische Pentest-Findings).

Die Rate-Limit-Contracts definieren konfigurierbare Policies pro Domain mit
Soft-/Hard-Limits, Wildcard-Matching und deterministischer evaluate_rate_limit()-Logik.
Die Security-Hardening-Contracts modellieren SecurityControls (OWASP-basiert),
feingranulaere RBAC-Permissions, SecretKlassifikation und evaluate_security_posture()
als pruefbares Contract-Fundament fuer Security-Reviews und Pentests.

## Lieferumfang

| AP | Zielmodul | Beschreibung | Status |
|----|-----------|--------------|--------|
| AP1 | `app/core/tenant_rate_limits.py` | `RateLimitPolicy`, `TenantCacheConfig`, `evaluate_rate_limit()`; Wildcard-Matching; konservativste Policy gewinnt | abgeschlossen |
| AP2 | `app/core/tenant_rate_limits.py` | `get_default_rate_limit_policies()` (8 Policies), `get_default_cache_configs()` (3 Tiers) | abgeschlossen |
| AP3 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/rate-limits[?domain=]` + `POST /process/rate-limits/check` | abgeschlossen |
| AP4 | `app/core/security_hardening_contracts.py` | `SecurityControl`, `RBACPermission` (17 Werte), `evaluate_rbac_permission()`, Rollen-Permission-Matrix | abgeschlossen |
| AP5 | `app/core/security_hardening_contracts.py` | `SecretKlassifikation`, `evaluate_security_posture()`, `get_default_security_controls()` (13 Controls) | abgeschlossen |
| AP6 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/security/controls[?kategorie=]` + `POST /process/security/rbac-check` | abgeschlossen |

## Abnahmekriterien

- `evaluate_rate_limit()` liefert ERLAUBT / GEDROSSELT / BLOCKIERT deterministisch
- Konservativste Policy (niedrigstes hard_limit) gewinnt bei mehreren Matches
- RBAC-Pruefung erfolgt rollenbasiert gegen feste Permission-Matrix (keine DB)
- SecurityControl-Katalog deckt OWASP A01-A09 ab mit Implementierungsstatus
- `evaluate_security_posture()` gibt KRITISCH bei offenen kritischen Findings
- SecretKlassifikation regelt Logging-Entscheidung programmatisch
- Kein Import von `app/api/` in `app/core/`

## Tests

`tests/test_process_kernel_wave34_ratelimits_security.py` — 55 Tests, alle gruen

```bash
pytest tests/test_process_kernel_wave34_ratelimits_security.py -q --no-cov
# Ergebnis: 55 passed
```

## Status
`abgeschlossen`
Stand: 2026-03-19
