# VALEO-WF-COCKPIT-001 - Workflow- und Prozessleitstand

Stand: 2026-06-23

## Ziel

Der Workflow-Leitstand macht laufende und blockierte ERP-Prozessinstanzen
sichtbar, ohne die fachliche Kernlogik aus Process Kernel, Domain-Services,
Outbox/NATS oder Audit-Logs herauszuziehen.

Der Slice setzt P0.1 aus `valeo_neuroerp_youtube_gap_analyse_2026-06-23.md`
um: Prozesssicht, externe Gate-Blocker, Event-Kette und Replay-Guard.

## Fachlicher Vertrag

Eine Prozessinstanz hat genau einen Tenant, einen Prozessschluessel, eine
Correlation-ID und einen operativen Status:

- `pending`
- `running`
- `blocked_external_gate`
- `failed`
- `completed`
- `compensated`

`blocked_external_gate` ist bewusst getrennt von `failed`. Ein DATEV-, TSE-,
DMS-, Bank-, ELSTER- oder Hardware-Blocker ist fachlich kein Systemfehler,
sondern ein externer Gate-Zustand mit Retry-/Replay-Entscheidung.

## Architekturgrenze

Der Leitstand ist kein n8n-Ersatz und keine neue Workflow Engine. Er ist eine
Cockpit-Projektion:

- read-heavy
- tenantisoliert
- auditierbar
- replay-fail-closed
- ohne produktive Seiteneffekte im MVP

Deterministische Buchungs-, QS-, POS-, Waage-, FIBU- und Settlement-Logik bleibt
in den Domain-Services.

## API-Vertrag

- `GET /api/v1/workflow/cockpit/status-model`
- `GET /api/v1/workflow/cockpit/summary`
- `GET /api/v1/workflow/cockpit/processes`
- `POST /api/v1/workflow/cockpit/processes`
- `GET /api/v1/workflow/cockpit/processes/{process_instance_id}`
- `POST /api/v1/workflow/cockpit/processes/{process_instance_id}/replay-requests`

Replay-Anforderungen brauchen den Header:

```text
X-VALEO-Roles: workflow:replay
```

Ohne diese Rolle wird `403` geliefert. Terminale Prozesse sind nicht replaybar.

## UAT-Szenario

1. POS-Tagesabschluss meldet Prozess `pos.daily-close` mit Status
   `blocked_external_gate` und Blocker `TSE`.
2. Operator sieht den Prozess im Cockpit als extern blockiert, nicht als
   technischen Fehler.
3. Replay-Anforderung ohne Rolle wird abgelehnt.
4. Replay-Anforderung mit `workflow:replay` erzeugt ein Audit-Event.
5. Event-Kette bleibt chronologisch nachvollziehbar.

## Abgrenzung Folgeslices

- UI-Leitstand / Meridian ListReport
- Persistente Cockpit-Tabellen
- NATS-/Outbox-Projektor
- Dead-Letter-Queue-Ansicht
- kontrollierter Retry mit Kompensationspfad
