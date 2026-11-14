---
title: Studio-Teststrategie — Klassen, Varianten und Bedienwege
type: explanation
audience: [entwickler, agent, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-11-13
version: 1.0.0
description: Fachliche Tests der Studio-Runtime statt Bindung an abgeloeste Einzelmasken.
---

# Tests fuer Studio-Masken und ihre Varianten

Die fachliche Erwartung ist der Pruefstein. Ein Test auf einen entfernten React-Hook,
einen bestimmten Dateinamen oder alten JSX-Text ist nach einer Migration zu ersetzen.
Eine weiterhin gueltige Mengen-, Buchungs-, Rechte- oder Freigaberegel bleibt bestehen.
Ein fehlendes Verhalten ist erst nach fachlicher Entscheidung entfallen; ein neuer
Katalogeintrag oder ein gruener Renderer-Test ersetzt diese Entscheidung nicht.

## Gemeinsamer Kern und gezielte Varianten

| Ebene | Was auszufuehren ist | Was der Nachweis nicht ersetzt |
|---|---|---|
| Maskenklasse | Echte ScreenDefinition durch Compiler, Runtime und Renderer; Eingaben, Validierung, Tabellen, Dialoge, Fehler- und Leerzustand, Theme/Lesbarkeit | Fachregeln des jeweiligen Commands |
| Versionierte Variante | Konkrete Feld-/Aktionsabweichungen, exakte Basis-/Variantenbindung, unveraenderte Historie und Cachewechsel | Vollstaendige Prozessabnahme allein durch Hashvergleich |
| Fach-Command | Pflichtfelder, Mengen/Geld/Steuer, Zustaende, Freigabebindung, erwartete Version, Wiederholung, Rollback, Audit und Outbox | Freigabe allein durch sichtbaren Button |
| Bedienweg | Gleicher Command und Eingabeumschlag aus Mensch/HTTP, MCP und CLI; Erfolg und fachliche Ablehnungen transportieren | Identische Oberflaeche fuer alle Kanaele |
| Sicherheit/Autonomie | Token-Mandant, Rolle, Datensatz, freigegebene Capability, Delegation, Qualitaet, Risiko und unabhaengige Freigabe | Rechtegewinn durch Lernerfolg oder Tool-Sichtbarkeit |

Gemeinsame Mechanik wird an der Klasse geprueft, nicht fuer jede Variante erneut
abgeschrieben. Jede Variante benoetigt dennoch ihre spezifischen Fachfaelle und
eine korrekte Bindung an die gepruefte Fassung. Identische Eingaben und Rechte
muessen ueber alle Kanaele dieselbe zulaessige Wirkung und Ablehnung erzielen.
Eine bewusst menschliche Freigabe bleibt menschlich; CLI/MCP koennen ihren
Vorschlag vorbereiten, duerfen die Freigabegrenze jedoch nicht umgehen.

Die bestehenden Nachweise `test_mask_family_versions.py`,
`render-plan/document-variant-version.test.tsx` und
`test_studio_entity_channels.py` sichern unterschiedliche Teile dieses Vertrags.
Die SQL-Kanaltests sind keine datenbankfreien Unit-Tests. Die neuen
`test_studio_channel_outcomes.py` pruefen ergaenzend nur die Adapter gegen einen
kontrollierten HTTP-Zielweg. Sie ersetzen weder Browserbedienung, Tokenpruefung
noch die Fachregel am Ziel. `test_agent_autonomie_unit.py` prueft die echte
Entscheidungslogik mit gespeicherten Fakten am simulierten Datenbankrand;
`test_agent_autonomie.py` bleibt fuer die PostgreSQL-Wirkung erforderlich.

## Alte Tests ersetzen

1. Die bisherige fachliche Erwartung festhalten und ihren aktuellen Command,
   ihre Maskenklasse sowie die konkrete Variante bestimmen.
2. Vorhandene Klassen-/Commandtests wiederverwenden. Fehlende Erwartungen am
   echten Laufzeitweg ergaenzen, mit Mocks nur an externen Grenzen.
3. Negativfaelle pruefen: fehlende Rechte, fremder Mandant, veraltete Fassung,
   ungueltige Eingabe, fehlende oder unpassende Freigabe und Wiederholung.
4. Erst nach gruenem Ersatz den alten Test und dessen erwarteten Fehlschlag
   entfernen. Die Runtime46-Ratsche im selben Commit senken. Verbleibende
   Funktionsluecken mit Namen dokumentieren; kein pauschales Skippen.

Inventur am 13.11.2026 vor dieser Runde: **184 erwartete Fehlschlaege in 49
Frontend-Testdateien**, dazu neun gesonderte Smoke-Ausnahmen laut bestehender
Ratsche. Das sind Entwicklungsaltlasten, keine Abnahmebelege. Der erste
abgegrenzte Ersatz betrifft die drei alten Tests der Waagenliste: ersetzt durch
fuenf Verhaltenstests. Im Nachlauf vom 14.11. sank die Restliste durch
Klassen-, Workflow-, Bestellvorschlag-, Betriebslisten- und Sortentests auf
**131 in 38 Dateien**, Smoke-Ausnahmen
unveraendert. Das Ergebnis
und Grenzen stehen in [Waagenlisten-QA](studio-test-waage-20261113.md).
Die verbleibenden Gruppen werden nach fachlicher Wirkung abgebaut: Finanz- und
Bestandsaktionen, Belegketten, Annahme/Waage, danach Listen und Navigation.

## Effiziente Ausfuehrung und Freigabe

Bei einem Variantenpatch laufen betroffene Varianten, ihre gemeinsamen Klassen
und Command-Negativfaelle. Aenderungen am Compiler, Renderer, Identitaets- oder
Freigabekern erfordern die betreffenden klassen- und kanaluebergreifenden Suiten.
Das ist eine Auswahl nach Abhaengigkeit und Risiko, keine Freistellung alten
Codes. Vor Integration sind die verpflichtenden CI-Gates weiterhin erforderlich.

Nur die bereits vorhandene `valeo_probe`/`TEST_DATABASE_URL` verwenden;
Status/Nutzung vorher kontrollieren und eigene Transaktionen zurueckrollen.
Keine neuen Datenbanken oder Container pro Test und keine SQLite-Ersatzabnahme.
Coverage dient zur Suche nach ungeprueftem Verhalten. Schwellen, New-Code-Periode
oder Quellausschluesse werden nicht zum Entfernen roter Tests angepasst.

Der Liefernachweis benennt Commit, Testumfang, Ergebnis und simulierte Grenzen.
Ein gezielter gruener Lauf ist kein Vollsuite-, Browser- oder Sonar-Gesamtnachweis.
Freigabe und Ausfuehrungsrechte stammen weiterhin aus den bestehenden
Bereichsrollen, MCP-WRITE-001 bis 015 und ADR-086.
