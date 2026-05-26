# VALEO NeuroERP — ERP Quality Assessment & Roadmap

**Stand:** 2026-05-26
**Scope:** Backend (Python/FastAPI), Frontend (React/TypeScript), Infra, Tests
**Referenz:** SAP S/4HANA, Oracle Fusion Cloud ERP, Microsoft Dynamics 365
**Ziel:** Enterprise-Grade ERP — vergleichbar mit marktführenden ERP-Suites

---

## 1. Qualitätsstandards für Enterprise ERP (Soll-Definition)

### 1.1 Sicherheit (Security)
| Dimension | SAP/Oracle Standard | Messgröße |
|-----------|--------------------|-----------|
| SQL Injection | 0 dynamische SQL-Strings; ausschließlich parametrisierte Queries | 0 f-strings in text() |
| Authentifizierung | Jeder Endpoint explizit durch Auth-Dependency geschützt | 100% Coverage |
| Mandantentrennung | Jeder Datenzugriff durch tenant_id gefiltert; Middleware + Row-Level | 0 ungeschützte Routes |
| Secrets | Keine Hardcoding; ausschließlich Vault / Env-Variablen | 0 Hardcoded |
| Input Validation | Pydantic-Schemas auf 100% der Request-Bodies | 100% |
| OWASP Top 10 | Vollständig adressiert | Audit-Bericht jährlich |

### 1.2 Zuverlässigkeit & Datenintegrität
| Dimension | SAP/Oracle Standard | Messgröße |
|-----------|--------------------|-----------|
| Transaktionen | Jede Mutation in expliziter DB-Transaktion mit Rollback | 100% |
| Idempotenz | Alle POST-Mutations mit Idempotenz-Key | Critical paths 100% |
| Fehlerbehandlung | Kein `except: pass`; jeder Fehler geloggt oder propagiert | 0 bare excepts |
| Audit Trail | GoBD-konforme Unveränderlichkeit aller Buchungsdaten | 100% Finanztransaktionen |
| Concurrency | Optimistic/Pessimistic Locking wo notwendig | 0 Lost-Update-Risiken |

### 1.3 Performance & Skalierbarkeit
| Dimension | SAP/Oracle Standard | Messgröße |
|-----------|--------------------|-----------|
| List-Endpoints | Cursor-Pagination auf allen List-Routen | 100% |
| DB-Indexes | Index auf allen FK-Spalten + häufigen Filterfeldern | Index Coverage >90% |
| N+1 Queries | Kein N+1; eager loading / joins | 0 N+1 in Hot Paths |
| Response-Zeit | P99 < 500ms für Standard-CRUD | SLO-Monitoring |
| Caching | Redis-Cache auf Stammdaten, Preislisten, Session | Hit Rate >80% auf Stammdaten |

### 1.4 Wartbarkeit & Code-Qualität
| Dimension | SAP/Oracle Standard | Messgröße |
|-----------|--------------------|-----------|
| Datei-Größe | Max. 500 LOC pro Datei (Separation of Concerns) | 0 Godfiles >1000 LOC |
| Typsicherheit | 100% Response-Models in FastAPI; `strict: true` + `noImplicitAny` in TS | 0% untyped |
| Docstrings | Public-API-Endpoints vollständig dokumentiert | >80% |
| Pydantic V2 | Keine deprecated `class Config`; ausschließlich `model_config` | 0 Violations |
| Zyklomatische Komplexität | Funktionen max. Komplexität 10 | <5% >10 |
| Duplikation | DRY; max. 3% Code-Duplikation | <3% |

### 1.5 Testabdeckung
| Dimension | SAP/Oracle Standard | Messgröße |
|-----------|--------------------|-----------|
| Unit Tests | >80% Coverage auf Business-Logik / Services | Coverage >80% |
| Integration Tests | Alle Endpoints mit Happy-Path + 3 Fehlerfällen | 100% Endpoints |
| E2E Tests | Alle kritischen Geschäftsprozesse (Order-to-Cash, Annahme, Abrechnung) | >30 E2E-Flows |
| Performance Tests | Lasttests für Spitzenlastszenarien (Erntekampagne) | k6/Locust Baseline |
| Regressionstests | Automatisch bei jedem Merge | CI-Gate |

