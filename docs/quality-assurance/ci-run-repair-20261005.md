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

Die isolierte Frontend-Typpruefung und neun UI-Vertragstests bestehen.
Fehlende Exporte und der screenTitle-Prop-Vertrag wurden als minimale
committed-source-Hunks korrigiert, ohne Layout-WIP zu veroeffentlichen.
ErrorState verwendet volle Textdeckkraft fuer Status und Wiederherstellung;
die Browser-WCAG-Abnahme und neue Actions-Laufe bleiben erforderlich.
Der lokale Chromium-Lauf scheiterte bereits beim page.goto der Startseite
an 90 Sekunden Timeout, obwohl der Vite-Server HTTP 200 liefert. Er wurde
beendet; dieses lokale Ergebnis ist keine WCAG-Freigabe.

`@fastify/busboy` ist auf 3.2.1 gesperrt. Der unveraenderte Produktionsaudit
meldet danach zwei statt vier hohe Befunde. Node-forge
[GHSA-86w9-cpqp-85rv](https://github.com/advisories/GHSA-86w9-cpqp-85rv) und braces
[GHSA-vfj7-8cjw-p6xm](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm) haben
laut GitHub-Advisories derzeit kein gepatchtes Release. Diese bleiben offen;
keine Audit-Ausnahme und keine behauptete Security-Freigabe.

Die drei Code-Inventare und Router-Inventare wurden aus committed Quellen
plus eigenen UI-Hunks regeneriert. Der Preiscommit d33a59a30 fuegte zwei
Response-Felder hinzu; die erneute Spec aus b1e891249 enthaelt beide.
Der isolierte OpenAPI-Check bestaetigt 3092 Pfade; Architekturindex strict
prueft 932 von 932 Routen. Die drei Code-Inventare sind aktuell.

Der erste Reparaturcommit c50379d2e ist auf main gepusht. Seine Docs- und
API-Laeufe stoppten an Inventaren bzw. diesen zwei Preisfeldern; beide werden
im zweiten Meilenstein korrigiert. Eingereihte Runs sind kein Gruennachweis.

Der zweite Meilenstein 0b373a432 ist auf main, develop wurde mit dem echten
Merge db97ee665 nachgezogen. Der Folgepatch sperrt markdown-it auf 14.3.1
(Advisory GHSA-253c-mchw-3w2r). Formatierung, automatische Link-Erkennung und
begrenzte Verarbeitung eines 200-KB-Eingangs wurden mit dem heruntergeladenen
Paket ohne Installationsskripte geprueft. OpenAPI-Artefakt-, Generator- und
Workflow-Aenderungen starten kuenftig ebenfalls den unveraenderten Driftcheck;
so bekommt eine alleinige Spec-Korrektur eine neue Abnahme.

Die bestehende ADR-071-Evidenz fuer eingebettetes Chroma ist unveraendert;
neun Security-Gate-Vertraege bestehen. Es wurde keine neue Ausnahme eingefuehrt
und die Rohwarnungen bleiben sichtbar. Zusaetzlicher offener Sensorbefund:
[http-cache-semantics GHSA-ch52-4w7c-c8xp](https://github.com/advisories/GHSA-ch52-4w7c-c8xp),
ebenfalls ohne gepatchtes Release. Keine Gesamt-Security-Freigabe.
Ueberholte noch wartende Laeufe des eigenen ersten Reparaturcommits werden
beendet; gestartete, aktuelle und fremde Dependabot-Laeufe bleiben erhalten.
114 gezielte Konto-/Webhook-/Frachtbrief-/Doku-/Ratschen-/Workflow-/Besitztests bestanden;
Webhooks wurden mit beiden DB-Verbindungen explizit auf dem gemeinsamen Probe
geprueft. MkDocs (derselbe Buildmodus wie CI), ADR-Nav, Slice-Harness, SQL-,
Kalender- und Godfile-Ratschen sind gruen. Die Live-Tabellenpruefung ist
lesend. Kein zusaetzlicher Docker-Container und keine neue Testdatenbank.
