---
title: CRM Aktivitaeten: mandantengebundener Listenproxy
type: reference
audience: [entwickler, qa, agent]
owner: Codex
status: aktiv
last_reviewed: 2026-10-29
version: 1.0.0
description: Gezielter Vertragsnachweis im akzeptierten Integrationsstand.
---

# CRM Activity Proxy: mandantengebundene Liste (2026-10-29)

## Aenderung

`GET /api/v1/crm/activities/` uebergibt den aus dem verifizierten Request-Kontext stammenden Mandanten als Pflichtparameter an crm-core. crm-core filtert den Mandanten in seiner Abfrage vor `COUNT`, `OFFSET` und `LIMIT`. Der Client deckelt die Downstream-Grenze auf 200; der Proxy akzeptiert ebenfalls hoechstens 200 und meldet die tatsaechliche Seitengroesse.

Ein Downstream-Fehler ergibt eine generische `503`-Antwort ohne Fehlertext. Fremde Mandantenzeilen in einer Downstream-Antwort ergeben `502`; der Proxy gibt weder eine Teilantwort noch einen aus gefilterten Zeilen verfälschten Gesamtwert zurueck.

## Abnahme

- Unit-Test mit `httpx.MockTransport` und asynchronem Fake-Service belegt `tenant_id` zusammen mit `skip` und gekapptem `limit` in derselben crm-core-Anfrage.
- Endpoint-Vertrag prueft die Weitergabe des verifizierten Mandanten, korrekten Core-Gesamtwert, fail-closed `502` bei einer fremden Zeile sowie generische `503` ohne Downstream-Payload.
- Die fehlende Mandantenkennung wird vom Core-Client vor einer Anfrage abgewiesen.
- Keine Datenbank, kein Container, kein App-Startup und keine Service-Schreibwege verwendet.

## Grenzen

Die Aktivitaets-Detailwege und die getrennte lokale CRM-Tabelle sind nicht Bestandteil dieser Aenderung. `search` und `offset` bleiben wie zuvor unbeachtet; die CRM-Service-Oberflaeche sendet diese Parameter, aber deren Abbildung ist ein eigener API/UI-Vertrag.

Nachweis: alle fuenf gezielten Tests bestanden. Die HTTP-Vertraege wurden mit echter FastAPI-Routenvalidierung und synthetischen Abhaengigkeiten geprueft; kein externer CRM-Dienst aufgerufen.
