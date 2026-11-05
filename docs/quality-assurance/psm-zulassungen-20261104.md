---
title: PSM-Zulassungen - Pruefstand und Grenzen
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-11-04
version: 1.1.0
---

# PSM-Zulassungen: Pruefstand und Grenzen (04.11.2026)

Die native Liste verwendet ausschliesslich den lokalen PSM-Stamm des angemeldeten Mandanten. Artikelnummer, Name, Wirkstoff, Mitteltyp, BVL-Nummer und Ablaufdatum kommen unveraendert aus dem Stamm. Der nullable Aktivwert bleibt bei unbekanntem Wert leer. Ablauf bedeutet nicht Widerruf oder Sperre. Die Ablaufzahl vergleicht den Kalendertag in der Betriebszeitzone und umfasst alle Seiten der gefilterten Ergebnismenge.

Nutzerentscheidung 04.11.2026: „vorhandene zeilen sin nur testdaten. tabelle kann entfernt werden, wenn nicht mehr passend“. Das ersetzte Register wird nach Verbraucherpruefung auch mit Zeilen unter Tabellensperre ohne CASCADE entfernt. Weiter genutzte Tabellen sind nicht umfasst. Eine transaktionale Migrationspruefung mit belegter Tabelle und Rollback steht noch aus; Pruefungen mit gewachsener Datenbank sind nicht erfolgt.

Fuenf reine Vertragstests bestanden mit deaktiviertem Plugin-Autoload und Prozess-Exitcode 0. Auf dem gemeinsamen Pruefstand wurden nach Status- und Clientkontrolle zwei eigene PSM-Testmandanten, getrennte Leseergebnisse und Ablaufzaehlungen in einer anschliessend zurueckgerollten Transaktion geprueft. Ein Windows-pyreadline3-Destructorfehler trat nach Abschluss der reinen Tests auf. Offen sind die koordinierte transaktionale Migrationspruefung, Generatoren, Gates und visuelle Abnahme.
