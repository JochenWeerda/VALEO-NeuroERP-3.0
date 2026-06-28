---
title: CRM — Tests
type: reference
audience: [entwickler, qa]
owner: domain/crm
status: aktiv
last_reviewed: 2026-06-27
version: 1.0.0
---

# CRM — Tests

## Backend (pytest)

| Muster | Beispiel |
|---|---|
| Business Partner | `tests/test_business_partner*.py` |
| CRM Endpoints | `tests/test_crm*.py` |
| Bedarfsdeckung | `tests/test_bedarfsdeckung*.py` |

Ausführung:

```bash
pytest tests/ -k "crm or business_partner or verkauf" -m "not slow"
```

## Frontend (Vitest / Playwright)

| Typ | Pfad |
|---|---|
| Unit | `packages/frontend-web/src/pages/crm/` |
| E2E | `tests/e2e/` — grep `@crm` / Verkauf-Flows |

```bash
cd packages/frontend-web && npm run test
npx playwright test --grep verkauf
```

## QA-Matrix

→ [quality-assurance/](../../../quality-assurance/) — Capability-Matrix CRM/Vertrieb

## Architektur-Drift

Domain-Mapping prüfen: `pnpm arch:drift`
