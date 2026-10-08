---
title: MCP Agrar Deep-Link Navigation 2026-10-08
type: reference
audience: [agent, entwickler, qa]
owner: Cursor
status: abgeschlossen
last_reviewed: 2026-10-08
description: Voice/Dispatch navigiert auf sichere route_path aus agrar.contract.get und weighing_ticket.list.
---

# MCP-DEEP-LINK-AGRAR 2026-10-08

## Lieferung

| Schicht | Verhalten |
|---------|-----------|
| Contract-Read | `agrar.contract.get` liefert `route_path` `/agrar/kontrakt/{id}` |
| Weighing-List | Items + optional `ticket_id` mit `/waage/wiegeschein/{id}` (404 wenn leer) |
| Intent | „öffne Kontrakt K-42“ → `nav-agrar-vertraege` + `kontrakt_id` |
| Intent | „öffne Wiegeschein WS-9“ → `nav-wiegeschein` + `ticket_id` |
| Dispatch | MCP dryRun → Navigate; Listen-Fallback ohne Kennung |
| Guard | nur `/agrar/kontrakt/{id}` bzw. `/waage/wiegeschein/{id}` |

## Kernkette Deep-Links (Serie)

Kunde → Auftrag → Lot → Zelle → Bestellung → DMS → Agrar/Wiegeschein.
Optional weiter: Lagerbestand (`lager.bestand.get`).

## Nachweis

```bash
python -m pytest tests/test_mcp_execution.py -k "agrar_contract or weighing" \
  --noconftest -q --override-ini addopts=''

cd packages/frontend-web
npx vitest run src/__tests__/lib/mcp-agrar-open.test.ts \
  src/__tests__/features/ki-usability/ActionDispatchContext.test.tsx

cd services/ki-usability
python -m pytest tests/test_voice_intent_fibu_compliance_agrar_logistik.py::TestResolverAgrar \
  -q --override-ini addopts=
```

1 Agrar-MCP-, 27 Frontend-, 7 Voice-Agrar-Tests gruen.

## Grenzen

Kein Write, kein FIN-CLOSE/ADR-076. Kein Commit/Push; keine neue DB.
