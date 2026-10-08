---
title: Usability MCP-Map CI + Voice Nav-Sync 2026-10-08
type: reference
audience: [agent, entwickler, qa]
owner: Cursor
status: abgeschlossen
last_reviewed: 2026-10-08
description: blocked_no_endpoint-Audit; CI-Drift-Gate; Haupt-App Voice Deep-Link Nav-IDs.
---

# USABILITY-MCP-MAP-CI-VOICE 2026-10-08

## Audit blocked_no_endpoint (31)

Alle 31 Map-Eintraege in `screen_mask_actions.json` haben weiterhin
`commandEndpoint: null` (nur ActionRuntime-`command` oder UI-Flow).

| Hinweis | Bewertung |
|---------|-----------|
| REST-CRUD existiert (Fuhrpark/Personal/Postfach/PO-Save) | kein Mask-`commandEndpoint`; MCP-Write waere Vertragserfindung |
| `mask:admin/postfaecher:testen` hat CE `/testen` | nicht in den 31; Postfach-WIP Claude; kein Mut-Key |
| Zahlauf `open_high` | bewusst nicht verdrahten |
| FIN-CLOSE `blocked_adr_076` | unberuehrt |

## Lieferung (statt MCP-Writes)

1. **CI-Drift-Gate:** `generate_mcp_mask_action_map.py --check` und
   `generate_screen_action_catalog.py --check` in
   `scripts/check_all_doc_generators.sh` (Quality-Gate Doc-Meta-Check).
2. **Voice-Nav-Sync:** `nav-einkauf`, `nav-lager`, `nav-agrar-vertraege` in
   `app/core/ki_action_registry.py`; Umlaut-Phrasen auf bestehenden Deep-Link-Navs;
   Param-Extraktion via `ki_voice_deep_link_params.py`.
3. **Vite-Proxy:** `ki_usability`-Router zusaetzlich ohne `/ki`-Prefix
   (`/api/v1/voice`, `/api/v1/actions`).

## Nachweis

```bash
python scripts/generate_mcp_mask_action_map.py --check
python scripts/generate_screen_action_catalog.py --check
python -m pytest tests/test_ki_voice_deep_link_params.py \
  tests/test_process_kernel_wave25_quick_actions.py \
  tests/test_mcp_mask_action_map.py --noconftest -q --override-ini addopts=''
```

## Grenzen / Weiter

- 31× `blocked_no_endpoint` erst nach SD-`commandEndpoint` + Mandanten-Service.
- FIN-CLOSE ADR-076 / Zahlauf unberuehrt; Stufe-2-SUS live.
- 2026-10-08: Deep-Link/AP/Inventur/Usability-Map in-scope committed/pushed
  (`MCP-CONSOLIDATE-COMMIT-20261008`). Optional weiter: HTTP-CommandEndpoints
  Personal/Fuhrpark; ADR-076-Review.
