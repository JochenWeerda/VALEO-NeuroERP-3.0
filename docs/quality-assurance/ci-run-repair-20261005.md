---
title: CI-Reparatur am 5. Oktober 2026
type: reference
audience: [agent, entwickler]
owner: Codex
status: aktiv
last_reviewed: 2026-10-05
---

# CI-Reparatur 2026-10-05

Die Runs 37359972771, 37359972315, 37359972362, 37359972369,
37360271159 und 37360270406 belegen unterschiedliche Ursachen.
Die Korrekturen lassen Baselines, Audit-Schwellen und Pflichtgates bestehen.

- Slice-Pflichtfelder `tests` und `external_gates` nachgetragen; ADR-Navigation generiert.
- `domain_contracts` dem Agrar-Vertragsregister zugeordnet. 649 Tabellen im
  gemeinsamen `valeo_probe` lesend geprueft: keine Besitzfehler.
- Ein unmittelbarer Zwei-Eltern-Merge von etabliertem main nach develop
  vergleicht die Ratsche mit dem uebernommenen main-Elternstand. Andere
  Pushes und PRs behalten den bisherigen Vergleich. Verschlechterungen im
  Merge-Ergebnis bleiben verboten; acht synthetische Git-Vertraege pruefen dies.
- SQL-Kontoauswahl verwendet feste Statements; Webhook-Tabellen sind feste
  SQL-Literale. Fachwerte und Tenant bleiben gebundene Parameter.
- Fehlende Lieferdaten verwenden den zentralen Geschaeftstag statt Hostdatum.
- OpenAPI wird aus committed Backend-Code erzeugt; fremde Arbeitsbaum-Spec
  wird nicht ueberschrieben. Nachfolgende API-Commits erfordern erneute Generierung.

## Logistik und Revisionsbaum

`frachtbrief_service` erzeugt einen Frachtbrief aus vollstaendigen
Verladungsangaben und der kanonischen Sendungssicht. Bei fehlenden Angaben
wird kein unvollstaendiger Frachtbrief erzeugt; Wiederholungen finden den
Beleg ueber die Verladungsnummer. Fehlendes Datum folgt `business_today()`.

`webfleet_connect` liest Fahrzeugberichte mit Basic-Auth aus konfigurierten
Zugangsdaten, validiert Koordinaten und begrenzt Abrufe auf einmal pro Minute.
Ohne Konfiguration oder gueltige Position verbleibt die Tour am Zielort.
Externer Providerbetrieb ist eine gesonderte Abnahme.

`zusammenfuehrung_20261005_eudr_uebermittlung_trifft_bank_gl_` verbindet
`bank_gl_binding_20261001` und `eudr_uebermittlung_20261001` ohne eigenes DDL.
Beide Eltern muessen angewendet sein. Die Migration schreibt keine Fachdaten;
Upgrade und Downgrade ordnen ausschliesslich den Revisionsgraphen. Kein Reset
des gemeinsamen Pruefstands zur Verifikation.

## Offene Laufbefunde

Frontend-Typfehler und WCAG-Kontrastfehler sowie vier hohe npm-Auditbefunde
bleiben bis zur eigenen Korrektur und erneuten Actions-Abnahme offen.
114 gezielte Konto-/Webhook-/Frachtbrief-/Doku-/Ratschen-/Workflow-/Besitztests bestanden;
Webhooks wurden mit beiden DB-Verbindungen explizit auf dem gemeinsamen Probe
geprueft. MkDocs (derselbe Buildmodus wie CI), ADR-Nav, Slice-Harness, SQL-,
Kalender- und Godfile-Ratschen sind gruen. Die Live-Tabellenpruefung ist
lesend. Kein zusaetzlicher Docker-Container und keine neue Testdatenbank.
