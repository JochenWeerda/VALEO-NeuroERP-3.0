# FiBu Shared Libraries

`finance-shared` bündelt wiederverwendbare Bausteine für alle FiBu-Microservices.
Der Fokus liegt auf drei Querschnittsthemen:

1. **GoBD-Compliance (`finance_shared.gobd`)**
   - Modellierung von Audit-Trail-Einträgen
   - Hash-Chains zur Nachvollziehbarkeit von Änderungen
   - Validierungs- und Protokollierungs-Hilfen
2. **Rollen & Berechtigungen (`finance_shared.auth`)**
   - Einheitliches Rollenmodell für Sachbearbeiter, Freigeber, Steuerberater und Admins
   - Ableitung konkreter Berechtigungen und Freigabe-Regeln
3. **Event-Verträge (`finance_shared.events`)**
   - Stark typisierte Event-Schemas für Buchungen, Stammdaten und OP-Verwaltung
   - Registry/Factory zur Serialisierung und Validierung von Nachrichten

## Installation

```bash
cd packages/finance-shared
pip install -e ".[dev]"
```

## Schnelleinstieg

```python
from decimal import Decimal
from finance_shared.auth import FiBuRole, RoleAssignment, FiBuAccessPolicy, FiBuPermission
from finance_shared.events import BookingCreatedEvent, FiBuEventType
from finance_shared.gobd import GoBDAuditTrail

# Auth
assignment = RoleAssignment(tenant_id="tenant-a", user_id="user-1", roles=[FiBuRole.FREIGEBER])
policy = FiBuAccessPolicy(assignment)
policy.ensure_permission(FiBuPermission.JOURNAL_CREATE)
policy.require_approval(amount=Decimal("1200.00"))

# Events
event = BookingCreatedEvent.from_values(
    tenant_id="tenant-a",
    booking_id="41d0b53d-fc02-45af-8a67-52c5630a0895",
    account_id="8400",
    amount=Decimal("1200.00"),
    currency="EUR",
    period="2025-11",
)
payload = event.serialize()

# GoBD Audit Trail
trail = GoBDAuditTrail(tenant_id="tenant-a")
entry = trail.create_entry(
    entity_type="journal_entry",
    entity_id=event.payload.booking_id,
    action="create",
    payload=payload,
    user_id=assignment.user_id,
)
trail.append_entry(entry)
trail.verify_chain()
```

Die einzelnen Module können unabhängig voneinander eingesetzt werden und sind
bewusst framework-agnostisch gehalten, damit sie in FastAPI-Services, Worker-
Jobs oder Skripten gleichermaßen funktionieren.


