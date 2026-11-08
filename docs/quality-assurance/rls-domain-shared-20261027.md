---
title: QA RLS-DOMAIN-SHARED-20261027
type: qa
audience: [agent, entwickler]
owner: Claude Code
status: abgeschlossen
last_reviewed: 2026-10-27
version: 1.0.0
description: RLS-Domain shared (Niederlassungen, Stammdaten, Disponenten, Landwirte, Kalender, Nachrichten, Lastschriftposten, Futtermittel, Grundfutteranalysen, Konditionen, Nummernkreise) auf valeo_probe abgenommen, mit Fachkorrekturen an Mandant und Identitaet.
---

# QA RLS-DOMAIN-SHARED-20261027

**Basis:** `claude/rls-domain-einkauf-20261027` (#78, getestet 0ade49b36).
Migration `rls_domain_shared_20261027` folgt auf `rls_domain_einkauf_20261027`. `alembic heads` zeigt
einen einzigen Head.

**Status:** abgeschlossen. Prüfstandsfenster nach Freigabe durch Codex. `valeo_probe` stand vorher und
nachher auf `loading_stop_fk_20261023`, 0 fremde Sitzungen. Die gewachsene Datenbank wurde nur lesend geprüft.

## Analyse shared

| Tabelle | Befund | Entscheidung |
|---|---|---|
| `branches` (live 2) | **Fachbefund:** `branches.py` nahm `?tenant_id=` mit dem Standardmandanten als Rückfall (5 Wege) | Token; getrennt; Lieferschein und Ernteannahme verweisen über `(branch_id, tenant_id)` |
| `master_data_entries`, `dispatchers` | **Fachbefund:** `master_data.py` 11 Wege mit `?tenant_id=` und Standardmandant; Ändern/Löschen von Disponenten und Löschen von Kontaktarten **ohne Mandantenfilter** | Token; eigener Mandant je Weg, fremd 404 |
| `internal_messages` | **Fachbefund:** `?tenant_id=` mit Standardmandant; **Absender frei im Rumpf** (`sender_id`) | Token; Absender = geprüfter Nutzer (`bekannter_nutzer`) |
| `farmers` | **Fachbefund:** `agribusiness.py` `?tenant_id=` mit Standardmandant | Token |
| `grundfutter_analysen` (live 144) | **Fachbefund:** Mandant aus `X-Tenant-ID` mit Rückfall `"default"`; Portalzugang und Akteur aus **`X-User-Email`** | Token; E-Mail und Akteur aus den geprüften Claims |
| `rations_zugang` | **Fachbefund:** Aufrufer aus `X-User-Email`/`X-User-Name`, Rückfall `system@valeo.local` — wer eine E-Mail mit Verwaltungsrecht kannte, konnte sich DSGVO-Zugänge selbst vergeben | Aufrufer aus den Claims, ohne geprüfte E-Mail 403 |
| `zu_abschlag_konditionen` (C) | **Fachbefund:** `/pos/rabatte` und `/preise/konditionen` (Maskenbrücken) lasen Konditionen **aller Mandanten** | `tenant_id` von der Gruppe; Brücken filtern über die Gruppe |
| `futtermittel_einzelfutter` (live 743), `logistik_frachttabellen` | Matrix: „referenzdaten“ — die Treffer betreffen Nährstoffdefinitionen und Artikel, nicht diese Tabellen; live keine `system`-Zeile | getrennt, **kein** `system`-Lesen |
| übrige A-Tabellen (Sorten, Artikelsperren, Kalender, Lastschriftposten, Futteranalyse-Kinder, Misch-/Produktionsfutter, Rezepte, Rations-Zugang) | Schreiber tokengebunden; Standardmandant-Treffer waren Fehltreffer (`scope_code`, ICS-Nutzer, Fan-Gruppen) | getrennt |
| Kinder ohne Mandant (C): Thread-Audit, Rezeptkomponenten, Job-Artefakte, Provisionsstaffeln (+Zeilen, D), Zu-/Abschlagkonditionen | Mandant nur am Eltern | `tenant_id` vom Eltern, NOT NULL, Vorgabe aus dem Kontext, Verbund-FK (ON DELETE wie bisher) |
| `public.number_series` (nur frisch) | Vorgabe `'default'`; Schreiber `numbering_router.py`/`numbering_service_pg.py` sind nirgends eingebunden | NOT NULL, Vorgabe aus dem Kontext, getrennt |
| `domain_agrar.feeding_feed_*` (3), `delivery_notes`, `harvest_acceptances` | Einzel-FK auf Einzelfutter bzw. Niederlassung | Verbund-FK, Policies unverändert; SET NULL leert nur `branch_id` |

**Bewusst nicht in diesem Slice:** `users`, `admin_api_keys`, `api_keys`, `calendar_ics_tokens`
(Identität, Nachschlagen vor der Mandantenbindung), `outbox_events` (der Publisher liest mandantenübergreifend;
live 8 Zeilen mit `'default'`), `audit_logs` (eine `system`-Zeile), `policy_rules` (3 globale Regeln ohne Mandant).
Sie bleiben zurückgestellt, bis ihre Herkunft geklärt ist.

**Gewachsene DB (lesend):** keine Zeile ohne Mandant oder mit Platzhalter, kein Verweis auf einen Eltern
eines anderen Mandanten, keine Kinder ohne Eltern. Die Migration würde dort nicht abbrechen.

## Fachkorrekturen

- **Mandant aus dem Token** statt `?tenant_id=`/Kopf mit Standardmandant: `branches.py` (5), `master_data.py` (11),
  `messages.py` (2), `agribusiness.py` (2), `grundfutter_analysen.py` (8), `app/domains/agrar/api/psm.py` (21).
  Eingefrorene Rückfälle auf `"default"`: −1 (`grundfutter_analysen.py`), die übrigen liefen über
  `settings.DEFAULT_TENANT_ID` und tauchten in der Baseline nicht auf.
- **Fehlende Mandantenfilter:** Disponent ändern/löschen, Kontaktart löschen (`master_data.py`); POS-Rabatte und
  Preiskondition (`mask_frontend_bridges.py`).
- **Identität:** `messages.py` nimmt den Absender aus der Anmeldung statt aus dem Rumpf. `grundfutter_analysen.py`
  und `rations_zugang.py` lesen E-Mail und Namen aus den geprüften Claims (`app/core/akteur.py`:
  `gepruefte_email`, `gepruefter_name`) statt aus `X-User-Email`/`X-User-Name`.
- **Vertragstest geschärft:** `tests/test_keine_client_identitaet.py` erkannte die implizite Form
  `x_user_email: str = Header(None)` nicht (FastAPI leitet den Kopfnamen aus dem Parameter ab) und `sender_id` im
  Rumpf nicht. Beide Muster sind jetzt erfasst, mit Selbsttest.

## Nachweise

```
pytest tests/test_rls_domain_shared.py -rs     -> 63 passed, 0 skipped (valeo_app, zurueckgerollt)
Gegenprobe mit alten Einzel-FKs                -> 20 rot
Gegenprobe mit altem Code                      -> 13 rot (alle Fach-, Token- und Identitaetsvertraege)
RLS-Gesamtsuite + Fallback- und Identitaetsvertrag -> 548 passed, 0 skipped
149 betroffene Bestandsmodule (conftest, Pruefstand, Pakete nacheinander)
                                               -> 5416 passed; 27 rot wie auf der Basis #78 (0 neu rot)
Inventar/Rollout/Matrix/Systemlesen regeneriert, generate_code_inventories.py --check -> OK
```

| Abnahmekriterium | Test |
|---|---|
| Mandantengrenze je Tabelle (eigen ok; fremd und `system` SELECT/INSERT/UPDATE/DELETE gesperrt; kein `tenant_id`-Wechsel; fail-closed) | `test_mandantengrenze_je_tabelle` (27) |
| kein Verweis auf fremden Eltern, auch nicht umgehängt (auch aus anderen Domains) | `test_kein_verweis_auf_fremden_eltern` (19) |
| Kinder erben den Mandanten aus dem Kontext | `test_kind_erbt_den_mandanten_vom_kontext` |
| Nummernkreis-Vorgabe ist der Kontext | `test_nummernkreis_vorgabe_ist_der_kontext_nicht_default` |
| Eltern mit Verweisen behalten ihren Mandanten | `test_eltern_mit_verweisen_behaelt_seinen_mandanten` |
| Kontextwechsel/Savepoint, Hintergrund, Pool | `test_kontextwechsel_savepoint_hintergrund_pool` |
| Niederlassungen, Disponenten, Stammdaten, Nachrichten, Landwirte, Analysen, POS-Rabatte nur eigen, fremd 404 | `test_fachkette_*` (4) |
| Mandant aus dem Token für alle Datenbankwege der sechs Router | `test_wege_nehmen_den_mandanten_aus_dem_token` (6) |
| Absender und Aufrufer aus der Anmeldung | `test_nachricht_absender_aus_dem_token`, `test_rations_zugang_aufrufer_aus_dem_token` |

Die Fachketten laufen als Tabelleneigentümer (`RESET ROLE`), also ohne RLS: Sie prüfen den Code, nicht die
Policies. Zwei Tabellen sind nur zum Anhängen (`feeding_feed_analysis_revisions`, `domain_agrar.feeding_feed_revisions`,
Trigger gegen UPDATE/DELETE); für die Policy-Fälle wird der Trigger im zurückgerollten Savepoint abgeschaltet.

Die 27 vorbestehenden Fehlschläge (`test_studio_listen_kommandos` 14, `test_mcp_local_action_classification` 5,
`test_meridian_beleg_systemweit` 4 u. a.) sind mit und ohne diesen Slice gleich rot; 3 übersprungene Bestandstests
überspringen auch auf der Basis und zählen nicht als Abnahme.

Inventar: 86 zurückgestellt (−26; `vertreter_staffel_zeilen` stand als Klasse D nicht in der Liste).

## Verbleibend / vor Live-Aktivierung

- **Identität/Outbox/Audit/Regeln** (7 Tabellen, siehe oben): eigener Slice nach Klärung der Herkunft der
  `default`/`system`/NULL-Zeilen.
- `numbering_router.py`/`numbering_service_pg.py` sind toter Code mit `"default"`-Vorgaben (Baseline 7). Sie sind
  nicht eingebunden; unter RLS schlüge ein Schreiben mit `'default'` fehl (fail-closed). Entfernen ist ein eigener
  Aufräum-Slice.
- **Masken:** Niederlassungen, Stammdaten, Disponenten, Nachrichten, Landwirte, Grundfutter, Rations-Zugang,
  PSM, POS-Rabatte mit zwei Mandanten prüfen. Die Maskenabnahme liegt bei Codex.
