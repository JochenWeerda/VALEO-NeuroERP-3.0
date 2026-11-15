---
title: CI-Abhaengigkeitssicherheit November 2026
type: qa
audience: [entwickler, qa, sicherheit]
owner: Codex
status: active
last_reviewed: 2026-11-14
---

# CI-Abhaengigkeitssicherheit November 2026

Slice `CI-DEPENDENCY-FINAL-20261113`: Der PR-133-Lauf
[Security Scan 43467241548](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/runs/43467241548)
meldete fuenf Node-Befunde und keinen Python-Befund. Der bestehende
Entscheider blockierte alle fuenf; die Summary scheiterte nachgelagert.

`fast-xml-parser` wurde von 5.8.0 auf 5.12.1 aufgeloest (Override
`^5.12.0`), `node-forge` von 1.4.2 auf 1.4.3. Die Hersteller nennen
[5.12.0 als Fix](https://github.com/advisories/GHSA-474x-hrwr-fgx4)
und 1.4.3 als Fix fuer [Ed25519](https://github.com/advisories/GHSA-6889-vf6x-f3g5),
[TLS-Kompression](https://github.com/advisories/GHSA-w4xr-hqv8-ch44),
[HTTP-Header](https://github.com/advisories/GHSA-6cv4-p8m7-4r25) und
[TLS-Session](https://github.com/advisories/GHSA-j8rw-jp99-435v).
Der Lock-Diff umfasst diese Pakete und die Abhaengigkeiten des XML-Parsers;
unabhaengige automatische Aktualisierungen wurden entfernt.

Pruefung am 14.11.: pnpm 9.12.0 `install --frozen-lockfile --ignore-scripts`
fuer alle 36 Workspaces erfolgreich; 78 Sicherheits- und Entscheidervertraege
bestanden. Ein Audit meldete zunaechst null Befunde. Der erneute aktuelle
Audit meldete zusaetzlich [GHSA-3v2p-hm54-8qcq](https://github.com/advisories/GHSA-3v2p-hm54-8qcq)
fuer `@opentelemetry/instrumentation-http` 0.218.0 und blockierte. Der
Hersteller nennt 0.222.0 als Fix. Ein bereichsbegrenzter Override aktualisiert
nur die betroffenen Versionen: `auto-instrumentations-node` 0.76.0 verwendet
nun HTTP-Instrumentierung 0.222.0, deren Instrumentierungsbasis 0.222.0 und
Core 2.12.1. Die unbetroffenen direkten Versionen 0.26.0 und 0.53.0 und die
bisherigen Core-2.8-Pfade bleiben erhalten. Ein lokaler HTTP-Vertrag prueft
den erzeugten Server-Span: Signaturwert geschwaerzt, regulaerer Querywert
erhalten; er laeuft auch im bestehenden Security-Vertrag.
Der Nachtest mit explizit gesetztem `SECURITY_NODE_RUNTIME` bestand; die
Paketversion wird aus dem aufgeloesten Paketmanifest gelesen.

Der erneute Prod-Audit am 14.11. um 08:31 Uhr MEZ ergab null Advisories,
null blockierte Befunde und `release_allowed: true`; alle Runtime-Vertraege
des Entscheiders bestanden. Der erweiterte Security-Vertrag besteht mit
57/57 Tests. Ein GitHub-Nachlauf steht aus. Die abgelaufenen Bewertungen
von `braces` und `deepmerge` wurden nicht verlaengert und keine Pruefregeln
oder Scan-Grenzen geaendert.
