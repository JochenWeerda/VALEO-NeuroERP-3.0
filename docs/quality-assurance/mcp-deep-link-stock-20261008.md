---
title: MCP Lagerbestand Deep-Link Navigation 2026-10-08
type: reference
audience: [agent, entwickler, qa]
owner: Cursor
status: abgeschlossen
last_reviewed: 2026-10-08
description: Voice/Dispatch navigiert auf sicheren route_path aus lager.bestand.get.
---

# MCP-DEEP-LINK-STOCK 2026-10-08

## Lieferung

| Schicht | Verhalten |
|---------|-----------|
| Bestand-Read | `lager.bestand.get` liefert `route_path` `/lager/artikel/{id}` |
| Intent | „öffne Bestand ART-WEIZEN“ / „öffne Artikel …“ → `nav-lager` + `artikel_id` |
| Dispatch | mit `artikel_id` → MCP dryRun → Navigate |
| Dispatch | ohne Kennung → `/lager/bestandsuebersicht` |
| Guard | nur relative `/lager/artikel/{id}` |

## Deep-Link-Serie (abgeschlossen)

Kunde → Auftrag → Lot → Zelle → Bestellung → DMS → Agrar/Wiegeschein → Bestand.
Weitere Reads (`lager.inventur.status`, `compliance.gate.status`, `agent.proposal.list`)
haben keine klare Einzel-Detailroute ohne Backend-/UI-Erfindung — Serie daher
**abgeschlossen**.

## Nachweis

```bash
python -m pytest tests/test_mcp_execution.py -k lager_bestand \
  --noconftest -q --override-ini addopts=''

cd packages/frontend-web
npx vitest run src/__tests__/lib/mcp-stock-open.test.ts \
  src/__tests__/features/ki-usability/ActionDispatchContext.test.tsx

cd services/ki-usability
python -m pytest tests/test_voice_intent_lager_einkauf_hr.py::TestResolverLager \
  -q --override-ini addopts=
```

1 Bestand-MCP-, 28 Frontend-, 19 Voice-Lager-Tests gruen.

## Grenzen

Kein Write, kein FIN-CLOSE/ADR-076. Kein Commit/Push; keine neue DB.
