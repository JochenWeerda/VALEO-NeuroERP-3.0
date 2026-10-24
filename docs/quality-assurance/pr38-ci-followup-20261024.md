---
title: PR38 CI-Nachlauf nach Workspace-Reparatur
type: reference
owner: Codex
status: migrationsfix-geprueft
last_reviewed: 2026-10-24
---

# Nachlauf auf 7bc7e37fa

Die neun Workspace-Reviewbefunde sind als eigene Abnahme geschlossen. Der
anschliessende Gesamt-CI-Lauf besitzt weitere, getrennt zu reparierende Befunde.

## Gesichert

- Mehrere Backend-, Strict-DB- und Service-Smoke-Jobs scheitern an derselben
  fehlenden Revision dms_inbox_tenant_20261022. Die Datei liegt in der geprueften
  Reparaturansicht, ist aber noch nicht in HEAD. Der Wiederherstellungsstand
  besteht check_alembic_single_head und py_compile; einziges Head bleibt
  loading_stop_fk_20261023. Keine Datenbank wurde migriert oder zurueckgesetzt.
- Alle437 Migrationsdateien stimmen nach LF-Normalisierung byteinhaltlich mit
  dem separat geprueften PR39-Stand ueberein. Das Migrationsinventar ist in der
  Reparaturansicht synchronisiert. Ein neuer Frischschema-/CI-Nachweis nach dem
  Commit bleibt erforderlich. Kein Tabellenkatalog wurde aus der lokalen Probe
  blind als frisches Schema uebernommen.
- Der Backendmaskenlauf hat genau einen Fehler: ein CRM-Strukturtest verlangt
  die alte ternary-Schreibweise. Der aktuelle Adapter besitzt explizite Lead-
  und Customer-Zweige. Der Test muss mit einem echten Rendervertrag fuer beide
  Arten aktualisiert werden; bislang keine Testaenderung oder Abschwaechung.

## Weiter offen

Sicherheitsfixes aus PR39 nach Quellenvergleich nachziehen, Frontendfehler
zwischen tatsaechlicher Funktionsluecke und veraltetem Strukturtest trennen,
kanonische Artefakte nach Integration erzeugen und neue CI-Abnahme abwarten.
Alte Studio-, API- und Fremdaenderungen bleiben erhalten.

## Ausfuehrungsgrenze

Der zusaetzliche Claim-Commit wurde nicht ausgefuehrt: automatische
Freigabepruefung konnte wegen Nutzungslimit nicht abgeschlossen werden.
Es war keine inhaltliche Ablehnung. Subagenten stoppten ebenfalls am Limit.
Keine Umgehung, kein Commit/Push dieser vorbereiteten Aenderungen behauptet.


## Fortsetzung

Die zuvor gemeldete Resetzeit ist verstrichen. Der Migrationsvorgaenger und
das aktualisierte Inventar werden als eigener Meilenstein integriert; die
weiteren Security-/Frontendbefunde bleiben bis eigener Abnahme offen.
