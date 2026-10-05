---
title: Gemeinsamer Testprüfstand ohne Datenbankproliferation
type: reference
audience: [agent, entwickler, qa, betrieb]
owner: Codex
status: aktiv
last_reviewed: 2026-10-01
description: Verbindliche User-Vorgabe für alle Agenten zur Wiederverwendung vorhandener Testressourcen.
---

# Gemeinsamer Testprüfstand

User-Vorgabe vom 2026-10-01: keine neue Testdatenbank in Docker pro Test.
Die Regel gilt verbindlich für alle Agenten und steht in `AGENTS.md` sowie
der Pflicht-Startcheckliste. Ältere Anleitungen zur Anlage je Agent oder
Testsuite werden durch diese Vorgabe ersetzt.

## Ablauf

1. Workboard und Ressourcenbesitz prüfen. Den vorhandenen `valeo_probe` oder
   die bereits konfigurierte Testdatenbank verwenden; keine Namen aus
   Agenten-IDs, Zeitstempeln oder UUIDs ableiten.
2. `python scripts/pruefstand_db.py --status` liest nur den Migrationsstand.
   Der Aufruf ohne Option setzt den Prüfstand zurück und ist keine normale
   Testvorbereitung. `--keep` migriert und gehört in einen abgestimmten Claim.
3. Tests öffnen Sessions am bestehenden Prüfstand. Isolation erfolgt durch
   Transaktionen/Savepoints oder eigene Datensätze mit eindeutigen Kennungen.
   Aufräumen löscht ausschließlich die selbst angelegten Datensätze.
4. Frische-Schema-Abnahmen werden am selben Prüfstand mit einem abgestimmten
   Wartungsfenster durchgeführt. Keine Rücksetzung bei fremder Nutzung.
5. CI verwendet die Datenbank des Jobs; Tests erzeugen darin keine weiteren
   Datenbanken, Container oder Volumes. In-Memory-Tests benötigen keinen Docker.

Kein pauschales Docker-Prune und keine Löschung fremder Datenbanken, Images,
Container oder Volumes. Eine bereits laufende fremde Ressource ist keine
herrenlose Ressource. Diese Regel reduziert Datenbank-/Containerkopien; sie
behauptet keine automatische Verkleinerung der Docker-VM-Datei auf Windows.

## Umsetzung und Nachweis

Die eigenen PostgreSQL-Finanzfixtures akzeptieren jetzt den bereits vorhandenen
`valeo_probe` neben explizit konfigurierten Testdatenbanken; Entwicklungs-
datenbanken bleiben ausgeschlossen. Keine dieser Fixtures erzeugt eine
Datenbank oder einen Container.

**36 Finanz-/Import-/Transaktionsverträge grün auf `valeo_probe`**, ohne
Schema-Rücksetzung, Containeranlage oder Zusatzdatenbank.
Log: `artifacts/shared-probe-finance-tests.log`.

Der zuvor einmal für mehrere Finanztests angelegte eigene Prüfstand
`valeo_test_payment_01a0f3fc_20260930` ist nach erfolgreichem Wechsel und
Prüfung auf null laufende Verbindungen entfernt. Sein zuvor gemessener
Datenbankbestand betrug 43.578.159 Bytes. Andere vorhandene Prüfstände wurden
nicht gelöscht. Historische Abnahmeberichte behalten ihren damaligen
Prüfstand als Nachweis; ab dieser Vorgabe wird er nicht neu angelegt.
