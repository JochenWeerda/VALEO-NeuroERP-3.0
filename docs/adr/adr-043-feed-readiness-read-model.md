---
title: ADR-043 Futter-Readiness als domänenübergreifendes Read-Model
type: adr
audience: [architektur, fachlich, entwickler, qa]
owner: domain/agrar
status: accepted
last_reviewed: 2026-07-14
version: 1.0.0
---

# ADR-043 Futter-Readiness als domänenübergreifendes Read-Model

## Status

Accepted, 2026-07-14.

## Kontext

Der Solver optimierte Nährwerte und Kosten, ohne den berechneten Einsatz
verbindlich gegen verfügbaren Bestand, aktuelle Grundfutteranalysen und gültige
Lieferantenpreise zu prüfen. Die Quelldaten existieren bereits in Stamm,
Inventory, Labor und Einkauf und dürfen nicht in einer zweiten Bestandsführung
dupliziert werden.

## Entscheidung

Ein tenantgebundenes Read-Model verknüpft die Komponenten einer Rationsversion
zur Laufzeit mit den bestehenden Quellen. Es berechnet deterministisch Reichweite,
Analysealter/-wechsel und Preisgültigkeit und liefert je Komponente maschinenlesbare
Codes, Schweregrad und verständlichen Handlungsbedarf.

Der Solver speichert das Readiness-Ergebnis im unveränderlichen Entwurfssnapshot.
Blockierende Befunde verhindern Freigabe und Aktivierung. Eine fachlich begründete
Ausnahme ist nur explizit als `OVERRIDE:` möglich und wird im Lifecycle-Audit
erhalten. Fehlende externe Zuordnungen werden als Warnung sichtbar, nicht still
als Nullbestand interpretiert.

Die native ScreenDefinition `agrar/feed-readiness` zeigt den aktuellen Zustand
aktiver Rationen. Stammdatenkorrekturen erfolgen weiterhin in den zuständigen
Bestands-, Analyse- und Preisoberflächen.

## Konsequenzen

- Keine Schattenbestände und keine kopierten Labor- oder Einkaufspreise.
- Freigaben bleiben auch bei Datenlücken bewusst entscheidbar und auditierbar.
- Neue Connectoren können über stabile Material-IDs in dasselbe Read-Model münden.
- Historische Entwürfe behalten den damaligen Befund; die aktuelle Prüfung kann
  davon abweichende Analysen und Preise erklären.

