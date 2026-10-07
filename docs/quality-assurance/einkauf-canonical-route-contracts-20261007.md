---
title: Kanonische Einkaufsrouten und veroeffentlichte Vertraege
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: lokal_geprueft
last_reviewed: 2026-10-07
---

# Laufzeit und OpenAPI verwenden dieselben Einkaufsvertraege

Acht spaeter registrierte Lieferanten-/Bestell-GET-/POST-/PUT-Handler in
`app/einkauf/router.py` waren zur Laufzeit durch die vorher montierten
`einkauf_bestellvorschlag`-Handler verdeckt. FastAPI veroeffentlichte trotzdem
die alten Integer-IDs, Rohantworten und Create-DTOs im OpenAPI-Vertrag.
Die unerreichbaren acht Handler und zwei ausschliesslich dort verwendeten
Whitelists sind entfernt. Der fuehrende ProcurementService und dessen
Endpoint-Modul wurden nicht geaendert; laufender fremder Fachbesitz bleibt erhalten.

## Abnahme

- 89 Tests bestanden (53,60 s): kanonische Montagen, sechs echte
  Mandanten-/ORM-Schreibvertraege, ProcurementService, Bestellmasken,
  bestehende Einkaufs-API, gemeinsame Probe-Integration, OCR und Anfragen.
- Ein bestehender unisolierter Bestell-Detailtest uebersprang wegen leerer
  Default-Mandantenliste. Er ist kein bestandener Detailnachweis; die separate
  Probe-Suite verwendet eigene Bestelldatensaetze und prueft Liste, Detail,
  Storno und fremde Mandanten.
- Acht Montagevertraege beweisen je genau einen Handler, unveraenderte
  Antwortmodelle, Status und Dependencies sowie identische publizierte Operation.
  Zwei weitere Vertraege sichern die einzigartigen DELETE-Pfade gegen Verlust.
- Alle 3974 Pfad-/Methodenvertraege und 3101 OpenAPI-Pfade erhalten;
  genau vier Einkaufs-Pfade korrigiert, Doppelgruppen 41 auf 33 reduziert.
  Zweiter Generatorlauf deterministisch identisch.
- Drei Code-Inventare, vollstaendiger Architekturindex (935 Routen) und fuenf
  Handbuchartefakte lesend aktuell; keine unnoetige Neuerzeugung.
  Godfile-Gate exakt 15, Logistik 1031, keine Baseline-Erhoehung.
- Gemeinsamer `valeo_probe` vor Integration lesend bestaetigt auf
  `mandant_finanz_crm_20261007`. Keine neue DB/Container, kein Reset/Migration.
  Erster sandboxbegrenzter Lauf beendet; erfolgreicher Lauf mit Zugriff
  ausschliesslich auf den bereits vorhandenen Pruefstand.

## Verbleibende Grenzen und Handshake

Die zwei einzigartigen Lieferanten-/Bestell-DELETE-Handler schreiben noch in
historische Tabellen mit Integer-IDs. Sie wurden nicht blind geloescht; ihre
Ausrichtung auf den kanonischen Speicher bleibt eigener Reparaturumfang.
33 weitere doppelte API-Registrierungen, der noch unechte Bestellimport und
die sonstigen dokumentierten fachlichen Luecken sind weiterhin offen.

GitHub auf `b2a63f451`: PostgreSQL, E2E, Erntepeak, Docs/OpenAPI und
Frontend lint/typecheck/build/WCAG gruen. Quality hat konkrete Restfehler:
Business-Time-Inventur und physischer Tabellenkatalog; Node-Audit weiterhin
zwei ungepatchte High-Befunde. Tabellenkatalog-Generator/Test/Workflow sind
fremde WIP. Diese Abnahme ersetzt keinen gruenen Gesamtpipeline-Nachweis.
