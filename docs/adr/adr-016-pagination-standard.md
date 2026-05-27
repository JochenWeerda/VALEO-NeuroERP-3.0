# ADR-016: Pagination-Standard (PaginatedResponse[T])

**Status:** Accepted
**Datum:** 2026-05-27
**Kontext:** Wave C1 — Scalability

---

## Kontext

97 List-Endpoints lieferten `.all()` ohne Paginierung — bei wachsenden Datenmengen führt das zu Speicher- und Latensproblemen. Unterschiedliche Endpoints verwendeten verschiedene Formate (`items/data/results`, `total/count`).

## Entscheidung

Alle List-Endpoints verwenden das standardisierte `PaginatedResponse[T]`-Schema:

```python
# app/api/v1/schemas/base.py
from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    skip: int
    limit: int
```

### Endpoint-Pattern

```python
@router.get("/", response_model=PaginatedResponse[ItemOut])
async def list_items(
    skip: int = Query(0, ge=0, description="Offset"),
    limit: int = Query(50, ge=1, le=500, description="Max. Ergebnisse"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> PaginatedResponse[ItemOut]:
    query = db.query(ItemDB).filter(ItemDB.tenant_id == tenant_id)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return PaginatedResponse(items=items, total=total, skip=skip, limit=limit)
```

### Grenzwerte

| Parameter | Default | Min | Max |
|-----------|---------|-----|-----|
| `skip`    | 0       | 0   | —   |
| `limit`   | 50      | 1   | 500 |

### Cursor-Pagination (für sehr große Datasets)

Für Tabellen >1M Rows wird Cursor-Pagination mit `after_id` bevorzugt:

```python
@router.get("/", response_model=CursorPaginatedResponse[ItemOut])
async def list_items(after_id: str | None = None, limit: int = Query(50)):
    query = db.query(ItemDB).filter(ItemDB.tenant_id == tenant_id)
    if after_id:
        query = query.filter(ItemDB.id > after_id)
    items = query.order_by(ItemDB.id).limit(limit + 1).all()
    has_more = len(items) > limit
    return CursorPaginatedResponse(items=items[:limit], next_cursor=items[-1].id if has_more else None)
```

## CI-Gate

`scripts/check_pagination.py` zählt `.all()`-Aufrufe ohne vorherigen `.limit()` und scheitert ab Threshold.

## Konsequenzen

**Positiv:**
- Konsistentes Frontend-Parsing (immer `response.items`, `response.total`)
- Vorhersehbarer Speicherbedarf
- Einfache Cursor-basierte Weiterentwicklung

**Negativ:**
- Migration bestehender Endpoints erfordert API-Version-Bump bei Breaking Changes
- `total` ist teuer bei großen Tabellen → für Cursor-Pagination entfällt es

## Referenz

- `app/api/v1/schemas/base.py` — `PaginatedResponse[T]`
- `scripts/check_pagination.py` — CI-Gate
- `.github/workflows/quality-gate.yml` — `check_pagination.py --threshold 60`
