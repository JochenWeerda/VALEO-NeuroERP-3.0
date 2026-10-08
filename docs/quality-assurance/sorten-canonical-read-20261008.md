---
title: Sortenregister am kanonischen Agrar-Vertrag
type: qa
audience: [entwickler, qa, agent]
owner: Codex-01a0f3fc
status: active
last_reviewed: 2026-10-08
version: 1.0.0
---

# Sortenregister am kanonischen Agrar-Vertrag

## Ursache und Umsetzung

GitHub-Smoke37739698920 auf b47cd87be: Agrar14 bestanden, ein Fehler im
Sortenregister. Alle drei Traces zeigen404 auf dem nicht vorhandenen
`/api/v1/agrar/saatgut/sortenregister`. Kanonisch ist bereits
`/api/v1/agrar/varieties/` gegen `domain_shared.agrar_sorten`.
Security Scan37739699012 und grosser CI-Lauf37739698939 sind gruen.

Der Hook liest den bestehenden Vertrag mit `aktiv=false` fuer alle
Aktivzustaende. Der zentrale AgrarVariety-Typ entspricht VarietyOut;
der Auswahldialog referenziert dessen Felder als Pick. Register und CSV
verwenden Kulturcode, Zuechter, Zulassungsjahr, Qualitaetsgruppe und Aktivstatus.
Nullable Daten bleiben nullable; keine erfundenen Eigenschaften oder
Zulassungsdaten. Inaktiv bedeutet nicht auslaufende Zulassung.

Die Saatgutbestellung verwendet crop_type. Eine reine Beschriftung fuer die
fuenf Backend-Katalogcodes erhaelt die deutschen Auswahlwerte; unbekannte
Codes bleiben erhalten. Handelsbestaende/-preise und die historischen
Standard-Fallbacks des Ernte-Auswahldialogs bleiben getrennte offene Altlasten.
Kein neuer API-Endpunkt, DB-Typ, Renderer oder Seitenlayout; fremde UI-Hunks
bleiben erhalten. Lieferung nur eigener Hunks auf committed-source.

## Abnahme und Betrieb

- Vier React-Query-Vertraege: nullable/inaktive Daten, echte Leerliste,
  sichtbarer Fehler und Kultur-Auswahlbeschriftung.
- Zwei Chromium-Faelle: Datendarstellung/Filter und retrybarer API-Fehler.
  Ein kalter erster Fixture-Start brach vor dem Test nach30s ab; gezielte
  Wiederholung des Datenfalls bestand in9,8s. CI-Produktgrenzen unveraendert.
- Drei echte HTTP-Vertraege mit DB-Mocks: kanonische Antwort, Leerliste,
  tenantgebundener404. Gemeinsam mit15 vorhandenen Schema-/Seed-Vertraegen
  **18 bestanden in73,41s**, keine Datenbankinteraktion oder neue Ressourcen.
- Vollstaendige Frontend-Typpruefung ohne Fehler. Der bestehende Agrar-Smoke
  erwartet jetzt die konkrete Registerueberschrift und das Suchfeld.

Der komplette alte Endpunkttest wurde zunaechst ohne konfigurierte DB
gestartet: fuenf echte DB-Aufrufe scheiterten am unbekannten Host postgres.
Das ist keine lokale Fachabnahme. Danach ausschliesslich Schema- und
HTTP-Mockvertraege; keine Ersatzdatenbank, Container, Migration oder Reset.
GitHub-Folgeabnahme des echten vorhandenen Agrar-Smokes bleibt offen.

Die beiden vom Pflichtformatter vereinfachten optionalen Suchketten des
Auswahldialogs werden ebenfalls geliefert; gepruefter Arbeitsinhalt und
Commitinhalt werden nach den Checks nochmals auf Gleichheit verglichen.

## Handshake

Beim Claim-Rennen entfiel der parallel committete Microsoft365-Workboard-
Block. Er wurde sofort exakt aus dem Vorgaenger restauriert (c1a0cc1c8).
Ergebniscommits binden ihren Parent atomar nach denselben Staged-Gates.
Fremde Claims und UI-Aenderungen bleiben erhalten. Dateibesitz: vier
Sortenverbraucherhunks, zwei neue Vertraege, konkrete Smokeassertions und
eigene Dokumentation. Keine fremden Produkt-/Berechtigungshunks uebernommen.
