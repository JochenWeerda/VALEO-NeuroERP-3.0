---
title: Handshake RLS-DOMAIN-DOCFLOW-20261027
type: handshake
audience: [agent]
owner: Claude Code
status: aktiv
last_reviewed: 2026-10-27
version: 1.0.0
description: Übergabe Claude → Codex für die RLS-Domain docflow.
---

# Handshake RLS-DOMAIN-DOCFLOW-20261027 (Claude Code → Codex)

Kette: `… → #70 → #71 → dieser PR`. Alembic:
`rls_booking_templates_shared_20261027 → rls_knowledge_objects_shared_20261027 → rls_domain_docflow_20261027`.

## Für dich

1. **Neue UNIQUE-Bedingungen auf P5-Tabellen:** `document_headers` und `pos_terminals`
   bekommen je `(id, tenant_id)`. Die Policies bleiben unverändert.
2. **OpenAPI:** Nachgezogen sind nur die Pfade `/gobd/*` (Query `tenant_id` entfällt). Deine
   Drift `closing-checklists` bleibt unverändert.
3. **Folge-Slice vorgeschlagen:** Verbund-FKs für die übrigen Kinder von `document_headers`
   (Links, Buchungen, POS-Belegprüfung, Rückgaben). Die sind P5-Tabellen; ich übernehme das
   gern, wenn du nichts dagegen hast.

## Nicht berührt

Keine Live-DB, kein Reset; `valeo_probe` unverändert.
