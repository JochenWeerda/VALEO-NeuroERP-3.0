# VALEO NeuroERP — Architekturstandards

**Stand:** 2026-05-28 | **Gültig für:** alle neuen und migrierten Endpoints

---

## 1. Prinzipien

1. **Systemweite Konsistenz vor lokaler Lösung** — gemeinsame Basisklassen statt Inline-Duplikat.
2. **Starke Typen überall** — kein `response_model=dict/list/Any` in Produktion.
3. **Rückwärtskompatibilität** — Schema-Änderungen dürfen keine laufenden Clients brechen.
4. **Testbarkeit** — jeder Endpoint hat einen direkten Testpfad.
5. **Mandantensicherheit** — `tenant_id` wird nie aus dem Request-Body akzeptiert, immer aus dem Auth-Kontext.

---

## 2. API-Response-Schemas

Alle Response-Schemas importieren aus `app.api.v1.schemas.base`.

### 2.1 Standard-Response-Typen

| Zweck | Klasse | Verwendung |
|---|---|---|
| Einfache Operation (Delete, Trigger) | `StatusResponse` | `return StatusResponse(success=True, message="Gelöscht")` |
| Create → neue ID | `IDResponse` | `return IDResponse(id=str(obj.id))` |
| Anzahl | `CountResponse` | `return CountResponse(count=n)` |
| Liste ohne Pagination | `ListResponse[T]` | `return ListResponse(items=rows, total=len(rows))` |
| Pagination (Offset/Limit) | `OffsetPaginatedResponse[T]` | `return OffsetPaginatedResponse(items=rows, total=n, limit=l, offset=o)` |
| Pagination (Page/Size) | `PaginatedResponse[T]` | `return PaginatedResponse(items=rows, total=n, page=p, size=s, pages=pages, ...)` |
| Bulk-Import | `BulkOperationResponse` | `return BulkOperationResponse(success_count=ok, error_count=err, errors=[...])` |
| Fehler (HTTP-Exceptions) | `ErrorResponse` | Wird automatisch via RFC-7807-Middleware erzeugt |

### 2.2 Anti-Patterns (verboten)

```python
# VERBOTEN
response_model=dict
response_model=list
response_model=Any
response_model=dict[str, Any]
response_model=Dict[str, Any]
response_model=list[dict]

# ERLAUBT
response_model=StatusResponse
response_model=IDResponse
response_model=ListResponse[MySchema]
response_model=OffsetPaginatedResponse[MySchema]
response_model=MyDomainSchema
```

CI-Check: `python scripts/check_weak_response_models.py`

### 2.3 Eigene Domain-Schemas

Eigene Schemas erben von `BaseSchema` (oder einem Mixin):

```python
from app.api.v1.schemas.base import BaseSchema, TimestampMixin, TenantMixin, AuditMixin

class KontraktOut(BaseSchema, TimestampMixin):
    id: str
    nummer: str
    artikel: str
    menge: float
    preis: float
    tenant_id: str
```

**Wo definieren?** In `app/api/v1/schemas/<domain>.py` — nicht inline im Endpoint.

---

## 3. Fehlerbehandlung

VALEO nutzt **RFC-7807 Problem Details** (`application/problem+json`). Alle HTTP-Fehler werden durch die globale `ExceptionHandlerMiddleware` vereinheitlicht.

### 3.1 In Endpoints

```python
# KORREKT — HTTPException, Middleware formatiert RFC-7807
raise HTTPException(status_code=404, detail="Kontrakt nicht gefunden")

# KORREKT — DomainError Hierarchie (app/core/exceptions.py)
raise EntityNotFoundError("Kontrakt", kontrakt_id)

# VERBOTEN — direkte dict-Antwort
return {"error": "Kontrakt nicht gefunden"}       # ❌
return JSONResponse({"detail": "..."}, status_code=404)  # ❌ (außer Sonderfälle)
```

### 3.2 DomainError-Hierarchie

```python
from app.core.exceptions import (
    EntityNotFoundError,   # → 404
    ConflictError,         # → 409
    ValidationFailedError, # → 422
    ForbiddenError,        # → 403
)
```

### 3.3 Error-Handling in Endpoints

Jede user-getriggerte Mutation muss bei Fehler sichtbares Feedback liefern (CLAUDE.md Invariante):
- Backend: `raise HTTPException` oder `raise DomainError`
- Frontend: `toast()`, `setError()` oder `throw`

---

## 4. Naming-Konventionen

### 4.1 Endpoint-Dateien

Format: `<domain>_<ressource>.py` (snake_case, immer Unterstrichen)

| Domain | Dateiname-Beispiel |
|---|---|
| Agrar | `agrar_feldbuch.py`, `agrar_contracts.py` |
| Finance | `finance_actions.py`, `journal_entries.py` |
| Einkauf | `einkauf_bestellvorschlag.py` |
| Sales | `sales_orders.py`, `sales_invoice_einvoice.py` |

### 4.2 Router-Prefixes

```python
router = APIRouter(prefix="/agrar/feldbuch", tags=["agrar", "feldbuch"])
router = APIRouter(prefix="/finance/actions", tags=["finance"])
```

