---
title: QA RLS-DOMAIN-HR-20261027
type: qa
audience: [agent, entwickler]
owner: Claude Code
status: abgeschlossen
last_reviewed: 2026-10-27
version: 1.0.0
description: Nachweis für die RLS-Domain hr (Schulungen, Onboarding, Dienstplan, Person/Beschäftigung) mit getrennten Policies und Verbund-FKs der Kindtabellen.
---

# QA RLS-DOMAIN-HR-20261027

**Basis:** `claude/rls-domain-pricing-20261027` (#65), Zweig `claude/rls-domain-hr-20261027`.
Migration `rls_domain_hr_20261027` folgt auf `rls_domain_pricing_20261027`.

## Lieferung

| Datei | Änderung |
|---|---|
| `alembic/versions/rls_domain_hr_20261027.py` | getrennte Policies `tenant_isolation_*` (kein `system`-Lesen) auf `onboarding_checklists`, `training_courses`, `work_plan_assignments`, `person`, `employment`; `person`/`employment` tenant_id NOT NULL; Verbund-FKs `onboarding_runs → onboarding_checklists`, `training_assignments → training_courses`, `employment → person`; Abbruch bei Platzhalter-Mandanten und bei Kindern unter fremdem Elternsatz; fehlende Tabellen werden übersprungen (`person`/`employment` gibt es live nicht) |
| `tests/rls_domain_support.py` | gemeinsame Prüfhilfe für alle Domain-Slices: Prüfstand-Transaktion, generische Zeilenanlage aus dem Katalog, Abnahmefälle je Tabelle, Kontextwechsel/Savepoint, Hintergrund, Pool |
| `tests/test_rls_domain_hr.py` | 14 Tests als `valeo_app` |
| Inventare, `rls-exceptions.json` | 508 Tabellen mit RLS, 207 zurückgestellt (−5) |

Keine Fachkorrektur nötig. `app/api/v1/endpoints/training.py`, die Command-Handler und die
MCP-Wege filtern durchgehend über den tokengebundenen Mandanten (`app.core.tenant`). Die
Matrix-Fundstellen `mcp_execution_service.py:3155` (betrifft `inventory_lot_movements`) und
`mask_frontend_bridges.py:972` (ID-Platzhalter `"default"`) sind Fehltreffer der dateiweiten
Heuristik.

## Nachweise (valeo_probe, zurückgerollt; Rolle valeo_app)

```
python scripts/pruefstand_db.py --status  -> Revision loading_stop_fk_20261023 (unverändert)
pytest tests/test_rls_domain_hr.py        -> 14 passed
pytest tests/test_rls_*.py tests/test_provision_db_roles.py
  -> 132 passed, 1 failed (bekannter P5-Formtest, Codex-Besitz, siehe Handshake)
```

| Abnahmekriterium | Test |
|---|---|
| eigener Mandant anlegen/ändern/löschen; fremder Mandant SELECT/INSERT/UPDATE/DELETE gesperrt; `system`-Zeilen nicht lesbar, nicht änderbar, nicht löschbar, nicht übernehmbar; `tenant_id`-Wechsel zu B oder `system` gesperrt; ohne Kontext fail-closed | `test_mandantengrenze_je_tabelle` (5 Tabellen) |
| kein Verweis auf fremde Elternsätze, auch nicht durch Umhängen | `test_kein_verweis_auf_fremde_elternsaetze` (3 Beziehungen) |
| Elternsatz mit Kindern kann den Mandanten nicht wechseln (auch nicht als Eigentümer) | `test_elternsatz_kann_den_mandanten_nicht_mitnehmen` |
| Kontextwechsel und Savepoint-Rollback ohne Übertrag | `test_kontextwechsel_und_savepoint` |
| Pool-Wiederverwendung ohne Mandantenübertrag | `test_pool_wiederverwendung` |
| Hintergrundarbeit nur mit ausdrücklichem Kontext; `valeo_system` sieht alles | `test_hintergrund_nur_mit_ausdruecklichem_kontext` |
| Fachkette über `training.py`: Kurs anlegen, listen und ändern, Zuweisung, Checkliste, Onboarding-Lauf; fremder Mandant 404 bei Ändern, Löschen, Zuweisen und Lauf; Löschen kaskadiert | `test_fachkette_schulung_und_onboarding` |
| Policy-Form `getrennt`, tenant_id NOT NULL | `test_policy_form_und_pflichtmandant` |

**Gegenprobe:** Zwei Mutationen der Migration wurden ausgeführt und danach zurückgenommen.
- Ohne Verbund-FKs: 4 Tests rot.
- Zusätzliche ALL-Policy mit `system`: 8 Tests rot.

## Befunde und Risiken

- **Seed-Zeilen der frischen Installation** (`hr_training_onboarding_module_20260215`) gehören
  dem Standardmandanten `00000000-…-0001`: eine Checkliste und zwei Kurse. Sie bleiben
  dort, nichts wird umgehängt. `training.py` filterte schon vorher nach Mandant, andere
  Mandanten sahen sie also auch bisher nicht. Ob Vorlagen künftig als `system` lesbar sein
  sollen, ist eine fachliche Entscheidung (Eintrag in `system_lesbar`).
- **Kindtabellen** `onboarding_runs`/`training_assignments` behalten ihre P5-Policies, nur
  der FK ist neu. Live: 0 Zeilen, keine Abweichungen.
- **Vor der Live-Aktivierung** sind abzunehmen: Masken Schulungen, Onboarding und
  Dienstplan-Zuweisung (`/personal/work-plan/assignments`) mit zwei Mandanten. Worker:
  keine.
- Der P5-Formtest bleibt rot, bis Codex' Fassung ein eigenes SELECT ohne `system` zulässt
  (Handshake).
