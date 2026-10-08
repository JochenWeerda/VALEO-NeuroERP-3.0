---
title: Node Production High Backports und Auditnachweis
type: qa
audience: [entwickler, qa, sicherheit]
owner: Codex-01a0f3fc
status: active
last_reviewed: 2026-10-08
version: 1.0.0
---

# Node Production High Backports und Auditnachweis

## Befund und Reparatur

Die Originale node-forge 1.4.0 und braces 3.0.3 wurden aus dem offiziellen
npm-Register geladen und gegen dessen SHA512-Integritaet geprueft.
[GHSA-86w9-cpqp-85rv](https://github.com/advisories/GHSA-86w9-cpqp-85rv)
und [GHSA-vfj7-8cjw-p6xm](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm)
haben zum Pruefzeitpunkt keinen Herstellerrelease.
Die lokalen pnpm-Patches reparieren Nested-DigestAlgorithm und begrenzen
Brace-Parser-/Walker-Tiefe. Sie erhalten Versionsnummern und Paketlizenzen.

## Reproduzierbare Abnahme

`node --test scripts/verify_node_security_releases.cjs` ist der bestehende
CI-Einstieg. Er prueft 30 reale Laufzeitvertraege und 15 Auditkontrollvertraege.
Der optionale Pfad `SECURITY_HIGH_RUNTIME` erlaubt ausschliesslich in der
direkt gestarteten neuen Laufzeitsuite die Originalgegenprobe.

Die zwoelf neuen Laufzeitvertraege reproduzieren echte RSA-Signaturen mit
zusaetzlichen ASN.1-Feldern und 4000-fach verschachtelte Brace-/Klammermuster
unter dem vorhandenen Zeichenlimit. Direkt uebergebene ASTs werden ebenfalls
geprueft. Gegen die Originale: drei Normalvertraege gruen, neun
Angriffsvertraege erwartungsgemaess rot. Gegen reparierte Quellen: zwoelf gruen.

Die 15 Gate-Vertraege pruefen unveraenderte Rohbefunde, unbekannte Advisories,
andere Versionen, Ablauf, zukuenftigen Reviewbeginn, doppelte Reviews, fehlende
Quellreferenz, Datumsformat, vier Evidenzdrifts und drei kaputte Berichtsformen.
Die CLI prueft immer die regulaere Installation, auch bei gesetztem Fixture-Pfad.

Das Lockfile aendert ausschliesslich die zwei Patchdatensaetze und ihre sechs
Referenzen. Der isolierte Frozen-/Offline-Manifestcheck umfasst alle 36
Workspaces. Keine neue Datenbank oder Docker-Ressource ist erforderlich.

Abnahme am 08.10.: regulaerer Workspace **45/45 gruen**, echte CLI-Rohbewertung
**2 High / 2 source_backported / 0 blocked**, zusaetzliche CLI-Laufzeit **12/12**.
Der lokale vorhandene Installationsbaum behielt zunaechst ungepatchte Quellen
trotz geaenderter Patchhashes. Laufzeit und Quellhashkontrolle sperrten korrekt.
Eine Frozen-/Offline-Neuverknuepfung desselben Workspace mit pnpm `--force`
wandte die Reparaturen an. Ein Hash im Lockfile allein ist kein Abnahmenachweis;
bei diesem Drift regulaer neu installieren, niemals node_modules manuell flicken.

## Audit und fortlaufender Betrieb

`pnpm audit --prod --json` bleibt ein unveraenderter Sensor. Seine zwei
versionsbasierten High-Befunde werden im Rohbericht nicht entfernt.
`scripts/check_npm_backport_audit.cjs` erstellt separat die Entscheidung
`source_backported`, wenn Review, Patch, Manifest, Lockfile, installierte
Quellhashes und reale Laufzeitvertraege uebereinstimmen. Jeder unbekannte Befund
oder fehlende Nachweis sperrt. Siehe [ADR-080 Proposed](../adr/adr-080-reviewed-node-source-backports.md).

Initiale Wiedervorlage: vor **15.10.2026**, Owner Codex-01a0f3fc.
Vor Ablauf aktuelle Advisories und Herstellerreleases recherchieren,
Frozen-Installation, Originalgegenprobe, Laufzeitsuite und Roh-Audit erneut
pruefen. Review nur mit dokumentierter Evidenz erneuern. Aenderungen an
Manifest, Lockfile oder reparierten Dateien erzwingen diese erneute Abnahme.
Die GitHub-Jobs Security Scan und Quality Gate bewahren beide Berichte als
Artefakte. Andere Security-Gates und Versionsalerts bleiben eigenstaendig.