Format: `/<domain>/<ressource>` (Kebab-Case bei mehrteiligen Ressourcen)

### 4.3 Schema-Klassen

| Zweck | Suffix | Beispiel |
|---|---|---|
| API-Output | `Out` oder `Response` | `KontraktOut`, `SiloStatusResponse` |
| API-Input (Create) | `Create` | `KontraktCreate` |
| API-Input (Update) | `Update` | `KontraktUpdate` |
| Internes Daten-Transfer | `DTO` | `KontraktDTO` |
| SQLAlchemy-Model | ohne Suffix | `Kontrakt` (in `infrastructure/models/`) |

### 4.4 Endpoint-Funktionen

```python
# KORREKT — Verb + Domänenobjekt
def list_kontrakte(...)   → GET /kontrakte
def get_kontrakt(...)     → GET /kontrakte/{id}
def create_kontrakt(...)  → POST /kontrakte
def update_kontrakt(...)  → PUT /kontrakte/{id}
def delete_kontrakt(...)  → DELETE /kontrakte/{id}

# Aktionen (nicht CRUD)
def approve_kontrakt(...)  → POST /kontrakte/{id}/approve
def release_kontrakt(...)  → POST /kontrakte/{id}/release
```

---

## 5. Mandantenfähigkeit

**Invariante:** `tenant_id` wird **niemals** aus dem Request-Body gelesen. Immer aus:
```python
tenant_id: str = Depends(get_tenant_id)  # Header X-Tenant-ID
```

**SQL-Filter:** Jede Query filtert auf `WHERE tenant_id = :tenant_id`.

**CI-Gate:** `scripts/check_tenant_isolation.py`

---

## 6. Service-Layer

### 6.1 Struktur

```
app/
├── api/v1/endpoints/   → Thin Router (HTTP-Layer): Validierung, Auth-Checks, HTTP-Fehler
├── services/           → Service-Klassen: Fachlogik, keine HTTP-Konzepte
├── core/repository.py  → BaseRepository: Generischer DB-Zugriff mit Tenant-Filter
└── infrastructure/models/ → SQLAlchemy-Modelle
```

### 6.2 Endpoint vs. Service

```python
# Endpoint — nur HTTP-Schicht
@router.post("/{id}/approve", response_model=StatusResponse)
def approve_kontrakt(
    id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> StatusResponse:
    try:
        service = KontraktService(db, tenant_id)
        service.approve(id)
        return StatusResponse(success=True, message="Freigegeben")
    except EntityNotFoundError as e:
        raise HTTPException(404, str(e)) from e

# Service — Fachlogik
class KontraktService:
    def approve(self, id: str) -> None:
        kontrakt = self._repo.get_or_raise(id)
        if kontrakt.status != "ENTWURF":
            raise ConflictError(f"Kontrakt {id} ist nicht im Status ENTWURF")
        kontrakt.status = "FREIGEGEBEN"
        self._db.commit()
```

### 6.3 Verboten im Service

- Kein `HTTPException` im Service — nur `DomainError`
- Kein `Response`-Objekt im Service
- Kein `Depends()` im Service

---

## 7. Test-Standards

### 7.1 Struktur

```python
# tests/test_<endpoint_dateiname>.py
class TestKontraktEndpoints:
    def test_list_kontrakte_returns_list_response(self, client):
        """GET /kontrakte gibt ListResponse zurück"""
        response = client.get("/api/v1/kontrakte", headers=TENANT_HEADERS)
        assert response.status_code == 200
        body = response.json()
        assert "items" in body
        assert "total" in body

    def test_get_kontrakt_not_found_returns_404(self, client):
        """GET /kontrakte/{id} gibt 404 für unbekannte ID"""
        response = client.get("/api/v1/kontrakte/NONEXISTENT", headers=TENANT_HEADERS)
        assert response.status_code == 404
```

### 7.2 Pflichtfälle pro Endpoint

1. Happy Path (200/201)
2. Not Found (404) bei GET/{id} und DELETE/{id}
3. Tenant-Isolation (403 oder leere Liste bei falschem Tenant)
4. Validierungsfehler (422) bei fehlenden Pflichtfeldern

---

## 8. Logging & Audit

```python
import logging
logger = logging.getLogger(__name__)

# Strukturiertes Logging
logger.info("kontrakt_approved", extra={"kontrakt_id": id, "tenant_id": tenant_id})
logger.warning("sync_failed", extra={"service": "proplanta", "reason": str(e)})
logger.error("unexpected_error", exc_info=True)
```

Audit-Trails für Mutationen: `app/core/audit_middleware.py` schreibt automatisch.

---

## 9. CI-Gates (Architektur-Checks)

| Check | Script | Was wird geprüft |
|---|---|---|
| Schwache Response-Typen (strict) | `scripts/check_weak_response_models.py` | `response_model=dict/list/Any` → Ziel: 0 |
| CompatFlexOut-Ratchet | `scripts/check_weak_response_models.py --compat-flex` | Transitional open schema → Ratchet senken |
| Fehlende `summary=` | `scripts/check_response_models.py` | Alle Routes haben summary |
| SQL f-Strings | `scripts/check_sql_fstrings.py` | SQL-Injection-Risiko |
| Tenant-Isolation | CI-Gate in `.github/workflows/quality-gate.yml` | |
| Critical Coverage | `scripts/check_critical_backend_coverage.py` | 33 kritische Pfade |

