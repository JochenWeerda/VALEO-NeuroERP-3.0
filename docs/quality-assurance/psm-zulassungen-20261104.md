---
title: PSM-Zulassungen - Pruefstand und Grenzen
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-11-04
version: 1.0.0
---

# PSM-Zulassungen: Pruefstand und Grenzen (04.11.2026)

Die native Liste verwendet ausschliesslich den lokalen PSM-Stamm des angemeldeten Mandanten. Artikelnummer, Name, Wirkstoff, Mitteltyp, BVL-Nummer und Ablaufdatum kommen unveraendert aus dem Stamm. Der nullable Aktivwert bleibt bei unbekanntem Wert leer. Ablauf bedeutet nicht Widerruf oder Sperre. Die Ablaufzahl vergleicht den Kalendertag in der Betriebszeitzone und umfasst alle Seiten der gefilterten Ergebnismenge.

Die entfernte Registertabelle darf ausschliesslich leer sein. Batch 9 behandelt historisch bekannte Seeds; die neue Migration entfernt selbst keine einzelnen Zeilen und bricht bei jedem Bestand ab. Pruefungen mit gewachsener Datenbank oder noch nicht abgesicherten Vorgaengermigrationen sind nicht erfolgt.

Fuenf reine Vertragstests bestanden mit deaktiviertem Plugin-Autoload und Prozess-Exitcode 0. Auf dem gemeinsamen Pruefstand wurden nach Status- und Clientkontrolle zwei eigene PSM-Testmandanten, getrennte Leseergebnisse und Ablaufzaehlungen in einer anschliessend zurueckgerollten Transaktion geprueft. Ein Windows-pyreadline3-Destructorfehler trat nach Abschluss der reinen Tests auf. Offen sind die koordinierte transaktionale Migrationspruefung, Generatoren, Gates und visuelle Abnahme.
