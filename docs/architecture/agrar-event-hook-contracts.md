# Agrar Event- und Hook-Contracts (v1)

Stand: 13.02.2026

## Event Contracts

Versionierte Event-Payloads liegen in:

- `modules/agrar/contracts/events_v1.py`

Initiale Event-Typen:

- `agrar.weighing_ticket.created`
- `agrar.weighing_ticket.allocated`
- `agrar.contract.allocated`
- `agrar.settlement.issued`

## Hook Contracts

Hook-Verträge liegen in:

- `modules/agrar/contracts/hooks_v1.py`

Sie definieren Producer, Consumer und Schema-Referenzen je Hook.

## Runtime Discovery

Die Contracts können zur Laufzeit über folgende API abgerufen werden:

- `GET /api/v1/meta/modules/agrar/contracts`

Zusätzlich liefert:

- `GET /api/v1/meta/modules`
- `GET /api/v1/meta/modules/{module_name}`

den aktivierten Modulzustand.

