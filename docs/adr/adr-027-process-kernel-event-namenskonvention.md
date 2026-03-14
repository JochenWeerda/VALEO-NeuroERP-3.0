# ADR-027 Process-Kernel-Event-Namenskonvention (NATS-Subject)

**Status:** Accepted
**Date:** 2026-03-11
**Supersedes:** keinen
**Bezug:** [ADR-008 Eventing-/Outbox-Standard](adr-008-eventing-outbox-standard.md)

## Context

ADR-008 legt den allgemeinen Eventing-/Outbox-Standard fest. Fuer die erste produktive
Umsetzung (Wave 2 AP1) ist eine verbindliche Namenskonvention fuer NATS-Subjects
notwendig, damit Consumer, Wildcard-Subscriptions und Read-Model-Aktualisierungen
zuverlaessig und konfliktfrei arbeiten.

Ohne Konvention entstehen:
- kollidierende Subject-Pfade zwischen Domains
- Wildcard-Subscriptions, die versehentlich fremde Events empfangen
- Unklarheiten, ob ein Subject tenant-isoliert oder global ist

## Decision

Alle produktiven Kernprozess-Events verwenden folgendes NATS-Subject-Format:

```
{tenant_id}.{domain}.{aggregate}.{verb}
```

### Felder

| Feld | Typ | Beispielwerte |
|------|-----|--------------|
| `tenant_id` | Mandanten-ID (lowercase) | `tenant1`, `genossenschaft-nord` |
| `domain` | fachliche Domaene | `finance`, `agrar`, `lager`, `sales` |
| `aggregate` | Aggregat-Wurzel (snake_case) | `ap_invoice`, `harvest_acceptance`, `quality_protocol` |
| `verb` | Ereignisart (snake_case, Vergangenheitsform) | `approved`, `completed`, `posted`, `rejected` |

### Wildcard-Subscriptions

| Pattern | Bedeutung |
|---------|-----------|
| `*.finance.>` | alle Finance-Events aller Mandanten |
| `tenant1.>` | alle Events von tenant1 |
| `*.*.ap_invoice.*` | alle AP-Invoice-Events aller Mandanten und Domains |
| `tenant1.finance.ap_invoice.*` | alle AP-Invoice-Events von tenant1 |

### Hilfsfunktion

```python
# app/domains/shared/process_events.py
def build_event_subject(event: ProcessKernelEvent) -> str:
    return f"{event.tenant_id}.{event.domain}.{event.aggregate}.{event.verb}"
```

### Implementierte Events (Wave 2 AP1)

| Event-Klasse | Subject-Beispiel |
|-------------|-----------------|
| `APInvoiceApprovalRequested` | `tenant1.finance.ap_invoice.approval_requested` |
| `APInvoiceApprovalGranted` | `tenant1.finance.ap_invoice.approval_granted` |
| `APInvoiceApproved` | `tenant1.finance.ap_invoice.approved` |
| `APInvoiceRejected` | `tenant1.finance.ap_invoice.rejected` |
| `APInvoicePosted` | `tenant1.finance.ap_invoice.posted` |
| `HarvestAcceptanceCompleted` | `tenant1.agrar.harvest_acceptance.completed` |
| `QualityProtocolCompleted` | `tenant1.agrar.quality_protocol.completed` |

### Basis-Eventklasse

```python
@dataclass(kw_only=True)
class ProcessKernelEvent(DomainEvent):
    tenant_id: str
    domain: str    # finance | agrar | lager | ...
    aggregate: str # ap_invoice | harvest_acceptance | ...
    verb: str      # approved | rejected | completed | ...
    schema_version: int = 1
    workflow_instance_id: str | None = None
```

## Consequences

Positiv:
- Konsistente NATS-Subject-Struktur ueber alle Domains
- Tenant-Isolation ist durch Praefix sichergestellt
- Wildcard-Subscriptions sind vorhersehbar und konfliktfrei
- `build_event_subject()` als einzige kanonische Funktion

Negativ:
- Umbenennung von Events bricht bestehende Subscriptions (Breaking Change)
- `tenant_id` im Subject erfordert korrekte Befuellung — kein Leerzeichen/Sonderzeichen

## Migration

Bestehende Events ohne Konvention (z.B. direkte DB-Side-Effects) werden schrittweise
auf den Outbox-Pfad migriert. Reihenfolge:
1. AP-Invoice-Freigabe (Wave 2 AP1) — umgesetzt
2. Ernte-Annahme, Qualitaetsprotokoll (Wave 2 AP1) — umgesetzt
3. Settlement, Zahlungslauf (Wave 2 AP1 Folgearbeiten)
4. Kundenstamm, Kontrakt (Wave 3)

## References

- [ADR-008 Eventing-/Outbox-Standard](adr-008-eventing-outbox-standard.md)
- [Wave 2 AP1 Status](../process-kernel/wave-2/STATUS.md)
- `app/domains/shared/process_events.py`
- `tests/test_process_kernel_wave2_events.py`
