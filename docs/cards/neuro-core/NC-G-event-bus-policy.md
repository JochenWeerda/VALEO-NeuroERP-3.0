# NC-G — Event Bus + Knowledge Store

**Lane:** Neuro-Core (Lane G)
**Prioritaet:** P2
**Status:** umgesetzt (G1, G4-G5)

## Kontext
Domain-Events brauchen typisierte Schemas mit Versionierung.
Policies muessen versioniert und rollback-faehig sein.

## Loesung
Event Schema Registry mit Pydantic-Modellen und Version-Header.
6 vordefinierte Event-Typen (Audit, Inventory, Settlement, Order, Compliance, Consent).
Policy Registry mit DB-Persistenz, Versionierung und Rollback.

## Dateien
- `app/services/event_schema_registry.py` — Event Schemas
- `app/services/policy_registry.py` — Policy Registry
- `app/api/v1/endpoints/neuro_event_policy.py` — REST-API