### 1.6 API-Qualität & Versionierung
| Dimension | SAP/Oracle Standard | Messgröße |
|-----------|--------------------|-----------|
| Response-Models | Alle Endpoints mit typisiertem `response_model` | 100% |
| API-Versionierung | Stable v1, Breaking Changes nur in v2 | Versionierungspolicy |
| OpenAPI-Doku | Beschreibung + Tags + Beispiele auf 100% | Vollständig |
| Pagination | Standardisiertes `{items, total, skip, limit}` | 100% List-Endpoints |
| Fehler-Responses | RFC 7807 Problem Details Format | 100% |

### 1.7 Observability
| Dimension | SAP/Oracle Standard | Messgröße |
|-----------|--------------------|-----------|
| Structured Logging | JSON-Logs mit trace_id, tenant_id, user_id | 100% |
| Metriken | RED-Metrics (Rate, Errors, Duration) per Endpoint | Prometheus/Grafana |
| Distributed Tracing | OpenTelemetry mit Trace-ID durch alle Services | W3C TraceContext |
| Alerting | SLO-Alerts für kritische Pfade (<500ms, <0.1% Error-Rate) | PagerDuty/OpsGenie |
| Health Checks | `/health`, `/readiness`, `/liveness` mit DB/Redis/NATS | Kubernetes-ready |

---

## 2. Ist-Analyse VALEO NeuroERP (Stand 2026-05-26)

### 2.1 Metrik-Übersicht

| Kategorie | Metrik | Ist-Wert | Soll-Wert | Status |
|-----------|--------|----------|-----------|--------|
| **Codebase** | Backend LOC | 228.455 | — | — |
| **Codebase** | Test-Funktionen | 9.044 | — | — |
| **Codebase** | E2E Playwright Specs | 48 | >60 | 🟡 |
| **Sicherheit** | SQL f-String Injection Risk | 111 Zeilen | 0 | 🔴 |
| **Sicherheit** | Dynamische WHERE-Clauses | 57 | 0 | 🔴 |
| **Sicherheit** | Endpoints ohne Auth-Dependency | 304 von 311 Dateien | 0 | 🔴* |
| **Sicherheit** | Endpoints ohne Tenant-Filter | 44 Dateien | 0 | 🔴 |
| **Sicherheit** | Potenzielle Hardcoded Secrets | 5 | 0 | 🟡 |
| **Fehlerbehandlung** | `except Exception: pass` | 0 (gefixed) | 0 | 🟢 |
| **Fehlerbehandlung** | Commits ohne Rollback | 117 Dateien | 0 | 🔴 |
| **Typsicherheit** | Ungetypte API-Routes (%) | 37,3% (1.123 Routes) | 0% | 🔴 |
| **Typsicherheit** | Frontend `: any` / `as any` | 982 Vorkommen | <50 | 🔴 |
| **Typsicherheit** | TS `noImplicitAny` | false | true | 🔴 |
| **Wartbarkeit** | Dateien >1.000 LOC | 30 | 0 | 🔴 |
| **Wartbarkeit** | Größte Datei | 6.939 LOC (rations_optimization) | <500 LOC | 🔴 |
| **Wartbarkeit** | Endpoint-Docstrings | 13% (350/2.705) | >80% | 🔴 |
| **Skalierbarkeit** | List-Endpoints ohne Pagination | 97 | 0 | 🔴 |
| **Skalierbarkeit** | DB-Index-Definitionen | 127 | >300 | 🟡 |
| **Skalierbarkeit** | Circuit Breaker | 5 Dateien | >20 | 🟡 |
| **Datenintegrität** | Alembic Migrationen | 185 | — | 🟢 |
| **Datenintegrität** | Pydantic V2 ConfigDict | 100% (0 Violations) | 100% | 🟢 |
| **API-Qualität** | OpenAPI Tags | 241/311 Dateien | 100% | 🟡 |
| **API-Qualität** | Endpoint-Beschreibungen | 154/311 Dateien | 100% | 🔴 |

*Auth wird durch `require_bearer_token` per-Dependency gelöst, nicht Middleware-global — siehe §2.2.

### 2.2 Detailbefunde

