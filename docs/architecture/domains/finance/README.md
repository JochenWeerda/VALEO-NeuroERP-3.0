---
title: Finance Domain Pack
type: explanation
audience: [entwickler, architect]
owner: domain/finance
status: aktiv
last_reviewed: 2026-06-27
version: 1.0.0
---

# Finance / FiBu — Domain Pack

**Owner:** `domain/finance`

Finanzbuchhaltung, AP/AR, Abschluss, DATEV-Export, UStVA/ELSTER, POS/TSE.

## Navigation

| Thema | Datei |
|---|---|
| API | [api.md](api.md) |
| Workflows | [workflows.md](workflows.md) |
| Tests | [tests.md](tests.md) |
| Entscheidungen | [decisions.md](decisions.md) |

## Sichten

- [C4 Component Finance](../../views/components/c4-finance.md)
- [fin-001 Workflow](../../../workflows/fin-001-finance-to-reporting.md)
- Index: `config/architecture-index.yaml` → `domains.finance`

## UIX / Universal Mask Generator

Finance wird nicht als erster Pilot umgestellt, bleibt aber ein harter
Interferenzbereich fuer GoBD, Audit, Freigabe und Export. Generatorfaehige
Finance-Masken muessen Audit-/Evidence-Anforderungen im `ScreenDefinition`-
Vertrag ausdruecken und duerfen keine schema-getriebenen Actions ohne
Permission- und Tenant-Pruefung ausfuehren.
