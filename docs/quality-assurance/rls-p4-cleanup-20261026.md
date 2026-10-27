---
title: RLS P4 Bereinigung der Testreste (2026-10-26)
type: qa
audience: [entwickler, qa, betrieb, agent]
owner: Claude Code
status: active
last_reviewed: 2026-10-26
---

# RLS P4: Bereinigung der Testreste (2026-10-26)

Phase P4, Zweig `claude/rls-p4-cleanup-20261026`. Nutzerentscheidung 2026-10-26: Testreste
in `valeo_neuro_erp` nach Inventar und Sicherung loeschen.

## Ablauf (live, valeo_neuro_erp)

1. **Inventar:** 77 verschiedene `tenant_id`-Werte. Echt: `…0001`, `…0051`, `system`.
2. **Sicherung:** `pg_dump -Fc` vor der Loeschung,
   `C:/Users/Jochen/valeo-backups/rls-p4-20261026/valeo_neuro_erp-vor-p4.dump` (6,2 MB,
   `pg_restore -l` lesbar, 818 Tabellendaten-Eintraege). Ausfuehrungsprotokoll daneben
   (`ausfuehrung.log`). Rueckweg: Wiederherstellung der betroffenen Tabellen aus der Sicherung.
3. **Skript** `scripts/rls_cleanup_test_tenants.py`: Trockenlauf als Standard, Ausfuehrung nur
   mit vorhandener Sicherung, eine Transaktion, Savepoints je Tabelle, Kindtabellen ohne
   `tenant_id` (Klasse C) ueber ihren Fremdschluessel. Erster Trockenlauf scheiterte an
   `bestellung_positionen` (Klasse C) – daraus entstand die Kinderloeschung.
4. **Ausgefuehrt:** 2 080 Zeilen in 51 Tabellen (u. a. 756 Audit-Logs, 379 Journalbuchungen,
   112 Agentenkontexte), 25 `test-<hex>`-Registereintraege. Alle Dienste danach healthy.

Geloeschte Muster: `test-<8 hex>`, `test-tenant`, `test-tenant-pos-001`,
`test-tenant-finance-001`, `tenant-a`, `tenant-a-persist`, `tenant-api-test`, `TENANT-TEST`,
`tenant-agent-persist`, `t1`. Der Registereintrag `test-tenant` bleibt (pytest-Suiten nutzen ihn
als Fremdschluesselziel). `tests/test_rls_p4_cleanup_patterns.py` (24) sichert die Muster ab.

## Nicht geloescht – Regel fuer den Rollout (P5)

| Wert | Zeilen | Tabellen | Behandlung |
| --- | --- | --- | --- |
| `NULL` | 54 | `feeding_reference_revisions` 22, `feeding_nutrient_definitions` 19, `feeding_unit_definitions` 8, `policy_rules` 3, `journal_entry_lines` 2 | Referenzdaten mit NULL = global: vor RLS auf diesen Tabellen zu `system` normalisieren; Journalzeilen fuellt P3 aus dem Kopf |
| `legacy-unassigned` | 80 | `ops_chargen` 79, `ops_fahrzeuge` 1 | fachlich zuzuordnen; unter RLS unsichtbar (fail-closed) |
| `default` | 53 | `edi_nachrichten` 31, `crm_sales_opportunity_stages` 8, `outbox_events` 8 u. a. | registrierter Altmandant; bleibt, sichtbar nur im Kontext `default` |
| `sd-ee9250d7` | 35 | `outbox_events` 25, `number_series` 7, `control_findings` 3 | Studio-Simulationskennung; unter RLS unsichtbar |
| `valeo` | 13 | Feldbuch, Abschlusschecklisten, Chargen, Einkauf | nicht registriert; unter RLS unsichtbar |
| `SYSTEM` | 5 | `aufbewahrungsfristen` | in P3 zu `system` normalisiert |
| `meridian-abnahme` | 1 | `recent_documents` | unter RLS unsichtbar |

Ein Fund floss zurueck in P3: die Platzhalter der Aufbewahrungsfristen standen unter `SYSTEM`.