#### Sicherheit — Auth-Enforcement
`require_bearer_token` ist FastAPI-Dependency, nicht globale Middleware. Das bedeutet: Endpoints, die die Dependency **nicht explizit deklarieren**, sind de facto ungeschützt. Die 304 Endpoint-Dateien ohne explizite Auth-Dependency sind ein **kritisches Sicherheitsrisiko** — auch wenn viele davon möglicherweise durch Netzwerk-/Reverse-Proxy-Kontrollen de-facto geschützt sind.

**Wichtig:** `TenantEnforcementMiddleware` im Code ist nur ein ContextVar-Setter — kein echter Schutz. Ohne DB-Level Row Security oder konsequente `tenant_id`-Filter in jedem Query kann cross-tenant Datenzugriff stattfinden.

#### SQL Injection
111 Zeilen mit f-Strings in `text()` oder `execute()`:
```python
# Beispiel - SQL Injection Risk:
text(f"SELECT * FROM {table} WHERE tenant_id = '{tenant_id}'")
# Korrekt:
text("SELECT * FROM :table WHERE tenant_id = :tid")
```
Die 57 dynamischen WHERE-Clauses sind besonders kritisch, da sie direkt Benutzereingaben in SQL einfügen können.

#### Godfiles (>1.000 LOC)
| Datei | LOC | Problem |
|-------|-----|---------|
| `rations_optimization.py` | 6.939 | Komplette Anwendungslogik in einem Endpoint-File |
| `process_kernel_api.py` | 5.982 | Process Engine + API gemischt |
| `personal.py` | 4.357 | HR-Domäne komplett inline |
| `compat.py` | 3.281 | Legacy-Compat ohne Struktur |
| `business_partners.py` | 2.716 | CRM ohne Service-Layer |
| ... | ... | 25 weitere >1.000 LOC |

#### Response-Model-Lücken
37,3% aller 3.012 API-Routes haben kein `response_model`. Das bedeutet:
- Keine automatische Serialisierungs-Validierung
- Keine OpenAPI-Dokumentation des Response-Schemas
- Keine Typsicherheit zwischen Backend und Frontend

#### Frontend TypeScript-Qualität
982 `any`-Verwendungen trotz aktiviertem `strict: true` (aber `noImplicitAny: false`). Faktisch läuft das Frontend ohne vollständige Typprüfung auf Rückgabewerte.

---

## 3. Roadmap: Von Ist zu SAP/Oracle-Niveau

### Übersicht — 5 Wellen à ~4-6 Wochen

```
Wave A  Security Hardening          (Kritisch — sofort)
Wave B  Data Integrity & Typing     (Hoch — 4 Wochen)
Wave C  Scalability & Performance   (Mittel — 8 Wochen)
Wave D  Observability & Ops         (Mittel — 12 Wochen)
Wave E  Developer Experience        (Kontinuierlich)
```

---

### Wave A — Security Hardening (Wochen 1–4) 🔴 KRITISCH

**Ziel:** Alle kritischen Sicherheitslücken schließen.

#### A1 — SQL Injection eliminieren (111 Zeilen)
```python
# Vorher (unsicher):
db.execute(text(f"SELECT * FROM {schema}.{table} WHERE id = '{id}'"))
# Nachher (sicher):
db.execute(text("SELECT * FROM domain_agrar.lots WHERE id = :id"), {"id": id})
```
- Alle 111 f-String-SQL-Stellen auf parametrisierte Queries umstellen
- Linter-Regel `S608` (Bandit) als CI-Gate einführen
- **Aufwand:** 3–5 Tage | **Risiko wenn nicht gemacht:** kritisch

#### A2 — Auth-Dependency auf alle Endpoints (304 Dateien)
Zwei Ansätze — **Ansatz 1 bevorzugt** (geringere Fehleranfälligkeit):
```python
# api.py: Globale Dependency auf alle Sub-Router
api_router.include_router(
    agrar_contracts.router,
    dependencies=[Depends(require_bearer_token)]  # ← einmalig hier
)
```
Alternativ: FastAPI `app.dependency_overrides` oder Router-Level `dependencies=`.

- Alle 311 Endpoint-Router-Includes in `api.py` mit `dependencies=[Depends(require_bearer_token)]` versehen
- Public-Endpoints (Health, OpenAPI) explizit exemptieren
- **Aufwand:** 2 Tage | **Risiko:** kritisch

