---
title: Studio-Erntekette – reale Befunde
status: in arbeit
type: reference
owner: Codex
last_reviewed: 2026-10-14
---

# Reale Erntekette

Der vorhandene gemeinsame Prüfstand valeo_probe wurde mit eigenen synthetischen Daten in einer äußeren Transaktion verwendet. Keine neue Datenbank oder Container, kein Reset. Die abschließende getrennte Verbindung bestätigte, dass der eigene Mandant nicht persistiert wurde.

## Behobene Brüche

Teilpositionen tragen kein tenant_id. Die Partienzählung verwendet jetzt den mandantengefilterten Annahmekopf; beide Anlagewege verwenden gültige ORM-Felder. Annahmen mit erzeugter Gutschrift, bezahlt oder endgültig freigegeben dürfen weder direkt storniert noch erneut freigegeben werden. Der Stornotext verwendet das persistierte Feld remarks statt eines nicht vorhandenen notes-Felds.

Die bestehenden reinen Service-Unit-Tests initialisieren keine unbenötigte Kompatibilitäts-App. Ihre Attrappen haben einen explizit leeren Rechnungsverweis und prüfen das tatsächliche remarks-Feld. Fünf zusätzliche Fälle prüfen den verbindlichen Zustand und die mandantengefilterte Partienabfrage.

## Offene Pflichtinvariante

Die reale Versuchskette erreichte Annahme, Qualitätsberechnung, Gutschrift, Bestand, Journalbuchung und Gegenbuchung; Mandantentrennung, Rollenentscheidung, Korrekturverweigerung, Wiederholungsverweigerung und Rollback waren positiv. Vorsteuer scheitert: Der bestehende Self-Billing-Weg schreibt Vorsteuer im Haben und verschluckt Buchungsfehler. Kontierung und Steuerschlüssel müssen kanonisch geklärt und integriert werden; kein erfolgreicher Simulations-/Veröffentlichungsnachweis.

## Abnahmegrenze

23 gezielte Backendfälle und neun Studio-Frontendfälle bestanden. Elf Lesebindungen und sechs kanonische POST-Eingabeschemas wurden gegen eine HEAD-basierte OpenAPI-Projektion abgeglichen. Historie/POSTs sind noch nicht der abgeschlossene Gesamtslice; Browserabnahme, vollständige Kanalparität, revisionsgebundene Simulation und Veröffentlichungssperre bleiben offen. STUDIO-CLOSURE-20261014 bleibt in Arbeit.

## Fortsetzung

Die Vorsteuerinvariante ist durch SELF-BILLING-ATOMIC-20261014 behoben. Das echte grain.v1-Profil besteht jetzt alle zwölf Prüfungen mit vollständigem Rollback. Die zentrale Studio-Freigabeanbindung befindet sich weiter in der Abnahme; siehe self-billing-atomic-20261014.md.
