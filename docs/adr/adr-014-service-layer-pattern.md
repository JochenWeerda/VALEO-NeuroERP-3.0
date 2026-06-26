# ADR-014: Service-Layer-Pattern (BaseRepository + DomainService)

**Status:** Accepted
**Datum:** 2026-05-27
**Kontext:** Wave E — Developer Experience

---

## Kontext

Die Codebasis enthielt über 30 Endpoint-Dateien mit >1.000 LOC, in denen Routing-Logik, Datenbankzugriffe und Geschäftslogik direkt gemischt waren. Dies führte zu schlechter Testbarkeit, hoher Kopplung und schwieriger Wartung.

## Entscheidung

Alle Mutation-Pfade und komplexe Abfragen werden in dedizierten **Service-Klassen** und **Repository-Klassen** extrahiert. Die Schichtung ist:

```text
Router (FastAPI)  →  DomainService  →  BaseRepository  →  SQLAlchemy / DB
```

### BaseRepository (Generisch)

```python linenums="0"
# app/core/repository.py — vereinfachtes Muster
class BaseRepository(Generic[T]):
    def get(self, id: str) -> T | None: ...
    def list(self, skip: int = 0, limit: int = 50) -> tuple[list[T], int]: ...
    def save(self, entity: T) -> T: ...
```

### DomainService-Konvention

- Service-Klassen liegen in `app/services/<domain>_service.py`
- Kein FastAPI-Coupling in Services (keine `Request`, `HTTPException` in Service-Methoden)
- Services erhalten `db: Session` und `tenant_id: str` via Dependency Injection
- Fehler werden als Domain-Exceptions (`EntityNotFoundError`, `ConflictError`) geworfen, die der Router in HTTP-Responses übersetzt

### Endpoint-Handler-Pattern

```python
# Endpoint-Handler bleibt schlank:
@router.get("/{id}", response_model=ItemOut)
async def get_item(id: str, svc: ItemService = Depends(get_item_service)):
    item = svc.get(id)
    if not item:
        raise HTTPException(404, "Not found")
    return item
```

## Konsequenzen

**Positiv:**
- Endpoint-Dateien bleiben unter 500 LOC
- Business-Logik ist isoliert testbar (ohne HTTP-Kontext)
- Konsistente Rollback-Behandlung in Services

**Negativ:**
- Mehr Dateien pro Domäne
- Initiale Extraktion bestehender Godfiles ist aufwändig

## Referenz

- `app/core/repository.py` — BaseRepository-Implementierung
- `app/services/agrar_contract_service.py` — Beispiel-Implementierung (403 LOC → 196 LOC Endpoint)
- `app/services/procurement_service.py` — ProcurementService (1407 LOC → 741 LOC Endpoint)
