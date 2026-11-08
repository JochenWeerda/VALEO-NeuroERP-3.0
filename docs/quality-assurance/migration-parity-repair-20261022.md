---
title: Reparatur der Maskenmigrationsregressionen 2026-10-22
type: reference
owner: Codex
status: teilweise abgeschlossen
last_reviewed: 2026-10-22
---

# Reparatur der Maskenmigrationsregressionen

Der lokale Batch `deeb707b4` hat neben neuen Parent-Buildern bereits gepruefte Sicherheits-, API- und Bedienvertraege zurueckgenommen. Der vorherige Remote-Stand `8086c464f` ist die Vergleichsbasis; fuer bestehende Backend-Dateien ist der direkte Batch-Vorgaenger massgeblich. Neue Builder und Layoutmodule bleiben erhalten. Fremde ungespeicherte Arbeitskopien und der aktive Adaptive-Workspace-Claim werden nicht ueberschrieben.

## Reparaturumfang

- 337 bestehende API-Dateien und 12 Core-Vertraege wieder auf den Stand vor dem fehlerhaften Batch bringen: Rollenpruefung, Token-Urheber, AP-Freigabe, Masken-Lesevertrag und Simulation.
- 13 zentrale Render-/Runtime-Vertraege bewahren: strukturierte Belegpositionen, Validierung, erwartete Version, mandantengebundene Cachekeys, Paging und Storno-Folgedialog.
- 24 nachweislich bestehende native Fachaktions- und Anlagevertraege wieder an die neuen Parent-Shells anbinden. Explizite Domain-Builder haben Vorrang vor generischen Familien-Platzhaltern. Rechte werden aus bestehenden Backend-Rollen projiziert.
- DATEV-Auswahl und CSV-Download ueber den tatsaechlichen lesenden Export-Endpunkt wiederherstellen; der Server bestimmt Inhalt und Dateiname. Dieselben drei deklarierten Lesedatenquellen sind ueber den gemeinsamen MCP-/CLI-Maskenleseweg adressierbar. Keine Buchungswirkung, keine behauptete EXTF-Zertifizierung.
- Falsche relative Imports, verlorene Chart-/Dialog-Props, Detail-ID und Lazy-Loader-Props reparieren.
- Durch reale fehlgeschlagene Bedienvertraege belegte Seiteneinstiege gezielt wieder funktionsfaehig machen. Die gemeinsame Belegkontrolle nutzt wieder Domain-Commands mit Auditbegruendung und Idempotenz statt direkter Statusmutation. Neue generische Builder bleiben verfuegbar, gelten bis Funktionsparitaet aber nicht als abgenommener Ersatz.

## Wahrheitsgemaesse Nachweise

Lazy-Legacy-Wrapper, Imports, Kommentare und `aria-hidden`/`sr-only`-Runtime-Huellen zaehlen nicht als sichtbare native Masken. Ein Katalogeintrag braucht einen passenden aktuellen Definitionshash. Strukturelle Bereitschaft ist keine Live-Freigabe. Ein fehlendes OpenAPI-Dokument oder ein nur aehnlicher Pfad ist kein gueltiger Endpunktnachweis. Der Kataloggenerator entfernt keine fremde Sperre und zerstoert bei fehlgeschlagenem atomaren Austausch keine bestehende Datei.

Die frueheren Aussagen „941/941 migriert“ und „alle release-ready“ sind damit nicht belastbar und werden durch die neu erzeugten Inventare ersetzt. Funktional benoetigte bestehende Masken werden erst nach echter Paritaet abgeloest. Keine Tests werden entfernt oder Gates abgeschwaecht, um einen Abschluss vorzutäuschen.

## Pruefung

- 54 gezielte UI-Testdateien: **196/196 bestanden**, einschliesslich Export, fachlicher Ablehnungen, Doppelaufrufschutz und bestehender Arbeitsablaeufe.
- Erneuter Backend-Vertragslauf: **195/195 bestanden**; vollstaendige Frontend-Typpruefung ohne Fehler bestanden. Vollstaendiger Vite-Produktionsbuild bestanden (4498 Module; bestehende Chunkgroessenwarnung bleibt).
- Abschliessender echter SQL-Lauf auf stabilen Quellen: **76/76 bestanden**, einschliesslich AP-Sicherheit/Nebenlaeufigkeit, Spuelchargen-Umlagerung und unabhaengiger Studio-Freigabe. Der zuvor ausgeloeste Quellstand-Neustartschutz wurde nicht umgangen.
- Rollenratsche zuletzt null ungeschuetzte Schreibwege, Godfile-Ratsche unveraendert bestanden. Business-Time-Baseline nur von194 auf193 abgesenkt.

## Offene Grenzen und Handshake

Kein Gesamtabnahmesiegel fuer alle Masken, keine Browser-/Bildabnahme dieser Reparatur und kein vorweggenommener gruener GitHub-Nachlauf. Der diagnostische Volltest enthaelt zudem alte Quelltext-/Layout-Assertions und drei Start-Dashboard-Befunde im aktiven Adaptive-Workspace-Claim. Diese werden nicht geloescht oder durch Ueberschreiben fremder Arbeit kaschiert. Inventar, fehlende echte API-Vertraege und vollstaendige native Fachparitaet bleiben explizite Folgearbeit.

Es werden ausschliesslich die vorhandene `valeo_probe` und eigene Testdatensaetze verwendet, keine neue Datenbank, kein Container, kein Reset. Zugangsdaten und persoenliche Identitaeten sind kein Bestandteil dieser Lieferung.

Aktuelles strenges Routeninventar: 941 Routen, davon833 mit Runtime-Pfad,50 Legacy-Wrapper,53 handgebaut,1 altes Maskenmuster und4 technische Seiten. Runtime-Pfad allein ist kein Fachparitaets-/Browserbeleg. Statische Gates: 20 Definitionen ohne bestaetigten API-Vertrag,52 ohne aktuellen Runtime-Evidenznachweis; diese Luecken werden nicht als fertig freigegeben.

Die zusaetzliche Typpruefung der zusammengefuehrten fremden Arbeitskopie ist wegen fuenf noch offenen Workspace-/Routen-Testbefunden nicht gruen. Sie ist nicht mit der erfolgreichen Typpruefung des Reparaturcommits gleichzusetzen. Einzelheiten im Handshake docs/agent-ops/handshakes/migration-parity-repair-20261022.md.
