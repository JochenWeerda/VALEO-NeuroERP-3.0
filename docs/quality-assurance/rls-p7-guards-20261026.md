---
title: RLS P7 Absicherung und Gesamtstand (2026-10-26)
type: qa
audience: [entwickler, qa, betrieb, agent]
owner: Claude Code
status: active
last_reviewed: 2026-10-26
---

# RLS P7: Absicherung gegen Umgehung, Gesamtstand P0–P7 (2026-10-26)

Phase P7, Zweig `claude/rls-p7-guards-20261026` (gestapelt auf P6, PR #62).

## Aenderung

- `app/core/rls_guard.py`, beim Start aus `main.py`: prueft, ob die Anwendungsverbindung RLS
  umgeht (Superuser, `BYPASSRLS`, Mitglied von `valeo_owner`). Produktion: Start verweigert.
  Entwicklung: Fehlerprotokoll und Metrik `rls_ineffective_connection`. Anlass:
  docker-compose faellt ohne `VALEO_APP_CONTAINER_DATABASE_URL` auf den Superuser zurueck.
- Vertraege: eigene Engines im Backend nur in `database.py`, `migration_session.py`,
  `studio_process_simulation.py`; keine Treiberverbindungen.
- `.github/CODEOWNERS`: `database.py`, `rls_*`, `base_worker.py`, `scripts/rls_*`,
  `provision_db_roles.py`, `docs/admin/rls-*.json` (`tenant*` und `alembic/` waren schon erfasst).

## Pruefung

`tests/test_rls_p7_guards.py` (5): Engine-Freigabeliste, keine Treiberverbindungen,
CODEOWNERS-Abdeckung, Start in Produktion verweigert / in Entwicklung gemeldet, Rollenpruefung
gegen die Datenbank (Superuser erkannt, `valeo_app` sauber, `valeo_system` meldet BYPASSRLS).
Live verbinden alle Dienste als `valeo_app`. Gesamtlauf RLS-, Rollen-, CODEOWNERS- und
Worker-Tests: 168 gruen; Start-Tests mit `APP_ENV=production`: 23 gruen.

## Befund ohne Aenderung

Die produktive App (`main.py`) setzt den Mandanten in `BearerAuthMiddleware` aus dem
**gepruefen Token**; die `TenantEnforcementMiddleware` (Kopfzeile, Dev-Rueckfall) haengt nur in
der Test-App `app/main.py`. Das laufende Backend hat `API_DEV_TOKEN` gesetzt, die
Bearer-Middleware wertet es aber nicht aus (toter Rest).

## Gesamtstand P0–P7

| Phase | PR | Ergebnis |
| --- | --- | --- |
| P0 Inventar | #56 | `rls_inventory.py`, Klassen A/B/C/D, Codepfade, Ratsche |
| P1 fail-closed | #57 | kein Standardmandant mehr, `tenant_scope`/`cross_tenant_scope`, Worker je Mandant |
| P2 Kontext in der DB | #58 | `app.tenant_id` je Transaktion (Savepoint-Befund behoben) |
| P3 Pilot | #59 | 22 Tabellen (`domain_finance` + Journal), Verhaltenstests als `valeo_app` |
| P4 Bereinigung | #60 | live 2 080 Testrest-Zeilen geloescht (mit Sicherung) |
| P5 Ausrollen | #61 | 478 Tabellen, Analyse mit Gruenden, Ratsche `ready` leer |
| P6 Systemrolle | #62 | `valeo_system` (live, ohne Passwort), uebergreifende Worker, Dienste abgesichert |
| P7 Absicherung | dieser | Startwaechter, Engine-Vertrag, CODEOWNERS |

**Stand:** 501 von 609 Klasse-A-Tabellen mit RLS (frisches Schema), 110 mit Grund
zurueckgestellt; Klasse B (54), C (53), D (60) noch ohne Policy. **Live (`valeo_neuro_erp`) ist
keine Policy aktiv** – die Migrationen greifen erst mit dem integrierten Code (P1+P2 muessen mit).

## Offen

- Zurueckgestellte Tabellen einzeln klaeren (v. a. `standardmandant` 80, `mandant_null` 40).
- Klasse B: NULL-Mandanten normalisieren (Referenzdaten → `system`), dann Policy.
- Klasse C: `tenant_id` nachziehen (Positionen), dann Policy.
- Dienste unter `services/*`: tokengebundene Identitaet als Voraussetzung.
- Bei Integration: Passwort und URL fuer `valeo_system` setzen; Maskenabnahme mit gewachsenen
  Daten vor dem Live-Rollout.
