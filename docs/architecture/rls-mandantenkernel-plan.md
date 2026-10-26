---
title: Plan Mandantentrennung in der Datenbank (RLS)
type: explanation
audience: [entwickler, betrieb, agent]
owner: Claude Code
status: draft
last_reviewed: 2026-10-26
---

# Plan: Mandantentrennung in der Datenbank (RLS)

Slice `RLS-PLAN-20261026`. Anlass: Vergleich mit SAP S/4HANA (Nutzer, 2026-10-26). Uebernommen
wird ein Prinzip, nicht die Architektur: **Die Datenbank selbst verweigert fremde
Mandantenzeilen**, auch wenn eine Abfrage den Filter vergisst – so wie das ABAP-SQL-Interface
die Mandantenbedingung ergaenzt. Kein neues Framework; Aenderungen an den vorhandenen
Zugriffspfaden.

**Ziel:** Ein Fehler in einem Fachmodul oder in KI-generiertem Code kann keine Zeilen eines
fremden Mandanten lesen oder schreiben.

## 1. Ist-Stand (Inventar 2026-10-26, `valeo_neuro_erp`, lesend)

### Datenbank

| Befund | Zahl |
| --- | --- |
| Fachtabellen (31 Schemata, ohne `governance`) | 817 |
| davon mit `tenant_id` | 683 |
| … `tenant_id` nullbar | 34 Tabellen |
| ohne `tenant_id`, aber per FK an einer Mandantentabelle (Positionen, Zeilen) | 64 |
| ohne `tenant_id`, ohne solchen FK (Stammdaten/global oder verwaist) | 70, davon 13 mit Zeilen |
| Tabellen mit RLS | **0** |

- **Typ von `tenant_id`:** fast ueberall Text (`text`, `varchar`, sechs Laengen), `uuid` nur in
  einzelnen `public`-Tabellen. Eine Policy mit `::uuid`-Cast scheitert an Werten wie `system`.
- **Werte:** Hauptmandant `00000000-…-0001` (25 277 Zeilen, 151 Tabellen), daneben `…-0051`,
  `system` (6 Tabellen), `default`, `legacy-unassigned`, `NULL` (5 Tabellen) und Testreste
  (`test-tenant` 1 651 Zeilen in 23 Tabellen, `tenant-a`, `TENANT-TEST` …).
