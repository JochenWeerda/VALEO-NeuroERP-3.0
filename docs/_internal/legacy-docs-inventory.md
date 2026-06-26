---
title: Legacy-Docs-Inventar (intern)
type: reference
audience: [entwickler, docs]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-26
version: 1.0.0
---

# Legacy-Docs-Inventar

**Generiert:** 2026-06-26 via `scripts/docs-legacy-migrate.py`

## Kennzahlen

| Metrik | Wert |
|--------|------|
| Markdown-Dateien gesamt | 649 |
| Kuratiert (behalten) | 630 |
| Archiv-Kandidaten | 0 |
| Doppelte Dateinamen (gesamt) | 140 |
| — strukturell harmlos | 140 |
| — inhaltlich prüfbar | 0 |

## Archiv-Buckets (Kandidaten)

| Bucket | Anzahl |
|--------|--------|

## Strukturell harmlose Duplikate

Gleicher Dateiname, unterschiedlicher Zweck — **kein Merge nötig** (Wave-`STATUS.md`, Cards↔Workflows, Bereichs-`index.md`/`README.md`).

| Dateiname | Vorkommen |
|-----------|-----------|
| `status.md` | 119 |
| `index.md` | 9 |
| `readme.md` | 8 |
| `governance.md` | 2 |
| `crm.md` | 2 |
| `vk-010-ernte-annahme.md` | 2 |
| `vk-011-qp-handover-und-lkw-validierung.md` | 2 |
| `vk-012-annahme-abrechnung.md` | 2 |
| `vk-013-kampagnenabschluss.md` | 2 |
| `vk-014-settlement-kampagnenreferenz.md` | 2 |
| `vk-015-settlement-kampagnen-backfill.md` | 2 |
| `vk-016-queue-cta-und-artikel-api.md` | 2 |
| `vk-017-queue-article-id.md` | 2 |
| `vk-018-klaerungsprozess-gesperrt.md` | 2 |
| `vk-019-queue-repair-article-id.md` | 2 |

## Inhaltlich prüfbare Duplikate

| Dateiname | Vorkommen |
|-----------|-----------|
| *(keine offenen Fälle)* | 0 |

## Card-Duplikate (kanonisch aufgelöst)

| Duplikat (archiviert) | Kanonisch |
|-----------------------|-----------|
| `docs/cards/inventory/INV-001-inventory-to-settlement.md` | `docs/cards/lager/INV-001-inventory-to-settlement.md` |

## Pflege

- Migration: `python scripts/docs-legacy-migrate.py --apply`
- Dry-run: `python scripts/docs-legacy-migrate.py --dry-run`
- Card-Dedupe: `python scripts/docs-legacy-migrate.py --dedupe-cards`
- Roadmap-Purge: `python scripts/docs-legacy-migrate.py --purge-roadmap --apply`
- Ziel: `docs/_internal/archive/` (einheitlich)

