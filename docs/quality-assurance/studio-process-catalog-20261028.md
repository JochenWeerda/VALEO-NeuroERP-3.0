---
title: Studio Prozesskatalog – funktionale Migration
type: reference
audience: [entwickler, qa, agent]
owner: Codex
status: aktiv
last_reviewed: 2026-10-28
version: 1.0.0
description: Funktionale Katalogmigration mit typisiertem Vertrag, Sprachcache und visueller Komponentenabnahme.
---

# Funktionale Katalogmigration

workflow/flow-spine-studio nutzt ausschliesslich UniversalNativeCockpitPage mit
registriertem flowSpineCatalog-Vertrag. Compiler und Servervalidierung erlauben
nur den registrierten Cockpitmodus und zwei boolesche Konfigurationen. Keine
beliebigen Endpoints, keine Dead-Letter-Tabelle, kein Export-Platzhalter und kein
Wrapper der ehemaligen Seite. Die Runtime nutzt den vorhandenen Katalog-Client;
der Renderer zeigt dynamisch Kennung, Titel, Zusammenfassung, Domaene und Ziele.
Die Backend-Rollen-/Mandantenentscheidung bleibt unveraendert.

Erhalten: Laden, Fehler mit Retry, leere Daten, Anzahl, lokale Prozessnavigation,
Sprachwahl und gestaffeltes Vorladen. Neue Buttons sind per Tastatur erreichbar,
verwenden Theme-Tokens und sperren unzulaessige Ziel-URLs. Antworten mit fehlenden
Textfeldern, doppelten Kennungen oder mehr als 500 Eintraegen werden abgewiesen.

Der Nachlauf fand einen Cachefehler: Verzoegerte Warmup-Anfragen konnten nach einem
Sprachwechsel andere Inhalte als ihren Cache-Schluessel laden. Die beim Planen
gewaehlte Sprache wird jetzt auch fuer die HTTP-Anfrage benutzt. Ausstehende Timer
werden beim Verlassen/Sprachwechsel entfernt; bereits gestartete Reads werden
nicht als Geschaeftsaenderung ausgefuehrt. Normale Reads behalten ihre Rechte.

## Nachweise

29 Frontendfaelle in sechs Dateien und 34 Backendfaelle bestehen; darunter echte
Compiler-/Runtime-/Renderer-Tests, Sprachwechsel, Navigation, Fehler/Retry,
Leerzustand, unzulaessige Ziele, Metadaten-/Cachevalidierung und Warmup-Abbruch.
Die bestehende Reklamationsliste und Prozessaktions-Fehlergrenze bleiben gruen.
Vollstaendige Typpruefung und Produktionsbuild bestehen; Chunk-Warnungen wurden
nicht durch hoehere Grenzwerte unterdrueckt. Keine Datenbank/Container erzeugt,
keine Buchung, Migration oder persoenliche Kennung benutzt.

Sechs reale Browseransichten mit explizit synthetischem Transport: 1366x768,
1440x900,1920x1080 jeweils Hell/Dunkel. Keine horizontale Ueberbreite und keine
axe-WCAG2A/AA-Verletzung; heller und dunkler Zustand gesichtet. Tab erreicht den
ersten Prozess. Dies ist eine Komponentenabnahme und keine angemeldete E2E- oder
vollstaendige Mandanten-/Rollenabnahme. Screenshots und maschinenlesbare Ergebnisse:
[screenshots/studio-catalog-20261028/results.json](screenshots/studio-catalog-20261028/results.json).

## Umfang

Gate E ist jetzt802/853, also51 offen. Der Katalog schliesst genau einen der
urspruenglichen52 Punkte. Die neun instanzgebundenen Prozessraeume bleiben eigene
funktionale Migrationen. C852/853 (Portalzertifikat) und fuenf strukturell bereite
Draft-Projektionen bleiben unveraendert. Die urspruengliche52er-Liste ist im
[Arbeitsinventar](studio-runtime52-inventory-20261028.md) dokumentiert.
