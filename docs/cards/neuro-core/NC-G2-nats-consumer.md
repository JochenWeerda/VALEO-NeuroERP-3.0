# NC-G2 -- NATS Consumer Framework

**Lane:** Neuro-Core  
**Prioritaet:** P2  
**Status:** umgesetzt  

## Kontext
NATS JetStream ist als Event Bus vorhanden, aber es fehlte ein generischer
Consumer fuer eingehende Events. Ohne Consumer bleiben Outbox-Events
einseitig, Integrationen koennen nicht reagieren.

## Loesung
NATSEventConsumer mit:
- Handler-Registry pro Event-Type
- Default-Handler fuer unbekannte Events
- Ack/Nak/Term fuer robuste Verarbeitung
- Fallback bei deaktiviertem Event Bus

## Dateien
- `app/infrastructure/eventbus/nats_consumer.py` -- Consumer-Framework
- `tests/test_nats_consumer.py` -- Handler/Dispatch-Tests
- `docs/workflows/nc-g2-nats-consumer.md` -- Workflow-Doku

## Abhaengigkeiten
- NATS JetStream (nats-py)
- Event-Schema-Registry (NC-G1)
