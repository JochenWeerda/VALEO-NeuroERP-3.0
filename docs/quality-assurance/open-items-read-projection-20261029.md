---
title: Offene Posten: vollstaendige Leseprojektion
type: reference
audience: [entwickler, qa, agent]
owner: Codex
status: aktiv
last_reviewed: 2026-10-29
version: 1.0.0
description: Gezielter Vertragsnachweis im akzeptierten Integrationsstand.
---

# Open items read projection — 2026-10-29

## Scope

Read-list contract only: `GET /api/v1/finance/open-items`. The production API router mounts `open_items.router` below `/finance`; it serves the route in `app/api/v1/endpoints/open_items.py`.

## Changes

- Added bounded `offset` pagination and `total`, counted with the same tenant and caller filters as the returned page.
- Made page ordering deterministic by due date, invoice number, then ID.
- Added opt-in `only_open`: positive outstanding amount and, when the status column exists, status `offen` or `teilweise`.
- Added the derived `ueberfaellig` response field. It is true only when the outstanding amount is positive and the due date is before today; an item due today is not overdue.
- Existing summary values remain calculated from the returned page. No defaults are substituted for count-query failures.

## Test evidence

`tests/test_open_items_read_projection.py` covers the SQL filters shared by count and page queries, count and offset, deterministic ordering, opt-in open-item criteria, computed overdue semantics, and invalid pagination bounds. It uses a database mock; no database or container was created.

## Limits

Eight isolated tests passed. The lead additionally verified signed REST, MCP and CLI reads against the shared valeo_probe: one transactionally rolled-back SQL scenario passed, including canonical detail summary, count, pagination, exact aggregate receipt, tenant and role denial. Existing tenant resolution and role dependencies were not changed. An extended payment-history scenario is tracked in the functional debtor QA report.
