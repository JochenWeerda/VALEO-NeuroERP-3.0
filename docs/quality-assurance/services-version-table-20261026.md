---
title: Eigene Versionstabellen der Dienst-Ketten (2026-10-26)
type: qa
audience: [entwickler, qa, betrieb]
owner: Claude Code
status: active
last_reviewed: 2026-10-26
---

# Eigene Versionstabellen der Dienst-Ketten (2026-10-26)

Slice `SERVICES-VERSION-TABLE-20261026`, Zweig `claude/services-version-table-20261026`.
Vorstufe: [services-db-roles-20261026.md](services-db-roles-20261026.md) (Befund „fremde
Versionstabelle“).

## Ausgangslage

crm-analytics, crm-communication, crm-multichannel, crm-workflow und inventory lasen beim
Start `public.alembic_version` des Backends, fanden dessen Revision nicht und scheiterten
still. Beim Pruefen der Ketten zeigte sich: Sie haetten auch mit eigener Versionstabelle
nirgends laufen koennen.

| Dienst | Fehler der Altkette |
| --- | --- |
| alle vier CRM | Enum-Typen doppelt angelegt (`op.execute("CREATE TYPE …")` und implizit ueber `postgresql.ENUM(name=…)` in `create_table`) |
| alle vier CRM | Kette weicht von `app.db.models` ab: IDs `varchar` statt `uuid` (UUID-v7-Refactor aenderte nur die Modelle), `jsonb` statt `json`, `updated_at` nullbar |
| crm-communication, crm-multichannel | Revisions-ID 35/36 Zeichen, `version_num` ist `varchar(32)`; crm-communication zusaetzlich FK auf eine erst spaeter angelegte Tabelle |
| inventory | Kette deckt 1 von 8 Tabellen ab (Rest per `create_all`), Enum doppelt, Enum-Werte (`ObjectEvent`) und ID-Typ abweichend von Modell und Live-Tabelle |

Live gab es keine einzige Tabelle der vier CRM-Dienste. Keine Revision war je irgendwo
angewendet (Versionstabelle des Backends enthaelt nur Backend-Revisionen); keine Referenz
auf die Alt-IDs im Repository.

## Aenderung

- `services/{crm-analytics,crm-communication,crm-multichannel,crm-workflow,inventory}/alembic/env.py`:
  `version_table=VERSION_TABLE` (`<dienst>_alembic_version`) online und offline.
- `services/{crm-sales,crm-service}/alembic/env.py`: Versionstabelle auch im Offline-Modus
  (bisher nur online; `--sql` zielte auf die Backend-Tabelle).
- Altrevisionen entfernt, je eine Basisrevision `<dienst>_0001` per Autogenerate aus
  `app.db.models` gegen einen leeren Suchpfad auf valeo_probe (lesend, kein DDL); Downgrade
  entfernt auch die Enum-Typen.
- `tests/test_service_alembic_version_tables.py`: eigene Versionstabelle je Kette
  (Ratsche crm-ai/-consent/-gdpr/-marketing, laufen nicht), Eindeutigkeit, Revisions-ID ≤ 32,
  keine doppelte Enum-Anlage; Muster-Selbsttest.

## Pruefung

- Modelle in den Images identisch zum Repostand (alle fuenf).
- valeo_probe, je Dienst eine Transaktion mit `ROLLBACK`, Schemata `vt_chain`/`vt_model`:
  Basis-Upgrade vs. Modell-DDL (Mock-Engine) – Spalten, Typen, Nullbarkeit, Defaults, Enums,
  Indizes identisch; FK-Zeilen unterscheiden sich nur im Schemapraefix. Derselbe Vergleich
  zeigte mit der Altkette 18 bzw. 13 Spaltenabweichungen (Negativprobe). Downgrade raeumt
  Tabellen und Typen vollstaendig ab. Danach keine `vt_*`-Schemata.
- Vertragstest: Zweig 14 gruen; derselbe Test auf der Basis 5 rot (Versionstabelle,
  doppelte Enums, Revisionslaenge).

## Live (valeo_neuro_erp, Migrator-Anmeldung, Images unveraendert)

- crm-analytics/-communication/-multichannel/-workflow: `alembic upgrade head` aus einer
  Kopie unter `/tmp` im Container → je `<dienst>_0001 (head)`; 20 Tabellen, 16 Enum-Typen,
  4 Versionstabellen, Eigentuemer `valeo_owner`, `valeo_app` hat Daten- und Typrechte.
- inventory: Live-Tabellen (aus `create_all`) gegen Modell-DDL verglichen – Spalten, Enums,
  Constraints identisch; live zusaetzlich zwei Indizes der Backend-Kette
  (`ix_inventory_gr_tenant_po`, `ix_inventory_gr_lines_receipt`). Danach
  `alembic stamp inventory_0001`, kein DDL an Fachtabellen.
- `public.alembic_version` unveraendert (`runtime_ddl_to_migrations_20261026`).
- ORM-Probe je Dienst als `valeo_app`: alle Modelltabellen abfragbar (5/5/6/4/8).
- `governance.ddl_events`: 82 Ereignisse `valeo_migrator`/`valeo_owner`, Quelle
  „unbekannt“ – die Herkunftskennung kam ueber asyncpg nicht an. Rueckweg:
  `alembic downgrade base` je CRM-Dienst bzw. `DROP TABLE inventory_alembic_version`.

Die Images enthalten weiter die alte `env.py`; bis zum Neubau scheitert das Start-Upgrade wie
bisher still und harmlos. Mit neuem Image findet es die eigene Tabelle auf Head.

## Befund: zwei Eigentuemer fuer public.inventory_* (nicht geaendert)

Die Backend-Migration `wms_material_flow_stock_link_20260619` legt
`public.inventory_warehouses/locations/goods_receipts/goods_receipt_lines` mit
`TEXT`-IDs an, der inventory-Dienst modelliert dieselben Namen mit `uuid`. Live kam
`create_all` zuerst, auf frischer Datenbank (valeo_probe) die Backend-Kette. Dort scheitert
die inventory-Basis an „already exists“ und `create_all` an FK-Typen – wie vor diesem Slice.
Welche Seite fuehrt, ist eine Architekturentscheidung (vgl. `domain_inventory.inventory_lots`
im Backend); eigener Slice.

Keine Aussage ueber vollstaendige Sicherheit oder Gesamtfreigabe.

## CI-Abnahme

| Lauf | Ergebnis |
| --- | --- |
| Docs Build 40373715781 | success (nach Nachziehen von `docs/admin/migration-inventory.md`; die drei fehlenden Backend-Migrationen stammten aus #47/#49, Drift bestand auf der Basis) |
| Quality Gate 40373528238 | Path Guard, FSX, Improvement integrity, Secret Scan, Dependency Scan, WCAG, Production contract success; SBOM nach GitHub-504 beim syft-Download neu gestartet: success; Backend bricht wie auf der Basis am Doc-Drift-Gate ab (272 Befunde, identisch); Frontend-Unit wie auf der Basis rot (keine Frontend-Aenderung) |
