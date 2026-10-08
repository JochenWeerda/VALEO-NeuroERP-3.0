---
title: MCP Kunde Deep-Link Navigation 2026-10-08
type: reference
audience: [agent, entwickler, qa]
owner: Cursor
status: abgeschlossen
last_reviewed: 2026-10-08
description: Voice/Dispatch navigiert auf sicheren route_path aus crm.customer.open.
---

# MCP-CUSTOMER-NAV 2026-10-08

## Lieferung

Folge zu [mcp-customer-open-20261008](./mcp-customer-open-20261008.md):

| Schicht | Verhalten |
|---------|-----------|
| Intent | „öffne Kunde TEST“ / „Kunde öffnen K-1001“ → `nav-customers` + `kunden_nr` |
| Dispatch | mit `kunden_nr` → MCP `crm.customer.open` (dryRun) → Navigate |
| Dispatch | mit sicherem `route_path` → Navigate ohne MCP |
| Dispatch | ohne Kennung → `/verkauf/kunden-liste` |
| Guard | nur relative `/crm/customers/{id}` (kein Open-Redirect) |

## Nachweis

```bash
cd packages/frontend-web
npx vitest run src/__tests__/lib/mcp-customer-open.test.ts \
  src/__tests__/features/ki-usability/ActionDispatchContext.test.tsx

cd services/ki-usability
python -m pytest tests/test_voice_intent_verkauf_crm.py -q
```

## Grenzen

Uebrige MCP-Adapter, Mask-ID-Write-Paritaet, FIN-CLOSE und Stufe-2-SUS bleiben offen.
Kein Commit in diesem Slice; keine neue DB/Container.
