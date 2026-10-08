---
title: MCP Nachweisraum/DMS Deep-Link Navigation 2026-10-08
type: reference
audience: [agent, entwickler, qa]
owner: Cursor
status: abgeschlossen
last_reviewed: 2026-10-08
description: Voice/Dispatch navigiert auf sichere route_path aus dms.document.search / gobd.export_status.
---

# MCP-DEEP-LINK-DMS 2026-10-08

## Lieferung

| Schicht | Verhalten |
|---------|-----------|
| Search-Read | `dms.document.search` Items mit `route_path`/`screen_id`; optional `dokument_id` (404 wenn leer) |
| GoBD-Read | `dms.gobd.export_status` liefert `route_path` `/docflow/gobd-export/{id}` |
| Intent | „öffne Dokument DOC-42“ → `nav-nachweisraum` + `dokument_id` |
| Dispatch | mit `dokument_id` → MCP dryRun Search → Navigate |
| Dispatch | mit sicherem `route_path` → Navigate ohne MCP |
| Dispatch | ohne Kennung → `/docflow/nachweisraum` |
| Guard | nur `/docflow/nachweisraum/{id}` bzw. `/docflow/gobd-export/{id}` |
| Route | Alias + Gen-Route `$id`; Seiten lesen `useParams` |

## Nachweis

```bash
python -m pytest tests/test_mcp_execution.py -k "document_search or gobd_export" \
  --noconftest -q --override-ini addopts=''

cd packages/frontend-web
npx vitest run src/__tests__/lib/mcp-dms-open.test.ts \
  src/__tests__/features/ki-usability/ActionDispatchContext.test.tsx

cd services/ki-usability
python -m pytest tests/test_voice_intent_lager_einkauf_hr.py::TestResolverNachweisraum \
  tests/test_voice_intent_lager_einkauf_hr.py::TestActionRegistry \
  -q --override-ini addopts=
```

4 DMS/GoBD-MCP-, 24 Frontend-, 12 Voice-Registry/Nachweisraum-Tests gruen.

## Grenzen

Kein Write, kein FIN-CLOSE/ADR-076. Kein Commit/Push; keine neue DB.
Keine neuen MCP-Tools (weiterhin 36).
