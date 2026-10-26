---
title: Laufzeit-DDL in Migrationen (2026-10-26)
type: qa
audience: [entwickler, qa, betrieb]
owner: Claude Code
status: active
last_reviewed: 2026-10-26
---

# Laufzeit-DDL in Migrationen (2026-10-26)

Slice `RUNTIME-DDL-MIGRATIONS-20261026`, Zweig `claude/runtime-ddl-migrations-20261026`,
gestapelt auf PR #48 ([db-roles-rollout-20261026.md](db-roles-rollout-20261026.md)).
Nutzerfreigabe: Codex-Aufgaben uebernehmen, per Handshake mitteilen
([Handshake](../agent-ops/handshakes/runtime-ddl-migrations-20261026.md)).

## Ausgangslage

Unter `valeo_app` (kein CREATE) scheitert jede DDL, auch `CREATE … IF NOT EXISTS` auf
Vorhandenes, weil PostgreSQL das Recht vor der Existenz prueft (per Login belegt). Inventur
ueber `CREATE/ALTER/DROP/COMMENT/TRUNCATE/REFRESH/CREATE INDEX/OR REPLACE` in `app/`:

| Stelle | Objekte | Migration vorher | Massnahme |
| --- | --- | --- | --- |
| `accruals_provisions.py` (2x) | `domain_erp.accruals_provisions` | ja | DDL entfernt |
| `ers_settlement.py` | `domain_einkauf.ers_suppliers`, `ers_invoices` | nein | Migration, DDL entfernt |
| `futtermittel_rezepte.py` / `futtermittel_rohwaren.py` | 4 Tabellen `domain_futtermittel` | nein | Migration, DDL entfernt |
| `opportunities.py` | 5 Spalten `public.opportunities` | ja | DDL entfernt |
| `price_lists.py`, `sales_orders.py`, `sales_delivery_notes.py` | Schemata | ja | DDL entfernt |
| `geo_pipeline.py` | `gap_map_points` + 2 Indizes | Tabelle ja, `idx_mappoints_geo` nein | Migration, `ensure_geo_schema` prueft nur |
| `lkv_pipeline.py` | `dairy_herd_performance`, `dairy_kunden_match` + 3 Indizes | teils | Migration, `ensure_*` pruefen nur |
| Studio (`studio_entity_compiler/evolution`) | erzeugt DDL als `migration.py`-Artefakt, fuehrt sie nicht aus | - | unveraendert |
| `compliance_whistleblower`, `wf_cockpit_persist_schemas`, `kunden_backfill` | DDL nur im Docstring | - | unveraendert |

Strukturen der Entwicklungsdatenbank deckten sich mit der Laufzeit-DDL (Spaltenzahlen).
Migration `runtime_ddl_to_migrations_20261026`: unveraenderte Strukturen, `IF NOT EXISTS`,
Downgrade bewusst leer (Objekte koennen vorher zur Laufzeit entstanden sein und Daten
enthalten). `app.core.schema_guard.require_tables` meldet fehlende Tabellen klar.

Nebenbefund: `geo_pipeline.NOMINATIM_UA` enthielt eine persoenliche Kontaktadresse (vom
Path-Guard erkannt); jetzt `NOMINATIM_USER_AGENT` aus der Umgebung, Platzhalter in
`.env.example`, bisheriger Wert in der Root-`.env`.

## Abnahme auf valeo_probe (41 betroffene Testdateien)

| Lauf | Aufbau | Ergebnis |
| --- | --- | --- |
| Basis, Superuser | Basis-Worktree `880d4f967`, frisch + `init_db.py` | 21 failed, 2073 passed, 1 skipped (49:31 min) |
| PR, Superuser | PR-Zweig frisch + `init_db.py` + Einrichtung | 22 failed: Basis-21 + `test_security_sales_orders::…scopes_final_update_by_tenant` (2:44 min) |
| PR, **valeo_app** | wie oben, Anwendung als `valeo_app` | 22 failed: Basis-21 + `test_check_schema_drift::…echte_abweichung` (2:27 min) |

- `test_security_sales_orders`: Der Test speist je `execute` eine Antwort ein; das entfernte
  `CREATE SCHEMA` verbrauchte eine. Indizes um eins verschoben, Assertions unveraendert.
- `test_check_schema_drift`: legt absichtlich Schemata an wie ein Migrationswerkzeug; nutzt
  jetzt `migration_database_url()`. Als `valeo_app` mit Migrator und als Superuser gruen,
  keine Reste.
- Nach beiden Anpassungen entspricht der `valeo_app`-Lauf der Basis-Fallmenge (21
  vorbestehend rot); keine Funktion der betroffenen Bereiche braucht DDL-Rechte mehr.
- Die Laufzeit sank von rund 50 auf unter 3 Minuten; Ursache nicht untersucht (vermutlich
  die Laufzeit-DDL je Request im Basis-Code).
- Rueckbau: `loading_stop_fk_20261023`, 767 Tabellen, keine Trigger, keine Sitzungen;
  Basis-Worktree entfernt.

## Offen

- Backend-Container auf `valeo_app` (`docker-compose.yml`): erst nach Merge und
  `alembic upgrade head` auf `valeo_neuro_erp`, weil der laufende Container den Code des
  Root-Arbeitsbaums (noch mit Laufzeit-DDL) ausfuehrt. `NOMINATIM_USER_AGENT` dort
  durchreichen.
- `create_tables()` beim Start: mit vollstaendigem Schema ohne DDL; fehlende ORM-Tabellen
  entstehen ueber `init_db.py` (Migrator).
- Keine Aussage ueber vollstaendige Sicherheit oder Gesamtfreigabe.

## CI-Abnahme

| Lauf | Commit | Ergebnis |
| --- | --- | --- |
| Security Scan 40320127260 | fb52b9287 | alle Jobs success |
| Quality Gate 40320121984 | fb52b9287 | eigener Folgefehler: Godfile-Ratsche verlangte, die Grenzlinie von `sales_orders.py` (1085 -> 1084) zu senken; in f8f016d86 nachgezogen |
| Quality Gate 40321373513 | f8f016d86 | Improvement integrity, Dependency Scan, FSX, Secret Scan, SBOM, WCAG, Production contract u. a. success; Frontend-Unit 214 Faelle mit identischer Fallmenge wie Basis-Lauf 40234161888 (0 neu); Backend bricht wie auf der Basis am Doc-Drift-Gate (272) ab |
