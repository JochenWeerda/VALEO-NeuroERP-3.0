---
title: CI read and audit boundary repairs
type: reference
audience: [entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-10-28
version: 1.0.0
description: Concrete CI repairs with targeted proof and remaining SQL acceptance.
---

# CI read and audit boundary repairs

The logs on 8a77 identify an unused ESLint directive, TS6305 in the standalone
mask workflow and the mask bridge exceeding its LOC cap after Shared integration.
The directive is removed. The workflow uses the existing type-check task, which
builds the referenced Node project first. Pricing/POS use one tenant-bound read
service; the actual file cap is reduced from 1416 to 1409, never increased.
Failed condition reads roll back and return 503 instead of a fabricated price.

Channel audit children explicitly inherit the thread tenant in ORM and WhatsApp
SQL writes. Failed database commits roll back and propagate, without reporting
an in-memory success. Foreign thread IDs cannot be reassigned; a missing SQL
record cannot fall through to the global memory store. Global persistent audit
clearing is refused.

Targeted unit run: 25 passed (13 verified-email, eight pricing, four channel),
3.50 seconds, no database writes. The initial invocation also passed all cases
but failed the global coverage threshold for this small selection. The rerun
uses --no-cov for the focused selection only; global coverage policy is unchanged.
These unit cases do not replace real SQL/HTTP authorization acceptance.

The existing probe still has loading_stop_fk_20261023. Its coordinated canonical
upgrade and strict SQL regression run remain pending while a foreign Claude
session is present. No backup, migration, reset or live activation has started.
Fresh CI and full frontend checks remain required; this report is not a total
release approval.
