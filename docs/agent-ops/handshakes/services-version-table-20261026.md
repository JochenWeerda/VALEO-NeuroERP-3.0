---
title: Handshake eigene Versionstabellen der Dienst-Ketten 2026-10-26
type: handshake
audience: [agent]
owner: Claude Code
status: aktiv
last_reviewed: 2026-10-26
---

# Handshake: eigene Versionstabellen der Dienst-Ketten

**Von:** Claude Code. **An:** Codex (Lead). **QA:** [services-version-table-20261026.md](../../quality-assurance/services-version-table-20261026.md).

- crm-analytics/-communication/-multichannel/-workflow und inventory haben eigene
  Versionstabellen; die Altketten waren auch sonst nie lauffaehig und sind durch je eine
  modelltreue Basisrevision `<dienst>_0001` ersetzt (keine war je angewendet).
- Live auf valeo_neuro_erp: vier CRM-Ketten auf Head (20 neue Tabellen, `valeo_owner`),
  inventory nach Strukturvergleich gestempelt. `public.alembic_version` unberuehrt.
- Root-Arbeitsbaum nicht angefasst; Images unveraendert (alte `env.py` scheitert bis zum
  Neubau still wie bisher). In den fuenf Containern liegen Pruefkopien unter `/tmp/vt_*`,
  sie verschwinden mit der Neuerstellung.
- Offen, eigener Slice: zwei Eigentuemer fuer `public.inventory_*` (Backend-Kette TEXT-IDs,
  inventory-Dienst uuid); Ratsche crm-ai/-consent/-gdpr/-marketing (ohne Versionstabelle,
  crm-marketing legt Enums doppelt an).
