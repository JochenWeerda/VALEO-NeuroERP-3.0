# ADR-017: Error-Response-Format (RFC 7807 Problem Details)

**Status:** Accepted
**Datum:** 2026-05-27
**Kontext:** Wave D3 — Observability

---

## Kontext

Verschiedene Endpoints lieferten inkonsistente Fehlerformate:
- `{"detail": "Not found"}`
- `{"error": "VALIDATION_FAILED", "message": "..."}`
- `{"status": 422, "errors": [...]}`

Frontend-Code und externe Clients mussten verschiedene Formate parsen.

## Entscheidung

Alle 4xx- und 5xx-Responses folgen **RFC 7807 Problem Details** (https://tools.ietf.org/html/rfc7807):

```json
{
  "type": "https://valeo-erp.de/errors/not-found",
  "title": "Nicht gefunden",
  "status": 404,
  "detail": "Kontrakt 'abc-123' nicht gefunden",
  "instance": "/api/v1/agrar/contracts/abc-123",
  "error": "NOT_FOUND"
}
```

### Felder

| Feld       | Pflicht | Beschreibung |
|------------|---------|--------------|
| `type`     | Ja      | URI-Referenz auf Fehlertyp-Dokumentation |
| `title`    | Ja      | Menschenlesbare Kurzbeschreibung (Deutsch) |
| `status`   | Ja      | HTTP-Statuscode (Integer) |
| `detail`   | Ja      | Spezifische Fehlerbeschreibung |
| `instance` | Ja      | Request-URL-Pfad |
| `error`    | Ja      | Machine-readable Code (Backward-Compat) |

### Content-Type

Alle Problem-Details-Responses setzen `Content-Type: application/problem+json`.

### Exception-Hierarchie

```python
# app/core/exceptions.py
class DomainError(Exception):
    http_status: int = 500
    error_code: str = "DOMAIN_ERROR"

class EntityNotFoundError(DomainError):
    http_status = 404
    error_code = "NOT_FOUND"

class ConflictError(DomainError):
    http_status = 409
    error_code = "CONFLICT"

class ValidationFailedError(DomainError):
    http_status = 422
    error_code = "VALIDATION_FAILED"
```

### Exception-Handler-Registrierung

```python
# app/main.py
from app.core.exceptions import register_domain_exception_handlers
register_domain_exception_handlers(app)
```

Der Handler fängt `DomainError`, `HTTPException` und `RequestValidationError` und konvertiert sie in RFC 7807 Format.

### Backward-Compatibility

Das `"error"`-Feld ist eine VALEO-Erweiterung für Clients, die bereits `response.error` parsen. Es bleibt dauerhaft erhalten.

## Konsequenzen

**Positiv:**
- Ein einziges Parsing-Pattern im Frontend
- Maschinenlesbare Fehlercodes für Monitoring und Alerting
- Standardkonformes Format (RFC 7807)

**Negativ:**
- Clients müssen ggf. auf neues Format migriert werden
- `trace_id` fehlt noch (geplant für Wave D1)

## Referenz

- `app/core/exceptions.py` — DomainError-Hierarchie + Handler-Registrierung
- `app/main.py` — `register_domain_exception_handlers(app)`
- RFC 7807: https://tools.ietf.org/html/rfc7807
