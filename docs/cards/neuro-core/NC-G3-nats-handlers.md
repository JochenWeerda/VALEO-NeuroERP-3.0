# NC-G3 -- NATS Consumer Handlers

**Lane:** Neuro-Core  
**Prioritaet:** P2  
**Status:** umgesetzt  

## Kontext
Der NATS-Consumer existiert, aber es fehlten aktivierte Handler fuer
kerngeschaeftliche Events. Ohne Handler bleibt der Event Bus passiv.

## Loesung
Drei baseline Handler fuer Audit, Inventory Movement und Settlement Created,
inklusive Schema-Validierung und strukturierter Logs.

## Dateien
- `app/services/nats_event_handlers.py`
- `app/domains/shared/events.py`
- `tests/test_nats_event_handlers.py`
- `docs/workflows/nc-g3-nats-handlers.md`

## Abhaengigkeiten
- Event Schema Registry (NC-G1)
- NATS Consumer (NC-G2)
