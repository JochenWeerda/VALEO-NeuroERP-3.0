---
title: Handshake Laufzeit-DDL in Migrationen 2026-10-26
type: handshake
audience: [agent]
owner: Claude Code
status: aktiv
last_reviewed: 2026-10-26
---

# Handshake: Laufzeit-DDL in Migrationen

**Von:** Claude Code. **An:** Codex (Lead).
**Zweig:** `claude/runtime-ddl-migrations-20261026`, gestapelt auf PR #48.
**Nutzerfreigabe 2026-10-26:** Claude darf Codex-Aufgaben uebernehmen und teilt das per
Handshake mit. Dieser Handshake ist diese Mitteilung.

## Was ich in deinem Bereich geaendert habe

- **Endpunkte ohne DDL:** `accruals_provisions.py`, `ers_settlement.py`,
  `futtermittel_rezepte.py`, `futtermittel_rohwaren.py`, `opportunities.py`, `price_lists.py`,
  `sales_orders.py`, `sales_delivery_notes.py` fuehren kein `CREATE SCHEMA/TABLE` bzw.
  `ALTER … ADD COLUMN` mehr aus, auch keine `db.commit()` mitten im Request aus diesen
  Hilfsfunktionen. Fachlogik unveraendert (reine Loeschungen).
- **Pipelines:** `geo_pipeline.ensure_geo_schema`, `lkv_pipeline.ensure_lkv_schema`,
  `ensure_dairy_match_schema` pruefen nur noch per `app.core.schema_guard.require_tables`.
- **Migration** `runtime_ddl_to_migrations_20261026` (neuer Head): uebernimmt die Strukturen
  unveraendert mit `IF NOT EXISTS`; Downgrade bewusst leer.
- **Datenschutz:** `geo_pipeline.NOMINATIM_UA` enthielt eine persoenliche Kontaktadresse
  (Path-Guard schlug an). Jetzt aus `NOMINATIM_USER_AGENT`; in der Root-`.env` mit dem
  bisherigen Wert gesetzt. Fuer den Backend-Container muss die Variable nach dem Merge in
  `docker-compose.yml` durchgereicht werden. Die Adresse bleibt in der Git-Historie.
- Zwei Tests patchten die entfernten Helfer nur weg (`test_futtermittel_complete.py`,
  `test_einkauf_3way_match_ers_rfq.py`); die Patches sind entfernt, Assertions unveraendert.

## Bitte beachten

- Im Root-Arbeitsbaum zeigen diese Dateien bei dir nur Zeilenend-Aenderungen; keine
  inhaltliche Ueberschneidung festgestellt.
- Neue Endpunkte bitte ohne Laufzeit-DDL: Tabellen nur ueber Migrationen; fehlende
  Tabellen mit `require_tables` bzw. dem vorhandenen 503-Muster melden.
- **Backend auf `valeo_app`** (`docker-compose.yml`, `DATABASE_URL` des Backends) erst nach
  Merge dieses Zweigs und `alembic upgrade head` auf `valeo_neuro_erp`; Zugangsdaten stehen
  in der Root-`.env` (`VALEO_APP_DATABASE_URL`, Host dort `127.0.0.1`, im Container `postgres`).
