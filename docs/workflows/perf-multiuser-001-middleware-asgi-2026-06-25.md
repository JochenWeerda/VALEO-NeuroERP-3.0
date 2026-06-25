# PERF-MULTIUSER-001 — Middleware-Stack auf pure ASGI + Logging entschlacken

**Owner:** Cursor
**Stand:** 2026-06-25 — umgesetzt
**Ziel:** Latenz und CPU-Last pro Request unter Multi-User-Last senken, ohne
Auth-, Tenant-, Audit- oder Security-Header-Semantik zu verändern.

## Problem

Der HTTP-Request-Hotpath nutzte sechs `BaseHTTPMiddleware`/
`@app.middleware("http")`-Schichten:

1. `PrometheusMiddleware`
2. `CorrelationMiddleware`
3. `SecurityHeadersMiddleware`
4. `AuditMiddleware`
5. `enforce_bearer_token` (`@app.middleware("http")`)
6. `log_requests` (`@app.middleware("http")`)

Starlettes `BaseHTTPMiddleware` wickelt jeden Request über anyio-Memory-Streams
ab. Unter Nebenläufigkeit erzeugt das erheblichen Overhead und serialisiert
Requests teilweise. Zusätzlich schrieb `log_requests` **zwei INFO-Logs pro
Request** (inkl. aller GETs), die jeweils durch den PII-Redaction-Regex-Filter
liefen — unnötige CPU-Last und Log-Flut im Multi-User-Betrieb.

## Messung (Micro-Benchmark)

Isolierter Benchmark der vier Response-/Context-Middleware gegen eine identische
App ohne Middleware (`scripts/benchmark_middleware_stack.py`, 3000 Requests,
Concurrency 32, ohne DB/Auth/Lifespan):

| Szenario           | vorher (BaseHTTPMiddleware) | nachher (pure ASGI) |
|--------------------|-----------------------------|---------------------|
| GET /ping  — RPS   | ~334                        | ~795                |
| GET /ping  — mean  | 82.2 ms                     | 1.21 ms             |
| GET /ping  — p99   | 159.5 ms                    | 4.14 ms             |
| POST /echo — RPS   | ~332                        | ~839                |
| POST /echo — mean  | 82.3 ms                     | 1.14 ms             |

Der reine Middleware-Overhead sank von **~82 ms/Request auf < 0,3 ms/Request**.
Die absoluten RPS-Zahlen sind maschinenabhängig; entscheidend ist der
Overhead-Delta zwischen „bare" und „stacked".

## Änderungen

- `app/middleware/metrics.py` — `PrometheusMiddleware` als reine ASGI-Middleware;
  Status-Code aus `http.response.start`; Pfad-Regex auf Modulebene vorkompiliert
  (vorher pro Request kompiliert), `_simplify_path` als Modulfunktion.
- `app/middleware/correlation.py` — `CorrelationMiddleware` als reine ASGI-Middleware;
  ContextVars token-basiert gesetzt/zurückgesetzt; Correlation-ID via `send`-Wrapper
  in den Response-Header.
- `app/middleware/security_headers.py` — `SecurityHeadersMiddleware` als reine
  ASGI-Middleware; Header-Injektion in `http.response.start`.
- `app/middleware/audit_middleware.py` — `AuditMiddleware` als reine ASGI-Middleware;
  loggt weiterhin nur mutierende Methoden; liest User/Tenant/Correlation aus
  `request.state`/Scope mit Header-Fallback.
- `main.py` — `enforce_bearer_token` → `BearerAuthMiddleware` (pure ASGI, gleiche
  OPTIONS-/CORS-/401-/Tenant-Semantik); `log_requests` → `RequestLoggingMiddleware`
  (pure ASGI; loggt nur Slow-Requests > 1 s und Fehler, kein Pro-Request-Doppellog).
- `scripts/benchmark_middleware_stack.py` — reproduzierbarer Micro-Benchmark.
- `tests/test_middleware_asgi.py` — Verifikation Security-Header, Correlation-ID,
  Audit-nur-bei-Mutation, unveränderte Response-Bodies, `_simplify_path`.

## Bewusste Entscheidungen / Grenzen

- **Bearer-Auth wurde mit umgestellt** (anders als im ursprünglichen
  konservativen Plan), da sie als verbleibende `BaseHTTPMiddleware` denselben
  Overhead behalten hätte. Verhalten ist 1:1 erhalten (durch
  `tests/test_auth_middleware.py` + `tests/test_tenant_enforcement.py` belegt).
- **DB-Pool/Threadpool unverändert:** `pool_size=40, max_overflow=5,
  pool_timeout=10, pool_pre_ping=True` (≈ 360 Connections bei 8 Workern, PG
  `max_connections=400`) und Threadpool-Limit 200 sind bereits passend
  dimensioniert. Eine Erhöhung würde PG-Connection-Erschöpfung riskieren —
  daher keine Änderung.
- **Reduziertes Logging:** Normale Requests werden nicht mehr pro Stück geloggt
  (Prometheus erfasst Durchsatz/Latenz). Sichtbar bleiben Fehler (5xx) und
  Slow-Requests > 1 s. Schwelle ist in `RequestLoggingMiddleware` konfigurierbar.

## Verifikation

```
python -m py_compile main.py app/middleware/metrics.py app/middleware/correlation.py app/middleware/security_headers.py app/middleware/audit_middleware.py
pytest -q -o addopts= tests/test_middleware_asgi.py
pytest -q -o addopts= tests/test_auth_middleware.py tests/test_tenant_enforcement.py tests/test_process_kernel_wave75_security_hardening.py
python scripts/benchmark_middleware_stack.py
```

Ergebnis: `test_middleware_asgi` 6/6 grün; Auth/Tenant/Security 75/75 grün;
Benchmark belegt Overhead-Reduktion.
