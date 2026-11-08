---
title: Smoke CI Migrationsumgebung
type: reference
audience: [entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-10-28
version: 1.0.0
description: Expliziter CI Migrationslogin fuer die bereitgestellte PostgreSQL Datenbank.
---

# Smoke CI Migrationsumgebung

Run40675694605 auf9bdbaef79 scheitert vor den Browsertests mit einer abgewiesenen
Anmeldung als valeo_migrator. Der Job stellt seinen eigenen PostgreSQL-Service
und DATABASE_URL bereit, kopiert aber auch die Beispielumgebung nach .env.
Alembic liest dort MIGRATION_DATABASE_URL:bei gleichem Ziel ist dieser Login
absichtlich vorrangig, wurde im CI-Service jedoch nicht angelegt.

Der Migrationsschritt setzt MIGRATION_DATABASE_URL nun explizit aus der
DATABASE_URL des Jobs. Der Beispielwert kann damit nicht uebernehmen. Dies
betrifft nur den CI-Migrationsprozess; Produktionsrollen, Anmelderegeln und
Mandantenschutz bleiben unveraendert. Keine neuen Ressourcen oder Secrets.

Die bestehenden Migration-Session-Vertraege pruefen die Auswahl und das
Owner-Rollenverhalten. Der echte Browser-Smoke-Nachweis erfolgt im neuen
GitHub-Lauf; diese Korrektur behauptet noch keinen abgeschlossenen Browsertest.

Abnahme:3 bestehende Migrationsvertraege bestanden (0.54s); Workflow-YAML
und exakte Bindung an DATABASE_URL statisch geprueft. Kein lokaler DB-Zugriff.
