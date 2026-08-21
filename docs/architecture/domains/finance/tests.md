---
title: Finance — Tests
type: reference
audience: [qa, entwickler]
owner: domain/finance
status: aktiv
last_reviewed: 2026-06-27
version: 1.0.0
---

# Finance — Tests

Rechnungstapel: `pytest tests/test_billing_batch.py -q --no-cov` und
`vitest run src/__tests__/pages/finance/rechnungstapel.test.tsx`.

```bash
pytest tests/ -k "finance or fibu or ap_invoice or closing" -m "not slow"
```

Frontend: `packages/frontend-web/src/pages/finance/`, `fibu/`, `meldewesen/`, `pos/`

E2E: Playwright Finance/FiBu-Flows in `tests/e2e/`
