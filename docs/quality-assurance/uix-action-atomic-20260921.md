---
title: Verbindliche Persistenz fuer Maskenaktionen
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-09-21
description: Atomare Mutation, Audit und Outbox ohne simulierten Erfolg bei Datenbankfehlern.
---

# Persistenzvertrag der gemeinsamen Masken-Runtime

`run_mask_action` meldet Erfolg erst nach erfolgreichem Commit. Fehler in
Mutation, Audit, Outbox oder Commit fuehren zum Rollback und einem Fehler ohne
erfundene Audit-/Outbox-IDs. Der bisherige Erfolg nach fehlenden Tabellen ist
entfernt. Audit-/Outbox-Exceptions werden nicht mehr verschluckt. Unbekannte
Modi werden vor jedem Handler-Aufruf abgewiesen; sie fallen nicht auf execute
zurueck. Fehlende `_mode` bleibt fuer bestehende Aufrufer execute.

Die bereits verwendete Tabelle `domain_crm.crm_action_audit_log` fehlte sowohl
in den Migrationen als auch in der lokalen PostgreSQL-Datenbank. Die additive
Migration `mask_action_audit_20260921` ergaenzt sie mit Tenant-/Entitaetsindex.
Ein Downgrade loescht keine Audit-Daten, sondern stoppt explizit. Anwendungscode
kann zurueckgerollt werden, waehrend das Audit-Schema erhalten bleibt.

## Nachweise

- `python -m pytest tests/test_mask_action_atomic.py tests/test_spec_p1_04_mask_commands.py --noconftest -q --override-ini addopts=''`: **22 bestanden**.
- Negative Tests fuer ungueltige Modi, Mutation, Audit, Outbox und Commit.
- SQLite: echte Mutation wird bei fehlender Audit-Tabelle zurueckgerollt;
  positiver Commit speichert Fachwert und die zurueckgegebene Audit-ID.
- PostgreSQL 15 im lokalen Backend-Container: neue Migration in einer aeusseren
  Transaktion ausgefuehrt; Mutation, Audit und Outbox mit echten SQL-Abfragen
  nachgewiesen. Erzwungener Tabellenfehler rollt den zweiten Schreibversuch
  zurueck. Test-DDL und synthetische Daten anschliessend vollstaendig rollback.
  Lokales Nachweisskript: `artifacts/test_mask_atomic_postgres.py`.
- Danach lokales `alembic upgrade mask_action_audit_20260921` erfolgreich.
  Versionsabfrage und `to_regclass` bestaetigen Revision und Audit-Tabelle.

## Noch offene Arbeit

Dieser Nachweis betrifft die gemeinsame Runtime, nicht die Persistenz jedes
Fachhandlers. Einige Handler liefern weiterhin nur eine `mutation`-Beschreibung.
Sie muessen vor produktiver MCP-Freigabe an echte Fachservices angeschlossen
werden. Handler duerfen nicht selbst vorzeitig committen. Der separate
CRM-360-Aktionspfad ist nicht durch diese gemeinsame Runtime abgedeckt.
Idempotente Wiederholung, Agent-Berechtigungen und Approval-Bindung sind fuer
den echten MCP-Schreibadapter weiterhin nachzuweisen.

Architektur-Impact: bestehender Vertrag wird durch fehlenden Audit-Speicher
vervollstaendigt; keine neue API, kein neuer Container, keine Domänengrenze.
UIX/MCP-Gesamtziel weiterhin offen.