#### A3 — Tenant-Isolation härtеn (44 Dateien)
- Alle Endpoints ohne `tenant_id` auf Notwendigkeit prüfen
- Admin-Endpoints: RBAC-Check statt Tenant-Filter
- Optional: PostgreSQL Row-Level Security als zweite Verteidigungslinie
- **Aufwand:** 1 Woche

#### A4 — Hardcoded Secrets beseitigen (5 Stellen)
- Audit mit `detect-secrets` / `truffleHog`
- Alle gefundenen Credentials in `.env` / Vault migrieren
- `detect-secrets` als pre-commit Hook
- **Aufwand:** 1 Tag

**Meilenstein A:** `bandit -r app/ --severity-level high` = 0 Findings

---

### Wave B — Data Integrity & Typing (Wochen 3–8) 🟠 HOCH

#### B1 — Rollback auf alle Mutation-Pfade (117 Dateien)
```python
# Pattern: Jede Mutation in try/except mit Rollback
try:
    db.add(entity)
    db.commit()
    db.refresh(entity)
except Exception:
    db.rollback()
    raise
```
- Alle 117 Endpoint-Dateien mit `db.commit()` aber ohne Rollback nachrüsten
- Service-Layer-Extraktion (B3) macht dies einfacher — koordinieren
- **Aufwand:** 1 Woche

#### B2 — Response-Models auf 100% (1.123 ungetypte Routes)
Priorisierung:
1. Finanz-Endpoints (Rechnungen, Buchungen, Zahlungen) — 100%
2. Agrar-Kern-Endpoints (Annahme, Kontrakte, Abrechnungen) — 100%
3. CRM/Verkauf — 80%
4. Admin/Monitoring — 60%

```python
# Vorher:
@router.get("/invoices")
def list_invoices(): ...

# Nachher:
@router.get("/invoices", response_model=list[InvoiceOut])
def list_invoices() -> list[InvoiceOut]: ...
```
- **Aufwand:** 2–3 Wochen (kann parallelisiert werden)

#### B3 — Service-Layer Vollständigkeit (Godfiles aufbrechen)
Priorisierung nach Komplexität und Risiko:
1. `process_kernel_api.py` (5.982 LOC) → `ProcessKernelService`
2. `personal.py` (4.357 LOC) → `PersonalService` (teilweise vorhanden)
3. `compat.py` (3.281 LOC) → `PosCompatService`, `CrmCompatService`
4. `business_partners.py` (2.716 LOC) → `BusinessPartnerService`
5. `rations_optimization.py` (6.939 LOC) → `RationsService` + `NutritionEngine`

Ziel: Max. 500 LOC pro Datei, klare Trennung Route Handler / Service / Repository.
- **Aufwand:** 4–6 Wochen (in Scheiben aufteilen)

#### B4 — Frontend TypeScript verschärfen
```json
// tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,      // ← aktivieren
    "strictNullChecks": true,
    "noUncheckedIndexedAccess": true  // ← aktivieren
  }
}
```
- `noImplicitAny` aktivieren
- Alle 982 `any`-Verwendungen systematisch typisieren
- **Aufwand:** 2–3 Wochen (iterativ, file-by-file)

**Meilenstein B:** `mypy app/ --strict` < 100 Errors; TS-Build 0 Errors mit `noImplicitAny`

---

### Wave C — Scalability & Performance (Wochen 6–12) 🟡 MITTEL

#### C1 — Cursor-Pagination auf alle List-Endpoints (97 fehlen)
```python
# Standard-Pattern für alle List-Routes:
@router.get("/items", response_model=PaginatedResponse[ItemOut])
def list_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    query = db.query(ItemDB).filter(ItemDB.tenant_id == tenant_id)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return {"items": items, "total": total, "skip": skip, "limit": limit}
```
- Generic `PaginatedResponse[T]` einführen (bereits partiell vorhanden)
- Alle 97 unpagierten List-Endpoints nachrüsten
- **Aufwand:** 1–2 Wochen

