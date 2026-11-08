---
title: RLS P5 Ausrollen per Ratsche (2026-10-26)
type: qa
audience: [entwickler, qa, betrieb, agent]
owner: Claude Code
status: active
last_reviewed: 2026-10-26
---

# RLS P5: Ausrollen per Ratsche (2026-10-26)

Phase P5, Zweig `claude/rls-p5-rollout-20261026` (gestapelt auf P4, PR #60).

## Vorgehen

`scripts/rls_rollout.py` teilt jede Klasse-A-Tabelle ohne RLS in **bereit** oder
**zurueckgestellt mit Grund** (`docs/admin/rls-rollout.json`). Gruende, bewusst vorsichtig
(dateiweit; Verweise ueber Tabellennamen und ueber ORM-Modellklassen):

| Grund | Tabellen | Bedeutung |
| --- | --- | --- |
| `standardmandant` | 80 | Datei mit Zugriff nutzt `DEFAULT_TENANT_ID`/`'default'` |
| `mandant_null` | 40 | Datei mit Zugriff fragt `tenant_id IS NULL` |
| `dienst` | 10 | Modell/Zugriff eines Dienstes unter `services/*` (eigene Engine, P6) |
| `identitaet` | 4 | Schluessel/Token: Nachschlagen vor der Mandantenbindung |
| `uebergreifend` | 3 | Zugriff aus mandantenuebergreifender Arbeit (P6) |
| `mandant_ermitteln` | 1 | `SELECT tenant_id FROM …` (ICS-Token) |

Ergebnis: **478 bereit, 111 zurueckgestellt** (Tabellen koennen mehrere Gruende haben).
Migration `rls_rollout_20261026` (nach `rls_pilot_finance_20261026`) setzt dieselbe Policy wie
der Pilot auf die 478 Tabellen; die Liste ist in der Migration fest. Danach: **500 Tabellen mit
RLS**, `ready` leer – jede neue Klasse-A-Tabelle landet dort und macht den Test rot.

Gepruefte Nicht-Betroffene: TypeScript-/Drizzle-Pakete legen ihre Tabellen in `public` an und
fragen keine Backend-Schemata ab; die Studio-Simulation arbeitet gegen den Pruefstand.

## Pruefung

`tests/test_rls_p5_rollout.py` (4): Analyse aktuell; keine Klasse-A-Tabelle ohne RLS und ohne
Grund; Analyse haelt riskante Faelle zurueck (synthetischer Selbsttest je Grund); gegen den
frischen Pruefstand (zurueckgerollt): alle 500 RLS-Tabellen tragen genau `tenant_isolation`
ohne `FORCE` mit erwartetem `USING`/`WITH CHECK`, und jede Policy wird als `valeo_app` mit und
ohne Mandant tatsaechlich ausgewertet (Typen, Funktionsrechte). Alle RLS-Tests P0–P5: 74 gruen.

## Grenzen – ehrlich

- Die Analyse ist heuristisch. Sie findet Code, der fremde Mandanten erwartet, ueber Muster;
  ein Zugriff ohne Muster (z. B. ein Vergleich ueber eine Variable mit Standardwert) kann ihr
  entgehen. Folge waere fail-closed: eine Maske zeigt leere Daten, kein Datenleck.
- Die bestehenden Anwendungstests verbinden als Superuser und pruefen RLS nicht.
- Empfehlung fuer die Integration: vor dem Ausrollen auf `valeo_neuro_erp` die Maskenabnahme
  (gewachsene Daten) mit dem integrierten Stand fahren; Rueckweg je Tabelle ist
  `DISABLE ROW LEVEL SECURITY` bzw. `alembic downgrade rls_pilot_finance_20261026`.
- Live (valeo_neuro_erp) ist nichts angewendet.
