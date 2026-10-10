---
title: Anthropic OSS Scanner – Build- und Enrollment-Nachweis
type: reference
audience: [entwickler, security, betrieb]
owner: Codex
status: in_arbeit
last_reviewed: 2026-10-10
version: 1.0.0
description: Reproduzierbarer Offline-Scan-Build, Threat Model und verbleibende externe Aufnahmegates.
---

# Anthropic OSS Scanner – Build- und Enrollment-Nachweis

## Ziel und Grenze

VALEO NeuroERP 3.0 wird fuer Anthropic OSS Scanner vorbereitet. Das ist kein
neuer Produktivdienst und keine GitHub Action im VALEO-Repository. Anthropic
baut das oeffentliche Repository zunaechst mit Netzwerkzugriff in einer
isolierten Umgebung und analysiert das fertige Image danach ohne Netzwerk.

## Lieferumfang

- `.oss-scanner/Dockerfile`: Python- und pnpm-Abhaengigkeiten, Python-Compile,
  Workspace-Build und kurze Security-Smokes.
- `.oss-scanner/threat_model.md`: Trust Boundaries, kritische Komponenten,
  Invarianten, Severity-Regeln und sichere Reproducer-Anforderungen.
- `.oss-scanner/README.md`: lokaler Build und genaue Enrollment-Struktur.
- `.github/workflows/oss-scanner-build.yml`: reproduziert das Image bei
  relevanten Pull Requests und auf `main`, ohne es in eine Registry zu pushen.

## Datenschutz und Secrets

Der Build verwendet nur Inhalte des oeffentlichen Repositorys und
Abhaengigkeiten aus den Paketquellen. Es werden keine GitHub-Secrets,
Produktivvariablen, Datenbankinhalte oder lokalen `.env`-Dateien eingebaut.
Die vorhandene `.dockerignore` schliesst Umgebungsdateien, Datenbanken,
Artefakte und lokale Entwicklungsverzeichnisse aus.

## Verbleibende externe Gates

1. Eine funktionsfaehige, zur Veroeffentlichung geeignete Sicherheitsadresse
   fuer `primary_contact` festlegen. Die bislang im Repository vorkommenden
   `example.com`, `company.com` und nicht verifizierten Projektadressen sind
   kein belastbarer Empfaenger.
2. Nach Integration der Dateien einen einzelnen Enrollment-PR mit
   `projects/valeo-neuroerp-3/project.yaml` bei `anthropics/oss-scanner`
   eroeffnen.
3. Der Kernmaintainer bestaetigt einmalig die Anthropic-CLA im PR.
4. Anthropic prueft die Aufnahme und meldet Buildprobleme oder Findings an den
   veroeffentlichten Kontakt.

Eine Scanneraufnahme oder Sicherheitsfreigabe wird vor Abschluss dieser Gates
nicht behauptet.
