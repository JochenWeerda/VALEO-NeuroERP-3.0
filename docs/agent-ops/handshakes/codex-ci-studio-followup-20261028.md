---
title: Codex CI and Studio followup 20261028
type: handshake
audience: [agent]
owner: Codex
status: aktiv
last_reviewed: 2026-10-28
version: 1.0.0
description: Integrated security and CI repairs, shared probe coordination and explicit remaining Studio work.
---

# Codex to parallel agents

Accepted source remains artifacts/migration-repair-source, delivery branch
codex/migration-parity-repair-20261022 (PR38). Root working copies are not the
accepted source. Shared author handoff has been read and integrated; 114 combined
Einkauf/Shared tests passed with outer rollback, zero skips. Live remains unchanged.

## Delivered corrections

- Verified email ownership requires boolean email_verified=true; no header fallback.
- Upstream forge1.4.2 replaces obsolete local exception. Braces reviewed against
  original; deepmerge source patch covers target and source in all entrypoints.
  Final real pnpm installation passes21 cases; policy20 cases. Raw audit retains
  the one low finding. Both remaining backport reviews expire October30.
- Concrete CI defects: existing full typecheck task, unused directive removed,
  pricing helper bounds/tenant/errors and reduced Godfile cap.
- Channel audit tenant propagation and fail-closed persistence, no memory success.
- Harvest head/position tenant propagation and explicit fixture child tenants.
  Focused boundaries25 cases, harvest14 cases, frontend full typecheck pass.
- Duplicate unrouted audit list removed; four selected existing cases pass,
  82 not selected. No feature or assertion was removed.

## Shared probe coordination

The PROBE-CANONICAL-UPGRADE claim reserves one preserving upgrade using --keep,
with compressed backup first. It has NOT started: a foreign connection named
agent:claude-rls-domains remains idle on the probe (latest check this session).
No termination, reset, backup or migration was performed. Please finish/release
your own session before the coordinated upgrade. The probe still reports
loading_stop_fk_20261023. Strict SQL regression acceptance remains pending.
No changes were made to valeo_neuro_erp or its active policies.

## Studio remains an active delivery objective

All business masks must eventually use the central Studio runtime with full
behavioral parity, Human/MCP/CLI authorization and tenant isolation. Current
report:857 definitions; gates A857/B857/C856/E800;57 runtime gaps; five draft
projections structurally ready; Browser/Image proof not measured here.
This is not a full Studio release.

The interrupted complaint listExperience drafts (schema/runtime AND builder)
are preserved byte-for-byte in ignored artifacts/studio-complaint-interrupted-20261028.
Their unsupported metadata is excluded from delivery and regenerated catalogs.
The existing complaint page still preserves workflow checkpoint/error handling,
search, export and priorities. Finish the central consumer contract before
switching that page. No legacy wrapper or fabricated ready marker is acceptable.

Remaining: coordinated probe upgrade and strict SQL checks; fresh complete CI;
portal certificate secure ownership relationship; functional Studio migration of
remaining masks and real browser acceptance. Generated artifacts are refreshed
from integrated sources; gate failures remain visible rather than baselines relaxed.
