---
title: RLS P0 Inventar (2026-10-26)
type: qa
audience: [entwickler, qa, agent]
owner: Claude Code
status: active
last_reviewed: 2026-10-26
---

# RLS P0: Inventar als Werkzeug (2026-10-26)

Slice `RLS-P0-INVENTORY-20261026`, Plan `docs/architecture/rls-mandantenkernel-plan.md` (PR #55).

## Ergebnis

- `scripts/rls_inventory.py` erzeugt `docs/admin/rls-inventory.json`: Tabellen der frischen
  Datenbank mit Klasse (A `tenant_id` NOT NULL, B nullbar, C Kind per FK, D ohne), Typ,
  RLS-Status, Policies; dazu die Codestellen, die die Mandantenbindung umgehen oder ersetzen
  koennen. `--check` meldet Drift, `--code-only` aktualisiert nur die Codepfade.
- valeo_probe stand auf `loading_stop_fk_20261023`, vier Revisionen hinter dem Kopf. Das Skript
  spielte sie in einer Transaktion ein und rollte zurueck; danach unveraendert (Revision gleich,
  kein `governance`-Schema, kein Event-Trigger, Kompatibilitaetstabellen weiter TEXT).
- `tests/test_rls_inventory_contract.py`: Selbsttest der Klassen und Codemuster, Codepfade
  aktuell (ohne DB), Inventar in sich stimmig, Tabellen gleich frischem Schema (integration,
  braucht `TEST_DATABASE_URL`). 5 gruen.
- Negativproben: neue `SessionLocal()`-Stelle in `app/` → rot mit Datei; aus dem Inventar
  entfernte Tabelle → rot mit Tabellenname.

## Zahlen (frisches Schema, Kopf `inventory_service_shape_20261026`)

| | |
| --- | --- |
| Tabellen | 775 (gewachsene DB: 817) |
| A / B / C / D | 608 / 54 / 53 / 60 |
| mit RLS | 0 |
| Typen von `tenant_id` | 11, davon `uuid` in 4 Tabellen |

Codepfade (ohne Tests und Migrationen):

| Muster | Dateien | Stellen | auffaellig |
| --- | --- | --- | --- |
| `SessionLocal()` | 27 | 52 | `app/core/container_config.py` (18), Pipelines, Scheduler, Studio-Entwuerfe |
| `engine.connect/begin` | 9 | 25 | `app/core/database.py` (14), Studio-Simulationen |
| eigene Engine | 20 | 21 | Migrator, Studio-Simulation, je Dienst unter `services/*` |
| Treiberverbindung | 0 | 0 | |
| `DEFAULT_TENANT_ID` | 55 | 85 | `knowledge_api.py` (8), crm-core-Endpunkte, Webhooks, `channel_ingress.py` |

Handfilter nur zur Information (nicht geprueft, aendern sich mit jeder Fachfunktion): 2 471 in
SQL-Text, 877 im ORM.

## Befunde fuer die naechsten Phasen

- **Pilot `domain_finance`:** frisch 20 Tabellen (18 A, 2 B: `period_closure`, `sales_order`),
  gewachsen 18 (alle A; die zwei B-Tabellen fehlen dort). **Das Buchungsjournal liegt nicht in
  `domain_finance`**, sondern in `domain_erp.journal_entries` (A) und `journal_entry_lines` (B);
  die gewachsene DB hat zusaetzlich `domain_erp.finance_journal_*` und
  `domain_shared.journal_entries`, die keine Migration anlegt. Die Begruendung des Plans fuer den
  Piloten ist zu korrigieren; Rueckfrage an den Nutzer.
- **P1:** `DEFAULT_TENANT_ID` in 55 Dateien, auch in Diensten unter `services/*`;
  `container_config.py` oeffnet 18 Sitzungen ausserhalb von Requests.
- **Frisch vs. gewachsen:** B ist frisch 54, gewachsen 34 – die gewachsene DB hat Tabellen und
  NOT-NULL-Regeln, die keine Migration beschreibt. Policies werden auf beiden geprueft.

## CI

Der Backend-Job der Quality Gate bricht vor pytest am Doc-Drift-Gate ab (vorbestehend, 272
Befunde, mit diesem Slice unveraendert); der Integrationstest laeuft daher in CI derzeit nicht.
Lokal gegen valeo_probe gruen.

Keine Aussage ueber vollstaendige Sicherheit oder Gesamtfreigabe.