---

## 10. Schema-Extraktion (Domain-Schema-Dateien)

**Prinzip:** Schemas die von Service-Layer und Endpoint-Layer gemeinsam genutzt werden, dürfen **nicht** im Endpoint inline definiert sein. Sie gehören in `app/api/v1/schemas/<domain>_schemas.py`.

### Wann extrahieren?

- Schema wird in einem Service importiert (→ circular import verhindert inline-Definition)
- Schema ist die Response-Basis für >3 Endpoints
- Schema repräsentiert ein fachlich stabiles Objekt (DTO-Vertrag)

### Beispiel: personal_schemas.py (Stand 2026-05-28)

```
app/api/v1/schemas/
├── base.py                  # Basis-Klassen (BaseSchema, ListResponse, CompatFlexOut, ...)
├── personal_schemas.py      # HRM-Domäne (HrmOperationsGateOut, EmployeeFileOut, ...)
└── <domain>_schemas.py      # weitere Domänen nach Bedarf
```

### Import-Konvention

```python
# Im Endpoint
from app.api.v1.schemas.personal_schemas import HrmOperationsGatesOut, EmployeeFileOut

# Im Service (korrekte Richtung: Service importiert Schemas, nicht umgekehrt)
from app.api.v1.schemas.personal_schemas import HrmOperationsGatesOut
```

### Architekturregeln

- **Erlaubt:** Service → Schema-Datei (schemas sind stabile Verträge)
- **Verboten:** Service → Endpoint-Datei (Endpoint ist HTTP-Layer)
- **Verboten:** Schema → Service (circular)
- Mapper-Funktionen (SQLAlchemy → Pydantic) gehören in den **Endpoint-Layer**, nicht in den Service

---

## 11. CompatFlexOut — Migrationspfad

`CompatFlexOut` ist ein **transitionales Schema** (`extra="allow"`, akzeptiert beliebige JSON-Felder).
Es wurde bei der Welle-D-Migration (2026-05-28) als Übergangsschritt zentralisiert.

### Stand 2026-05-28

- Baseline: **598 CompatFlexOut-Nutzungen** in 314 Endpoint-Dateien
- Zentralisiert in `app.api.v1.schemas.base.CompatFlexOut` (nicht mehr inline definiert)
- CI-Ratchet: `--compat-flex-threshold=598`

### Migrationsstrategie (Welle E+)

Für jeden Endpoint mit `response_model=CompatFlexOut`:

1. **Action-Endpoints** (POST Trigger, Status-Updates ohne Response-Body) → `StatusResponse`
2. **ID-Create-Endpoints** → `IDResponse`
3. **Detail-Endpoints** → echtes Pydantic-Schema in `app/api/v1/schemas/<domain>_schemas.py`
4. **List-Endpoints** → `list[EchtesSchema]` oder `ListResponse[EchtesSchema]`

**Ratchet senken:** Nach jeder Migrationswelle `--compat-flex-threshold` in `check_weak_response_models.py` verringern.

### Priorisierung nach fachlicher Bedeutung

| Priorität | Datei / Bereich | Begründung |
|---|---|---|
| P0 | `harvest_acceptance.py` | Kernprozess Ernte-Annahme |
| P0 | `agrar_settlements.py` | Abrechnung / Gutschrift (GoBD) |
| P0 | `sales_orders.py`, `sales_invoice_einvoice.py` | Verkauf / E-Rechnung |
| P1 | Finance-Domäne (journal_entries, financial_reports) | GoBD-Relevanz |
| P2 | `compat.py` Domain-Gruppen | PurchaseOrderOut → echte Felder |

---

## 12. Migrations-Ratchet — Verlauf

**Stand 2026-05-28: Literal dict/list/Any = 0 ✅ | CompatFlexOut = 598 (Basis)**

| Welle | Beschreibung | Threshold | Datum | Ergebnis |
|---|---|---|---|---|
| Baseline | Messung | 1451 | 2026-05-28 | CI-Gate eingerichtet |
| A | admin_mobile.py, compat.py | 1200 | 2026-05-28 | ✅ |
| B | process_kernel_api.py | 1000 | 2026-05-28 | ✅ |
| C | 50+ Dateien bulk | 500 | 2026-05-28 | ✅ |
| D | Restliche 260 Dateien | 0 | 2026-05-28 | ✅ Vollständige Typisierung (strict=0) |
| **D+** | **CompatFlexOut zentralisiert** | **598 (flex)** | **2026-05-28** | **Basis für Welle E** |
| E | Erste echte Feld-Schemas | TBD | TBD | Geplant |

**Fortschritt verfolgen:**
```bash
python scripts/check_weak_response_models.py            # strict: muss 0 bleiben
python scripts/check_weak_response_models.py --compat-flex  # flex: Ratchet senken
```
