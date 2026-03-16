# Wave 58 — Process Cost Allocation + Workflow Audit Trail Contracts

**Status:** DONE
**Date:** 2026-03-16
**Tests:** 155 passed, 0 failed

## Modules

### `app/core/process_cost_allocation_contracts.py`
- `KostenTyp` (PERSONAL, SYSTEM, EXTERN, OVERHEAD)
- `AllokationsMethode` (DIREKT, ANTEILIG, GLEICH, GEWICHTET)
- `KostenStatus` (GEPLANT, GEBUCHT, STORNIERT)
- `KostenPosition` — individual cost line item
- `KostenAllokation` — cost allocation to a cost center with:
  - `gesamtkosten()` — sums non-STORNIERT positions × allokations_anteil
  - `kosten_nach_typ()` — per-type breakdown × allokations_anteil
- `verteile_kosten()` — distributes a total amount across cost centers (DIREKT / GLEICH / ANTEILIG / GEWICHTET)
- `get_default_kosten_allokationen()` — 2 fixture allocations (KA-001: 135.0 EUR, KA-002: 144.0 EUR)

### `app/core/workflow_audit_trail_contracts.py`
- `AuditAktionsTyp` (ERSTELLT, GEAENDERT, FREIGEGEBEN, ABGELEHNT, GELOESCHT, EXPORTIERT, ANGEMELDET)
- `AuditIntegritaetsStatus` (GUELTIG, UNGUELTIG, UNBEKANNT)
- `AuditEintrag` — immutable audit entry with SHA-256 hash chain:
  - `berechne_hash()` — SHA-256 of all fields including vorgaenger_hash
  - `ist_hash_gueltig()` — validates eintrag_hash against computed hash
- `AuditTrail` — ordered chain of AuditEintrag:
  - `pruefe_integritaet()` — validates entire hash chain
  - `letzter_eintrag()` — entry with latest zeitstempel
- `erstelle_audit_eintrag()` — factory with auto-computed hash
- `get_default_audit_trail()` — 4-entry valid chain for WI-K-001 (AT-001)

## FastAPI Endpoints (prefix: `/api/v1/process`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/kosten/allokationen` | List default cost allocations with totals |
| POST | `/kosten/verteile` | Distribute amount across cost centers |
| GET | `/audit-trail/trail` | Get default audit trail with integrity check |
| POST | `/audit-trail/pruefe-integritaet` | Verify trail integrity (with tamper simulation) |

## Test Coverage

| Section | Tests |
|---------|-------|
| Enum validation | 14 |
| KostenPosition dataclass | 6 |
| KostenAllokation.gesamtkosten() | 11 |
| KostenAllokation.kosten_nach_typ() | 8 |
| verteile_kosten() | 14 |
| get_default_kosten_allokationen() | 18 |
| AuditAktionsTyp/IntegritaetsStatus enums | 11 |
| AuditEintrag.berechne_hash() | 13 |
| AuditEintrag.ist_hash_gueltig() | 5 |
| AuditTrail.pruefe_integritaet() | 9 |
| AuditTrail.letzter_eintrag() | 5 |
| erstelle_audit_eintrag() | 6 |
| get_default_audit_trail() | 16 |
| FastAPI endpoint tests | 21 |
| **Total** | **155** |

## Regression
- 4189 existing tests: all still passing
- 3 pre-existing failures in `test_process_kernel_wave4_ap4_ap5_ap6.py` (NameError in runtime_operations.py — unrelated to Wave 58)
