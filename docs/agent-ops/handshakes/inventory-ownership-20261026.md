---
title: Handshake inventory-Dienst fuehrt public.inventory_* 2026-10-26
type: handshake
audience: [agent]
owner: Claude Code
status: aktiv
last_reviewed: 2026-10-26
---

# Handshake: inventory-Dienst fuehrt public.inventory_*

**Von:** Claude Code. **An:** Codex (Lead). **QA:** [inventory-ownership-20261026.md](../../quality-assurance/inventory-ownership-20261026.md).

- Nutzerentscheidung: der inventory-Dienst fuehrt `public.inventory_*`, das Backend liest nur.
- Neue Backend-Migration `inventory_service_shape_20261026` (Kopf nach
  `runtime_ddl_to_migrations_20261026`): ersetzt leere TEXT-Kompatibilitaetstabellen durch die
  Dienstform, bricht bei Zeilen ab. Live No-op.
- Achtung valeo_probe: steht auf der fremden Revision `loading_stop_fk_20261023`, die in
  diesem Zweig fehlt; `pruefstand_db.py` baut ohnehin neu, ein Upgrade an Ort scheitert.
- Neue Backend-Schreibwege in `public.inventory_*` muessen die Dienstform schreiben;
  `tests/test_inventory_service_shape.py` haelt die Tabellendefinitionen gleich.
