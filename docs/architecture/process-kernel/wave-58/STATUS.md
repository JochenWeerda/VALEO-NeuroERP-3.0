# Wave 58 - Process Cost Allocation + Workflow Audit Trail Contracts

**Status:** abgeschlossen
**Datum:** 2026-03-16
**Tests:** 155 passed, 0 failed

## Scope

Wave 58 liefert Kostenallokations-Contracts fuer Prozesskosten und Audit-Trail-Contracts mit Integritaetspruefung fuer Workflows.

## Zielbild

Kostenverteilung und manipulationssichere Audit-Ketten sollen als standardisierte Kernel-Bausteine verfuegbar sein.

## Lieferumfang

### `app/core/process_cost_allocation_contracts.py`

- `KostenTyp`
- `AllokationsMethode`
- `KostenStatus`
- `KostenPosition`
- `KostenAllokation`
- `verteile_kosten()`
- `get_default_kosten_allokationen()`

### `app/core/workflow_audit_trail_contracts.py`

- `AuditAktionsTyp`
- `AuditIntegritaetsStatus`
- `AuditEintrag`
- `AuditTrail`
- `erstelle_audit_eintrag()`
- `get_default_audit_trail()`

### FastAPI-Endpunkte

| Methode | Pfad | Beschreibung |
|---------|------|--------------|
| GET | `/kosten/allokationen` | Listet Default-Kostenallokationen mit Summen |
| POST | `/kosten/verteile` | Verteilt einen Betrag ueber Kostenstellen |
| GET | `/audit-trail/trail` | Liefert Audit-Trail mit Integritaetscheck |
| POST | `/audit-trail/pruefe-integritaet` | Verifiziert Trail-Integritaet |

## Abnahmekriterien

- Kosten lassen sich per `DIREKT`, `GLEICH`, `ANTEILIG` und `GEWICHTET` verteilen.
- Audit-Eintraege bilden eine gueltige SHA-256-Hashkette.
- Default-Kostenallokationen und ein Default-Audit-Trail stehen bereit.
- Die vier API-Endpunkte liefern Kosten- und Audit-Funktionen.

## Tests

| Bereich | Tests |
|---------|-------|
| Enum validation | 14 |
| KostenAllokation und Verteilung | 57 |
| Audit Trail und Hashing | 49 |
| FastAPI endpoint tests | 21 |
| Total | 155 |

## Status

`abgeschlossen`
Stand: 2026-03-16
