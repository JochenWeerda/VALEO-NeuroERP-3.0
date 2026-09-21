---
title: Gemeinsame kompakte Buttons mit 44 px
type: reference
audience: [entwickler, agent, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-09-21
description: Nachweis und Grenzen der zentralen Touch-Mindestgroesse kleiner Buttons.
---

# Zentrale Button-Mindestgroesse

Die gemeinsame Variante `Button size="sm"` verwendet jetzt
`h-11 min-h-touch min-w-touch` statt `h-8`. Schrift und horizontale Abstaende
bleiben kompakt. Die bestehenden Touch-Tokens betragen 44 px. Auch ein
zusätzliches `h-6` unterschreitet die Mindesthoehe nicht. Dies gilt fuer
Builder und Custom-Seiten, sofern sie dieselbe Button-Komponente verwenden.
FSX-, Auftrag-, Rechnung- und KIM-Fachdateien wurden nicht veraendert.

## Verifikation

- Vitest: 13 Tests in vier Dateien bestanden: `button-touch`,
  `uix-runtime-restmasken`, `data-table`, `VirtualDataTable`.
- Neuer Regressionstest prueft Mindestklassen bei Legacy-Hoehen,
  Event-Ausloesung, Ref/Fokus, disabled und `asChild`-Links.
- Chromium gegen `localhost:3001`: echte Button-Komponente mit App-CSS
  in einem isolierten Testbereich gerendert. Sechs Varianten, jeweils mit
  und ohne `h-6`, bei 390, 1366, 1440 und 1920 px: **48/48 Messungen**
  mindestens 44 px hoch und breit. Kein Geschaeftsvorgang wurde ausgeloest.
- Lokale Rohmessungen: `artifacts/uix-sm-browser.json`.

## Grenzen und naechste Abnahme

Die Messung belegt die Komponente, keine vollstaendige Seitenabnahme.
Toolbars und feste Tabellenzeilen koennen durch die groesseren Ziele mehr
Platz brauchen; insbesondere FSX/KIM sind noch in ihren Fachablaeufen zu
pruefen. Explizite kleinere `min-height`-Overrides oder native Buttons
sind nicht automatisch abgesichert.

Die Kartenstapel existieren inzwischen im gemeinsamen Arbeitsbaum, liegen
aber im Slice HOME-UIX von Cursor; dieser Commit nimmt dessen Aenderungen
nicht mit. MCP-Write bleibt offen. Das gesamte UIX-Ziel ist nicht abgeschlossen.

Ruecknahme: ausschliesslich den zentralen Button-Slice revertieren, keine
fremden Masken- oder Kartenstapel-Aenderungen zuruecksetzen.
