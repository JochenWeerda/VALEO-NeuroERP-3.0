---
title: Einheitlicher JSON-Objektvertrag fuer KI-Antworten
type: reference
audience: [entwickler, qa, agent]
owner: Codex
status: aktiv
last_reviewed: 2026-10-11
description: Vier duplizierte Antwortparser ersetzen und widerspruechliche KI-Ergebnisse sicher zur Fachlogik zurueckfuehren.
---

# KI-JSON-Objektvertrag

## Befund und Umsetzung

WhatsApp-Bestellextraktion, Kaeuferklassifikation sowie die beiden CRM-KIM-Wege
Kundendossier/E-Mail-Entwurf entfernten JSON-Fences mit vier gleichen Regex-
Ausdruecken. Diese vier Stellen tragen Sonar S5850. Die Gegenprobe fand ausserdem
echte Vertragsfehler: WhatsApp meldete Listen, null oder Zahlen als erfolgreiche
Bestellextraktion; nichtfinite Zahlen konnten eine scheinbar erfolgreiche
KI-Antwort erzeugen; Grossbuchstaben im JSON-Fence verursachten unnoetige
Fallbacks. Kaeuferklassifikation loggte private Werte aus Konvertierungsfehlern.

Alle vier Wege nutzen nun parse_json_object im bestehenden LLM-Gateway:

- Reines JSON oder ein vollstaendiger JSON-Codeblock (json/JSON oder ohne Label).
  Leerzeichen am Fence erlaubt; Text innerhalb des JSON bleibt erhalten.
- Wurzel muss ein Objekt sein; keine Liste, Zeichenkette, Zahl, Boolean oder null.
- Nichtfinite Zahlen einschliesslich Exponentenueberlauf werden abgewiesen,
  auch in verschachtelten Strukturen. Doppelte Objektschluessel werden nicht
  still ueberschrieben, sondern als widerspruechliche Antwort abgewiesen.
- Defekte/anders deklarierte Fences und ungueltiges JSON werden nicht aus
  Begleittext erraten. Vorhandene Fachfallbacks bleiben erhalten.
- Parsingwarnungen der WhatsApp- und Klassifikationswege enthalten feste Texte
  statt privater Antwort-/Konvertierungswerte.

Keine neue Serviceinstanz, Provideranfrage, Abhaengigkeit, Route oder
Antwortschema. Anbieterwahl, Mandant, Tokenlimit, Fachklassifikation und
Heuristik bleiben bestehende Vertraege. Vier Regex-Parser entfallen.

## Abnahme

Vor Reparatur waren elf von 14 Verbraucher-Gegenproben rot; drei bestehende
Rückfallpfade bestanden. Daneben definierten 20 neue Parservertraege die noch
fehlende gemeinsame Schnittstelle; deren Fehlschlag ist kein zusaetzlicher
Produktionsfehler. Die finalen Tests erweitern die Randfaelle um erlaubte
Fence-Leerzeichen und verschachteltes NaN.

Final 51 Tests bestanden in 2,53 Sekunden: 36 neue Parser-/Verbrauchervertraege,
neun bestehende Gateway- und sechs bestehende CRM-KIM-Vertraege. Echte Verbraucher
laufen; nur Providerantworten und DB-Leser werden an ihren Grenzen ersetzt.
SQLAlchemy-Verbindungen und HTTP-Provideranfragen sind explizit verboten.
Keine Datenbank, Migration, Dockerinstanz oder externe Nachricht erzeugt.

Grundlage: [Python JSON-Decoder](https://docs.python.org/3.11/library/json.html)
(parse_float, parse_constant und object_pairs_hook).

## WhatsApp-Transportentscheidung

User-Vorgabe vom 2026-10-11: WhatsApp laeuft als WhatsApp Web im Browser und
wird ueber Computer Use bedient. Dies ist der vorgesehene Integrationsweg.
Die Bestellextraktion verarbeitet den eingelesenen Nachrichtentext unabhaengig
vom Transport. Diese Parsingkorrektur stellt noch keine Browseranbindung her.
Bestehende Webhook-/Cloud-API-Wege muessen mit dieser Vorgabe abgeglichen werden;
Browserkonto und Mandant muessen eindeutig zusammengehoeren. Ein Versand darf
erst nach einer konkreten Versandautorisierung ausgefuehrt werden.

## Verbleibende Grenzen

Der gemeinsame Vertrag prueft JSON-Struktur und Zahlenintegritaet. Vollstaendige
fachliche Feldschemas der vier Ergebnisse sind damit nicht vereinheitlicht;
deren bestehende Validierung/Fallbacks bleiben bestehen. WhatsApp nutzt weiterhin
die bestehende Herkunftsbezeichnung claude; eine providerneutrale Kennzeichnung
braucht einen abgestimmten Verbraucher-Nachzug. Andere Gateway-Logs sind nicht
Teil dieser begrenzten Parsingkorrektur.

Weitere Sonar-Befunde, Abdeckung, Duplikate und Security-Hotspot-Bewertungen
bleiben offen. Die vier Scannerbefunde gelten erst nach Rescan als extern
bestaetigt geschlossen; keine Regel-/Schwellen-/Baseline-Ausnahme eingefuehrt.
