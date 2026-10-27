---
title: Handshake SYSTEM-TENANT-FALLBACK-20261027
type: handshake
audience: [agent]
owner: Claude Code
status: aktiv
last_reviewed: 2026-10-27
version: 1.0.0
description: Übergabe Claude → Codex: Mandanten-Rückfall "system" systemweit entfernt, Ratsche, Auswirkungen auf Leadbesitz.
---

# Handshake SYSTEM-TENANT-FALLBACK-20261027 (Claude Code → Codex)

Kette: `… → #69 → #70 → dieser PR`. Keine Migration.

## Was du wissen musst

1. **Breite Codeänderung** in 65 Quelldateien, nur an den Mandantenstellen. Wenn deine
   Studio- oder Inbox-Arbeit dieselben Dateien berührt (`agents.py`, `knowledge_api.py`,
   `crm_campaigns.py`, `fibu_router.py`, `financial_reports.py`, `open_items.py`,
   `process_kernel_api.py`), sind Konflikte möglich. Die Änderungen sind mechanisch:
   `Depends(get_tenant_id)` bzw. `tenant_id or get_current_tenant_id()`.
2. **OpenAPI** (Leadbesitz): 65 Pfade und 13 Request-Schemas nachgezogen. Deine vorbestehende
   Drift `/finance/closing-checklists*` habe ich bewusst unverändert gelassen.
3. **Agenten-Ops-Routen** (`/agents/neuroassist/ops/*`) verlangen jetzt einen geprüften
   Mandanten. Vorher waren sie ohne Token und mit `?tenant_id=` frei erreichbar. Masken oder
   MCP-Werkzeuge, die dort `tenant_id` mitsenden, sollten das weglassen.
4. **Neue Ratsche** `tests/test_system_tenant_fallback_contract.py` (Unit, läuft in CI).
   Neue Rückfälle auf `"system"` sind verboten. `"default"` ist je Datei eingefroren und darf
   nur sinken; nach einem Abbau die Basis im Test senken.
5. **`SHARED_TENANT_ID`** in `app/core/tenant_context.py` ist der benannte gemeinsame
   Mandant. Die Konstanten `SHARED_TENANT` in `booking_templates.py` und
   `chart_of_accounts.py` können darauf zeigen.

## Nicht berührt

Keine DB, keine Migration, keine Masken-/ScreenDefinitions, dein Arbeitsbaum.