#### C2 — DB-Index-Strategie (fehlen mindestens 173 Indexes)
Priorität:
```sql
-- Beispiele fehlender Indexes:
CREATE INDEX idx_harvest_acceptance_tenant_date ON harvest_acceptance(tenant_id, created_at);
CREATE INDEX idx_invoices_tenant_status ON invoices(tenant_id, status, due_date);
CREATE INDEX idx_articles_tenant_active ON articles(tenant_id, active) WHERE active = true;
```
- Index-Audit mit `pg_stat_user_indexes` auf Live-DB
- Alembic-Migration für fehlende Indexes
- **Aufwand:** 1 Woche

#### C3 — N+1 Query Elimination
- SQLAlchemy Eager Loading (`joinedload`, `selectinload`) auf alle Relationships die in List-Endpoints geladen werden
- Query-Logging in Dev-Mode mit `SQLALCHEMY_ECHO=true`
- **Aufwand:** 2 Wochen

#### C4 — Cache-Strategie ausbauen
```python
# Redis-Caching auf Stammdaten:
@cache(ttl=300, key="articles:{tenant_id}")
def get_article_catalog(tenant_id: str) -> list[ArticleOut]: ...
```
- Preislisten, Artikelstamm, Variantenkonfiguration cachen
- Cache-Invalidierung bei Mutations sicherstellen
- **Aufwand:** 1 Woche

**Meilenstein C:** P99 Response-Zeit < 500ms auf Standard-CRUD (Baseline: k6-Lasttest)

---

### Wave D — Observability & Ops (Wochen 10–16) 🟡 MITTEL

#### D1 — Structured Logging vereinheitlichen
```python
# Jeder Log-Eintrag enthält:
logger.info("Ernte-Annahme erstellt", extra={
    "trace_id": request.headers.get("X-Trace-ID"),
    "tenant_id": tenant_id,
    "user_id": user_id,
    "entity_id": str(annahme.id),
    "duration_ms": elapsed,
})
```
- JSON-Formatter auf alle Logger
- `trace_id` als ContextVar durch alle Service-Aufrufe propagieren
- **Aufwand:** 1 Woche

#### D2 — OpenAPI-Dokumentation vervollständigen (87% fehlen)
```python
@router.post(
    "/annahme",
    response_model=AnnahmeOut,
    summary="Ernte-Annahme erfassen",
    description="Erfasst eine neue Ernte-Annahme mit Qualitäts- und Mengendaten.",
    responses={
        201: {"description": "Annahme erfolgreich erstellt"},
        422: {"description": "Validierungsfehler"},
    },
    tags=["Agrar — Annahme"],
)
```
- Docstrings und OpenAPI-Metadaten auf alle 2.355 undokumentierten Funktionen
- Automatisierbar mit Code-Generator für Boilerplate
- **Aufwand:** 2–3 Wochen

#### D3 — RFC 7807 Problem Details Format
```python
# Standardisiertes Fehlerformat für alle 4xx/5xx:
{
  "type": "https://valeo-erp.de/errors/validation-failed",
  "title": "Validierungsfehler",
  "status": 422,
  "detail": "Menge darf nicht negativ sein",
  "instance": "/api/v1/agrar/annahme/abc123",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736"
}
```
- Exception-Handler in `main.py` auf RFC 7807 umstellen
- **Aufwand:** 2 Tage

#### D4 — Performance-Baseline & SLO-Monitoring
- k6-Lasttest-Suite für Kernanwendungsfälle (Ernte-Annahme, Rechnung, Kontrakt)
- Prometheus-Metriken + Grafana-Dashboard
- Alerting auf Error-Rate > 0.1%, P99 > 500ms
- **Aufwand:** 1 Woche

**Meilenstein D:** Vollständige OpenAPI-Doku; SLO-Monitoring aktiv; strukturiertes Logging

---

### Wave E — Developer Experience (Kontinuierlich)

#### E1 — CI/CD Quality Gates (sofort einführen)
```yaml
# .github/workflows/quality.yml
- name: Security scan
  run: bandit -r app/ -ll  # Severity HIGH+
- name: SQL injection check
  run: python scripts/check_sql_fstrings.py  # 0 = pass
- name: Type check backend
  run: mypy app/ --ignore-missing-imports
- name: Type check frontend
  run: pnpm type-check
- name: Test suite
  run: pytest --no-cov -q  # 0 failed
- name: Playwright E2E
  run: playwright test --project=chromium
```

