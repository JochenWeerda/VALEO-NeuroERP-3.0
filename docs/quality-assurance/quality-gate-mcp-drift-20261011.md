---
title: Quality Gate MCP-Referenzdrift 2026-10-11
type: reference
audience: [entwickler, qa, agent]
owner: Codex
status: aktiv
last_reviewed: 2026-10-11
description: Ursache und Regressionsschutz fuer den veralteten MCP-Referenzstand im Quality Gate.
---

# Quality Gate MCP-Referenzdrift

## Ursache

Der [Quality Gate 38121252132](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/runs/38121252132)
auf `4337dd684` brach im Doc-Generator-Meta-Check ab. Die Registry enthielt
56 MCP-Tools, die generierte Referenz noch 51. Die fuenf bereits gelieferten
Fuhrpark-Commands fehlten in der Referenz. Nachfolgende Backend-Schritte
wurden dadurch nicht ausgefuehrt.

## Korrektur und dauerhafter Schutz

Die Referenz wird aus der committed Registry regeneriert. Der Generator
unterstuetzt jetzt `--check --staged`: Registry und Referenz werden aus dem
Git-Index gelesen. Nicht gestagte Arbeitsbaum-Aenderungen koennen weder
veraltete Commit-Inhalte verdecken noch einen konsistenten Commit blockieren.
Der Modus schreibt weder Arbeitsbaum noch Index und erlaubt keine Generierung.

`scripts/run-staged-checks.cjs` fuehrt diesen Vertrag bei Aenderungen an der
Registry, dem Generator oder der Referenz aus. Der bestehende verpflichtende
GitHub-Meta-Check bleibt erhalten; keine Schwelle, Baseline oder Pruefung
wurde abgesenkt oder deaktiviert.

## Abnahme

Sieben fokussierte Regressionstests bestanden: konsistenter Index,
veraltete Referenz trotz korrigiertem Arbeitsbaum, fremdes ungestagtes WIP,
fehlende gestagte Referenz, unveraenderter Index/Arbeitsbaum,
abgewiesener Schreibmodus und Anbindung im Commit-Hook.

Die Generatorfolge wird am isolierten committed Lieferstand mit der Korrektur
geprueft. GitHub-Folgeabnahme und eventuell zuvor verdeckte Gate-Befunde
werden im zugehoerigen Workboard-Claim weiterverfolgt. Kein aktueller
projektweiter gruener Gesamtlauf wird vor dessen Abschluss behauptet.

Keine Datenbank, kein Container, keine Migration und kein Reset fuer diese
Pruefungen; fremdes laufendes WIP bleibt erhalten.

## Generatorfolge und nachfolgender Katalogdrift

Alle 13 Befehle der Doc-Generator-Metafolge bestanden lokal am isolierten
committed Lieferstand mit der Korrektur. GitHub 38122841810 bestaetigt diesen
Schritt ebenfalls. Danach reproduziert die physische Katalogpruefung einen
weiteren Drift; der vorhandene Job exportiert seine echte frische Schema-Ernte.

Diese Ernte enthaelt weiterhin 670 Tabellen. Genau vier Fuhrpark-Tabellen
erhalten die bereits migrierte tenant_id-Spalte (NOT NULL, character varying).
Sieben weitere Eintraege korrigieren ausschliesslich Code-Verbraucherzuordnungen
nach den bereits gelieferten Command-Auslagerungen. Keine Tabelle hinzugefuegt
oder entfernt; Primaer-/Fremdschluessel unveraendert. Alle Verbraucher und
Screen-Quellen stimmen mit dem committed Quellcode ueberein; keine fehlende
Lineage. JSON und Markdown stimmen mit dem kanonischen Generator ueberein.

Die beiden fremden lokalen Katalogfassungen bleiben byteweise erhalten.
Nur der isolierte Lieferindex erhaelt die aus dem CI-Job geprueften Artefakte.
Keine lokale DB/Migration/Ruecksetzung und kein neuer Container. Nachabnahme
des Gesamtlaufs bleibt bis zum folgenden GitHub-Lauf offen.
