---
title: Frischen CI-Tabellenkatalog synchronisieren
type: qa
audience: [entwickler, qa]
owner: Codex
status: active
last_reviewed: 2026-10-16
version: 1.0.0
---

# Katalogdrift gegen frische Installation

Quality Gate 38797044667 hat den Katalog gegen die bereits migrierte Job-Datenbank geprueft und anschliessend ueber seinen bestehenden Fehlernachweisschritt das frische Katalogpaar erzeugt. Dieses vorhandene Artefakt wurde heruntergeladen und gegen den kanonischen HEAD verglichen. Keine lokale Datenbank wurde migriert, zurueckgesetzt oder kopiert.

Alle 680 bisherigen Tabellen behalten ihre vollstaendigen Spalten-, Schluessel- und Besitzdefinitionen. Hinzu kommt ausschliesslich domain_shared.screen_definition_history aus der bereits versionierten Migration studio_history_20261014 mit neun Spalten und Primaerschluessel id. Sieben additive Lineagezuordnungen stimmen mit den qualifizierten Tabellenreferenzen in den kanonischen Quelldateien ueberein: Portalzugang, Kontrollkorb, Ernteabrechnung und Prozesssimulation. Keine bestehende Verbraucherzuordnung entfaellt.

Die JSON-Datei entspricht bytegenau der Ausgabe des kanonischen Generators; Markdown entspricht dessen Ausgabe nach der bestehenden Datumsnormalisierung. Der korrigierte Katalog umfasst 681 Tabellen. Die physisch abweichenden fremden Arbeitskopien werden nicht ueberschrieben; geliefert wird ausschliesslich das gepruefte Katalogpaar im isolierten Index. Keine Gate-Ausnahme oder Schemaaenderung. Die abschliessende GitHub-Abnahme muss den Driftcheck erneut gegen ihre frische Job-Datenbank ausfuehren.
