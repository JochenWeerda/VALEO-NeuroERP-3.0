---
title: RLS P2 Mandant in jeder Transaktion (2026-10-26)
type: qa
audience: [entwickler, qa, agent]
owner: Claude Code
status: active
last_reviewed: 2026-10-26
---

# RLS P2: Mandant in jeder Datenbanktransaktion (2026-10-26)

Phase P2, Zweig `claude/rls-p2-db-context-20261026` (gestapelt auf P1, PR #57). Noch keine
Policy: das Verhalten aendert sich nicht.

## Aenderung

- `app/core/rls_session.py`, an die zentrale Engine gehaengt (`app/core/database.py`): vor
  jeder Anweisung wird der Mandant des Kontexts mit dem zuletzt gesetzten verglichen und nur bei
  Abweichung `set_config('app.tenant_id', <mandant>, true)` ausgefuehrt. Ohne Kontext: leer.
  Gilt fuer ORM-Sitzungen und direkte Verbindungen gleichermassen.
- Zwischenspeicher je Verbindung, verworfen bei Commit, Rollback, Savepoint-Rollback (nach der
  Anweisung) und Pool-Checkout.
- Metrik `db_transactions_without_tenant_total{scope=none|cross_tenant}`.

## Befund waehrend der Arbeit

Erster Entwurf setzte den Mandanten auch vor SQLAlchemys eigenen Steueranweisungen
(`SAVEPOINT`, `ROLLBACK TO SAVEPOINT`). Damit landete die Einstellung im Untertransaktionsteil,
den der Rollback zuruecknahm, waehrend der Zwischenspeicher den Wert noch fuer gesetzt hielt –
eine stille Abweichung. Der Savepoint-Test fand es; Steueranweisungen werden jetzt ausgelassen,
der Speicher nach dem Savepoint-Rollback verworfen.

## Pruefung (valeo_probe, echte Verbindungen)

`tests/test_rls_p2_db_context.py` (7): Engine ausgestattet; ohne Kontext leer; Scope;
Wechsel innerhalb einer Transaktion inkl. Cross-Tenant; nach Commit und bei Wiederverwendung
derselben Poolverbindung neu gesetzt; Savepoint-Rollback stellt den aeusseren Mandanten wieder
her; Wert ist transaktionslokal. Breite Gegenprobe (Mandanten-, Middleware-, Integrations-,
Worker- und RLS-Tests): 835 gruen, 4 uebersprungen.

Kosten: eine zusaetzliche Anweisung je Transaktion und Mandantenwechsel, keine je Abfrage.