#### E2 — Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/PyCQA/bandit
    hooks: [bandit]
  - repo: https://github.com/Yelp/detect-secrets
    hooks: [detect-secrets]
  - repo: https://github.com/pre-commit/mirrors-mypy
    hooks: [mypy]
```

#### E3 — Architecture Decision Records (ADRs)
- ADR-001: Service-Layer-Pattern (BaseRepository + DomainService)
- ADR-002: Auth-Enforcement-Strategie (Dependency vs. Middleware)
- ADR-003: Pagination-Standard (`PaginatedResponse[T]`)
- ADR-004: Error-Response-Format (RFC 7807)

---

## 4. Priorisierte Backlog-Liste

| Priorität | ID | Maßnahme | Aufwand | Impact |
|-----------|-----|----------|---------|--------|
| P0 🔴 | A2 | Auth-Dependency auf alle Endpoints | 2 Tage | Kritisch |
| P0 🔴 | A1 | SQL Injection (111 Zeilen) eliminieren | 5 Tage | Kritisch |
| P0 🔴 | B1 | Rollback auf alle Mutation-Pfade | 1 Woche | Hoch |
| P1 🟠 | A3 | Tenant-Isolation härten (44 Dateien) | 1 Woche | Hoch |
| P1 🟠 | C1 | Pagination auf 97 List-Endpoints | 2 Wochen | Hoch |
| P1 🟠 | B2 | Response-Models 37% → 100% | 3 Wochen | Mittel |
| P1 🟠 | B3 | Godfiles aufbrechen (30 Dateien) | 6 Wochen | Hoch |
| P2 🟡 | B4 | TS noImplicitAny + 982 any-fixes | 3 Wochen | Mittel |
| P2 🟡 | C2 | DB-Index-Audit + fehlende Indexes | 1 Woche | Hoch |
| P2 🟡 | D3 | RFC 7807 Fehlerformat | 2 Tage | Mittel |
| P2 🟡 | D1 | Structured Logging (trace_id) | 1 Woche | Mittel |
| P2 🟡 | E1 | CI/CD Quality Gates | 3 Tage | Hoch |
| P3 🟢 | C3 | N+1 Query Elimination | 2 Wochen | Mittel |
| P3 🟢 | D2 | OpenAPI-Doku vervollständigen | 3 Wochen | Niedrig |
| P3 🟢 | D4 | Performance-Baseline & SLO | 1 Woche | Mittel |
| P3 🟢 | C4 | Cache-Strategie ausbauen | 1 Woche | Mittel |

---

## 5. Vergleich: Ist vs. SAP/Oracle-Niveau

| Dimension | SAP S/4HANA | VALEO Ist | VALEO Soll (nach Roadmap) |
|-----------|-------------|-----------|--------------------------|
| SQL Injection | 0 | 111 Risiken | 0 |
| Auth Coverage | 100% | ~5% explizit | 100% |
| Response-Typing | 100% | 62,7% | 100% |
| Pagination | 100% | ~85% | 100% |
| Rollback-Pattern | 100% | ~60% | 100% |
| Godfiles >1k LOC | 0 | 30 | 0 |
| Test-Funktionen | >50k | 9.044 | 15.000+ |
| Structured Logging | 100% | ~60% | 100% |
| OpenAPI-Doku | 100% | 13% Docstrings | >80% |
| TypeScript strict | 100% | 78% | 100% |
| **Gesamtreife** | **Produktionsreif** | **~55%** | **>90%** |

---

## 6. Nächste Schritte (sofort)

1. **Diese Woche:** Wave A starten — Auth-Dependency (A2) ist 2-Tages-Aufgabe mit maximalem Sicherheits-Impact
2. **Parallel:** SQL-Injection-Scan verfeinern, alle 57 dynamischen WHERE-Clauses auflisten
3. **CI/CD:** Quality Gates (E1) einrichten, damit keine neuen Verstöße eingeführt werden
4. **Tracking:** Dieses Dokument als lebendige Roadmap führen — Fortschritt per Wave dokumentieren

---

*Dokument generiert durch automatische Codebase-Analyse + manuelle Architektur-Review.*
*Referenzstandards: SAP Clean Core, Oracle Fusion Architecture Principles, OWASP ASVS Level 2.*
