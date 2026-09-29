---
title: Metadatenvertrag des Portal-Business-Time-Slices
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-09-29
description: Nachweis der kanonischen Pflichtfelder im Portal-Slice.
---

# Metadatenvertrag des Portal-Business-Time-Slices

`BUSINESS-TIME-PORTAL-20260929.yaml` führt jetzt `slice_id`, `title` und
`created_at`. `slice_id` und `id` sind identisch. Die bereits dokumentierten
Abnahme-, Risiko- und AI-Harness-Verträge bleiben unverändert.

## Nachweis

`python scripts/valeo_slice.py status BUSINESS-TIME-PORTAL-20260929`

Der Slice-Validator meldet `Schema: OK`; YAML-, Markdown- und Docs-Governance-
Prüfung sind grün.
