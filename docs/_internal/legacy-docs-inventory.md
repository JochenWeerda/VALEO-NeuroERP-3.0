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
| Markdown-Dateien gesamt | 648 |
| Kuratiert (behalten) | 629 |
| Archiv-Kandidaten | 0 |
| Doppelte Dateinamen | 140 |

## Archiv-Buckets (Kandidaten)

| Bucket | Anzahl |
|--------|--------|

## Doppelte Dateinamen (Top 30)

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
| `vk-020-rohware-wizard-schrittvalidierung.md` | 2 |
| `cmp-001-compliance-to-report.md` | 2 |
| `com-001-compliance-to-audit.md` | 2 |
| `dom-doc-003-nachweis-und-rueckmeldung.md` | 2 |
| `crm-001-crm-to-revenue.md` | 2 |
| `dom-crm-003-fall-und-ownership.md` | 2 |
| `dom-proc-003-beschaffungsausnahmen.md` | 2 |
| `p2p-050-wizard-schrittvalidierung.md` | 2 |
| `dom-fin-003-fibu-operatorparitaet.md` | 2 |
| `fin-001-finance-to-close.md` | 2 |
| `fin-001-finance-to-reporting.md` | 2 |
| `otc-011-zahlungseingang-und-abstimmung.md` | 2 |
| `dom-supply-003-physische-kette.md` | 2 |
| `cts-001-contract-to-settlement.md` | 2 |
| `cts-009-rohwaren-positionsmonitor.md` | 2 |

## Card-Duplikate (kanonisch aufgelöst)

| Duplikat (archiviert) | Kanonisch |
|-----------------------|-----------|
| `docs/cards/inventory/INV-001-inventory-to-settlement.md` | `docs/cards/lager/INV-001-inventory-to-settlement.md` |

## Pflege

- Migration: `python scripts/docs-legacy-migrate.py --apply`
- Dry-run: `python scripts/docs-legacy-migrate.py --dry-run`
- Card-Dedupe: `python scripts/docs-legacy-migrate.py --dedupe-cards`
- Roadmap-Status: `python scripts/docs-legacy-migrate.py --archive-roadmap-status --apply`
- Roadmap-Purge: `python scripts/docs-legacy-migrate.py --purge-roadmap --apply`
- Ziel: `docs/_internal/archive/` (einheitlich)

