---
title: ADR-080 Nachweisgebundene Node-Sicherheitsbackports
type: adr
audience: [architektur, entwickler, qa, sicherheit]
owner: architecture
status: proposed
last_reviewed: 2026-10-08
version: 1.0.0
---

# ADR-080 Nachweisgebundene Node-Sicherheitsbackports

**Status:** Proposed

**Datum:** 2026-10-08

## Kontext

Der Production-Audit meldet node-forge 1.4.0 und braces 3.0.3 als High.
Am 08.10.2026 gibt es fuer beide Befunde keinen Herstellerrelease.
Ein Versionsscanner erkennt lokale Quellreparaturen nicht. Die Regeln aus
[ADR-071](adr-071-security-dependency-gate.md) verlangen weiterhin sichtbare
Rohbefunde und eine nachpruefbare, befristete Entscheidung.

## Entscheidung

`source_backported` beschreibt reparierten installierten Quellcode, nicht
Unerreichbarkeit und nicht einen Herstellerfix. Der Kontrolltyp ist im
Node-Gate implementiert; diese Architekturentscheidung bleibt Proposed.

Der Originalbericht von `pnpm audit --prod --json` wird unveraendert gespeichert.
Ein separater Entscheidungsbericht darf ausschliesslich die zwei explizit
benannten Advisories bewerten. Unbekannte Befunde jeder Schwere, andere Versionen,
fehlende Berichte, widerspruechliche Zaehler, unterdrueckte Befunde, Scannerfehler,
abgelaufene Reviews und geaenderte Evidenz sperren den Gate.

Die Review-Datei bindet Advisory, Paket, Version, npm-Tarballintegritaet,
Quellreferenz, Verantwortlichen und Wiedervorlage an SHA256 von Patch,
vollstaendigem Manifest, Lockfile und allen reparierten installierten Dateien.
Die Hashes normalisieren ausschliesslich CRLF, damit Windows und Linux denselben
Quellstand pruefen. Die maximale Reviewdauer betraegt 90 Tage; initial gilt
08.10. bis ausschliesslich 15.10.2026. Jede Manifest-/Lockaenderung verlangt
eine erneute dokumentierte Bewertung, keine automatische Hash-Erneuerung.

Die echte RSA-/ASN.1- und Brace-Regressionssuite muss zusaetzlich gegen die
regulaer installierten Pakete bestehen. Der CLI-Gate entfernt einen optionalen
Testfixture-Pfad aus seiner Umgebung. Kein Aufruf kann die Laufzeitpruefung
ueberspringen. pnpm wendet die geprueften Patches beim Frozen-Install an.

## Konsequenzen

- node-forge: Nested-DigestAlgorithm akzeptiert nur OID plus optionales NULL.
  Grundlage ist der [offene Upstream-PR 1152](https://github.com/digitalbazaar/forge/pull/1152).
  Gueltige SHA256-/SHA384-, RSA-PSS- und Zertifikatsvertraege bleiben erhalten.
- braces: Parser und drei rekursive AST-Walker begrenzen die Tiefe auf 128.
  Grundlage ist [Issue 70](https://github.com/micromatch/braces/issues/70).
  Sehr tiefe bisher akzeptierte Muster werden kontrolliert abgewiesen.

Diese Kontrolle betrifft den Root-Node-Production-Audit. Sie schliesst weder
andere GitHub-Alerts noch die separaten Python-/Container-/Secret-Gates.
Herstellerfixes werden nach Verfuegbarkeit geprueft und die lokalen Patches
anschliessend mit positiver und negativer Evidenz entfernt.

## Validierung und Betrieb

[QA und Wiedervorlage](../quality-assurance/node-high-backports-20261008.md)
dokumentieren Originalgegenprobe, reale Laufzeit, Audit und Betrieb.
Beide vorhandenen Root-Audit-Jobs archivieren Roh- und Entscheidungsbericht.
Es gibt keine Severity-Ausnahme, Versionsfaelschung oder Alert-Dismissal.