- **Rollen:** `valeo_app`, `valeo_agent`, `valeo_owner`, `valeo_migrator` ohne `SUPERUSER` und
  ohne `BYPASSRLS` (Rollentrennung #50/#51). Tabelleneigentuemer ist `valeo_owner`; der Migrator
  arbeitet als `valeo_owner`.
- **Dienste unter `services/*`:** zwoelf eigene Engines in derselben Datenbank (Tabellen in
  `public`, `tenant_id` als `varchar(64)`).

### Anwendung

| Befund | Fundstelle |
| --- | --- |
| **Eine** zentrale Engine fuer das Backend | `app/core/database.py` (`engine`, `SessionLocal`) |
| Vertrauenswuerdige Mandantenquelle: Tenant aus geprueftem Token, Kopfzeile wird ueberschrieben | `app/core/tenant_binding.py`, `app/core/identity_context.py` (`Principal.tenant_id`) |
| **Mandantenkontext ist fail-open:** ohne gesetzten Mandanten liefert `get_current_tenant_id()` still `DEFAULT_TENANT_ID` | `app/core/tenant_context.py`; 48 Verwendungen von `DEFAULT_TENANT_ID` |
| Middleware faellt im Dev-Modus auf den Standardmandanten zurueck | `app/middleware/tenant_enforcement.py` |
| Handfilter in SQL-Text (`tenant_id = :…`) | 2 463 Stellen |
| Handfilter im ORM (`.tenant_id ==`) | 834 Stellen |
| Sitzungen ausserhalb von Requests (`SessionLocal()`) | 45 Stellen in 21 Dateien, u. a. `workers/outbox_publisher.py`, `scheduler_service.py`, `mail_poll_worker.py`, `rag_indexer.py` |
| Direkte Verbindungen (`engine.connect/begin`) | 23 Stellen |
| Weitere Engines im Backend | `migration_session.py` (Migrator), `studio_process_simulation.py` |

Bewertung: Die Trennung haengt heute an ueber 3 200 einzelnen Filtern und an einem
Kontext, der bei Fehlen still auf einen Mandanten zurueckfaellt. Belegt ist die Isolation fuer
Teilbereiche (z. B. Fuhrpark/MCP, 581 Tests am 2026-10-09), nicht fuer alle Zugriffswege.

## 2. Zielbild

```
Request ─► Token geprueft ─► Principal.tenant_id ─┐
Worker ──► system_context(tenant, grund) ─────────┼─► Engine-Ereignis "begin":
                                                  │   set_config('app.tenant_id', <id>, true)
kein Kontext ─────────────────────────────────────┘   (leer, wenn kein Kontext)
                                                        │
PostgreSQL (valeo_app / valeo_agent, ohne BYPASSRLS) ◄──┘
  Policy je Mandantentabelle:
  tenant_id = NULLIF(current_setting('app.tenant_id', true), '')
```

1. **Setzen an einer Stelle.** Ein SQLAlchemy-Ereignis auf der zentralen Engine (`begin`) setzt
   `app.tenant_id` transaktionslokal (`set_config(…, true)`). Das erfasst ORM-Sitzungen und alle
   23 direkten Verbindungen gleichermassen; Poolverbindungen tragen nichts in die naechste
   Transaktion.
2. **Fail-closed.** Ohne Principal und ohne ausdruecklichen Systemkontext bleibt die Einstellung
   leer → `NULLIF` ergibt `NULL` → die Policy liefert keine Zeile und erlaubt keinen Schreibzugriff.
   Der Rueckfall auf `DEFAULT_TENANT_ID` entfaellt fuer Datenzugriffe.
3. **Textvergleich statt Cast.** `tenant_id` bleibt, wie es ist; die Policy vergleicht als Text.
   Fuer die wenigen `uuid`-Spalten: `tenant_id::text = …` (kein Cast der Einstellung, der an
   `system` scheitern wuerde). Indexnutzung bei `varchar`/`text` bleibt erhalten.
4. **Kein `FORCE`.** Policies gelten fuer `valeo_app` und `valeo_agent`. Der Eigentuemer
   (`valeo_owner`, also Migrationen) bleibt aussen vor – Datenmigrationen ueber alle Mandanten
   funktionieren weiter. Damit ist die Rollentrennung tragend: keine Anwendung darf als Eigentuemer
   oder Superuser verbinden (Vertragstest).
5. **Systemwege ausdruecklich.** Worker, die je Mandant arbeiten, setzen den Kontext je Durchlauf
   ueber `system_context(tenant, grund)` (protokolliert). Echte mandantenuebergreifende Jobs (z. B.
   Outbox-Versand) bekommen eine eigene Rolle mit `BYPASSRLS` und eigener URL, namentlich
   freigegeben – das Gegenstueck zu SAPs eingeschraenktem Native SQL.
6. **Kindtabellen.** Positionen ohne `tenant_id` (64): bevorzugt Spalte `tenant_id` nachziehen
   (Fuellung aus dem Kopf, NOT NULL, Policy wie oben); eine Policy mit `EXISTS` auf den Kopf nur,
   wo das Nachziehen nicht traegt.

## 3. Phasen

Jede Phase ist ein eigener Slice mit Abnahme auf frischer Datenbank (Schema) und gewachsener
Datenbank (Daten), siehe `docs/quality-assurance/pruefstand-datenbank.md`.

| Phase | Inhalt | Verhalten aendert sich? | Abnahme |
| --- | --- | --- | --- |
| **P0 Inventar als Werkzeug** | Skript, das die Tabellen klassifiziert (A: `tenant_id` NOT NULL, B: nullbar, C: Kind per FK, D: global) und die Codepfade zaehlt; Ratschen-Vertragstest: neue Mandantentabelle ohne Klassifikation ist rot | nein | Inventar reproduziert die Zahlen oben |
| **P1 Fail-closed-Kontext** | `get_current_tenant_id()` ohne Rueckfall fuer Datenzugriffe; `system_context()` fuer Worker; 21 Worker-Dateien darauf umstellen; Dev-Rueckfall der Middleware nur hinter ausdruecklicher Einstellung | ja, Fehler statt stiller Standardmandant | Worker-Tests; Negativtest: Zugriff ohne Kontext scheitert |
| **P2 Kontext in die Datenbank** | Engine-Ereignis `begin` setzt `app.tenant_id`; Metrik fuer Transaktionen ohne Kontext | nein (noch keine Policy) | Test: Einstellung ist je Transaktion gesetzt und nach Commit leer |
| **P3 Pilot** | RLS auf einer Domaene (Vorschlag: `domain_finance`, 18 Tabellen, alle mit `tenant_id` NOT NULL, Buchungen sind der teuerste Fehler); Cross-Tenant-Negativtests in CI (lesen, schreiben, aendern, loeschen fremder Zeilen) | ja, fuer diese Domaene | Gesamtsuite auf frischer DB gruen; gewachsene DB: Masken der Domaene abgenommen |
| **P4 Bereinigung** | Testreste und `legacy-unassigned` aus der gewachsenen DB, `NULL`-Mandanten klaeren, Regel fuer `system`-Zeilen | Daten | Inventar zeigt nur echte Mandanten |
| **P5 Ausrollen** | Domaene fuer Domaene per Ratsche (Liste der Tabellen ohne Policy darf nur schrumpfen); Kindtabellen mit `tenant_id` nachziehen | ja, schrittweise | je Domaene wie P3 |
| **P6 Dienste und Querschnitt** | `services/*` mit demselben Ereignis; mandantenuebergreifende Worker auf eigene `BYPASSRLS`-Rolle; Studio-Simulation | ja | wie P3 je Dienst |
| **P7 Absicherung** | Vertragstests: keine neue Engine/Verbindung ausserhalb freigegebener Pfade, jede Mandantentabelle hat Policy, keine Anwendung als Eigentuemer; CODEOWNERS fuer `app/core/database.py`, `tenant_*`, `alembic/versions/` | nein | Tests rot bei Umgehung (Negativprobe) |

Die Handfilter (3 297 Stellen) bleiben zunaechst bestehen: doppelt haelt besser, und sie
tragen die Indexnutzung. Entfernen ist kein Ziel dieses Plans.

## 4. Risiken

- **Stille Leere statt Fehler.** RLS liefert bei falschem Kontext leere Ergebnisse, keinen
  Fehler. Gegenmittel: P1 (fail-closed im Code, Fehler vor der Abfrage), Metrik aus P2,
  Negativtests, die ausdruecklich auf Fehlermeldung bzw. leere Menge pruefen.
- **Worker ohne Kontext** sehen nach P3 in der Pilot-Domaene nichts mehr. Deshalb P1 vor P3.
- **Leistung.** `current_setting` ist stabil je Abfrage; Policy-Vergleich nutzt vorhandene
  `tenant_id`-Indizes. Messung im Pilot an den teuersten Finanzabfragen.
- **Systemzeilen** (`system`, 6 Tabellen) werden ohne Regel unsichtbar. Klaerung in P4 vor dem
  Ausrollen auf diese Tabellen.
- **Gewachsene vs. frische DB.** RLS-Migrationen werden auf beiden geprueft; die gewachsene
  Datenbank hat Constraints verloren (CLAUDE.md, Pruefstand).

## 5. Offene Entscheidungen

| Frage | Empfehlung |
| --- | --- |
| Pilot-Domaene | `domain_finance` (klein, vollstaendig mit `tenant_id`, hoechster Schaden bei Fehler) |
| Bedeutung der `system`-Zeilen | lesbar fuer alle Mandanten, schreibbar nur ueber Eigentuemer/Migration (Policy `USING (tenant_id IN (<ctx>, 'system'))`, `WITH CHECK (tenant_id = <ctx>)`) |
| Mandantenuebergreifende Worker | eigene Rolle `valeo_system` mit `BYPASSRLS`, nur fuer namentlich freigegebene Worker, eigener Vertragstest |
| `FORCE ROW LEVEL SECURITY` | nicht setzen; Schutz ueber Rollentrennung (Anwendung ist nie Eigentuemer) |
| Typ von `tenant_id` vereinheitlichen | nicht als Voraussetzung; Textvergleich genuegt, Vereinheitlichung spaeter |

## 6. Bewusst nicht Teil dieses Plans

- RAP-artige transaktionale Geschaeftsobjekte (Sperren, Validierungsphasen) – eigener Plan.
- Entfernen der Handfilter.
- Eine zusaetzliche Abstraktionsschicht ueber SQLAlchemy.

Kein Nachweis vollstaendiger Sicherheit; der Plan beschreibt den Weg dorthin.
