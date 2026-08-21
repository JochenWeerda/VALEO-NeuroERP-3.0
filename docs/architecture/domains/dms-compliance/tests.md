---
title: DMS / Compliance — Tests
type: reference
audience: [qa]
owner: domain/dms-compliance
status: aktiv
last_reviewed: 2026-08-21
version: 1.1.0
---

# DMS / Compliance — Tests

```bash
pytest tests/ -k "compliance or dms or archive"
```

Frontend: `packages/frontend-web/src/pages/compliance/`, `dms/`

```bash
pytest tests/test_docflow_returns.py -q --no-cov
pnpm --dir packages/frontend-web exec vitest run src/__tests__/pages/docflow/dokumenten-ruecklauf.test.tsx
```
