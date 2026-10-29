---
title: RLS P6 Systemrolle und Dienste (2026-10-26)
type: qa
audience: [entwickler, qa, betrieb, agent]
owner: Claude Code
status: active
last_reviewed: 2026-10-26
---

# RLS P6: Systemrolle und Dienste (2026-10-26)

Phase P6, Zweig `claude/rls-p6-system-role-20261026` (gestapelt auf P5, PR #61).

## Systemrolle (Nutzerentscheidung: eigene Rolle mit BYPASSRLS)

- `scripts/provision_db_roles.py`: neue Rolle `valeo_system` (LOGIN, Datenrechte wie
  `valeo_app`, als einzige `BYPASSRLS`, kein Superuser). Passwort nur aus
  `VALEO_DB_PASSWORD_SYSTEM`.
- **Live angewendet** auf `valeo_neuro_erp` (additiv, idempotent; 16 Rollen- und 355
  Rechte-Anweisungen, nur `valeo_system` neu). Die Rolle hat **kein Passwort**, ein Login ist
  erst nach Setzen von `VALEO_DB_PASSWORD_SYSTEM` moeglich.
- `app/core/database.py`: `system_session()` – nur innerhalb von `cross_tenant_scope`,
  verbindet ueber `SYSTEM_DATABASE_URL`; ohne Einstellung Anwendungsanmeldung (fail-closed).
  Compose: `SYSTEM_DATABASE_URL: ${VALEO_SYSTEM_CONTAINER_DATABASE_URL:-}`.
- Worker auf der Systemverbindung: Outbox-Versand, Compliance-Monitor und alle
  `@cross_tenant_job`-Jobs ueber `BaseWorker` (Berichte, Cleanup, Compliance-Check, GAP-Sync).
- Rollout-Analyse: `uebergreifend` blockiert nur noch, wenn mandantenuebergreifender Code
  **nicht** die Systemverbindung nimmt. Dadurch wurde `domain_erp.business_partners` frei;
  Migration `rls_system_role_20261026` setzt dort die Policy. **501 Tabellen mit RLS**,
  110 zurueckgestellt, `ready` leer.

## Dienste unter services/* – bewusst ohne RLS

Kein Dienst bindet seinen Mandanten an ein geprueftes Token; Mandant kommt aus Parametern mit
Rueckfall auf `default` (crm-core 22 Stellen, workflow 7, crm-security 5, inventory 4, die
uebrigen 1–2). Ein `app.tenant_id` aus dieser Quelle waere Scheinsicherheit. Voraussetzung fuer
RLS in den Diensten ist eine gepruefte Identitaet dort (eigenes Vorhaben). Abgesichert ist:
**kein Dienst liest eine Tabelle mit RLS** (Vertragstest), Dienste werden also nicht still blind.

## Pruefung

`tests/test_rls_p6_system_role.py` (4): `system_session()` nur im uebergreifenden Scope; nur
uebergreifender Code oeffnet sie; gegen den Pruefstand (zurueckgerollt) sieht dieselbe Abfrage
ohne Mandant als `valeo_app` 0 und als `valeo_system` 2 Zeilen; kein Dienst liest eine
RLS-Tabelle. Rollenplan-Tests 5 (nur `valeo_system` mit BYPASSRLS). Alle RLS-Tests: 82 gruen.
Worker-Suiten 130 gruen.
