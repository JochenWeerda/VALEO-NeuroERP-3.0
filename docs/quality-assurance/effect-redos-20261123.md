---
title: Effect ReDoS Sicherheitsupdate
type: reference
audience: [entwickler, agent, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-11-23
version: 1.0.0
description: Gezieltes Effect-Update mit Integritaets- und Verhaltenstest ohne Datenbankzugriff.
---

# Effect ReDoS Sicherheitsupdate

Dependabot #710 / [GHSA-7589-6fvf-x4pw](https://github.com/advisories/GHSA-7589-6fvf-x4pw): `effect <=3.22.0` kann bei mehreren String-Spannen in TemplateLiteral durch lange ungueltige Eingaben blockieren.

## Aenderung

Root-Override auf exakt `3.22.1`; pnpm-Lock ersetzt ausschliesslich Effect 3.21.3 samt Integritaet und Aufloesung unter `@prisma/config@6.19.0`. Dessen Abhaengigkeiten bleiben kompatibel und unveraendert. Kein allgemeines Paketupdate, keine neue Ausnahme.

## Abnahme

- `pnpm install --lockfile-only --offline --frozen-lockfile --ignore-scripts`: erfolgreich, alle 36 Workspace-Projekte. Keine Installation in bestehende node_modules.
- Veroeffentlichte npm-Metadaten und SHA-512 des separat geladenen Tarballs stimmen mit dem Lock ueberein.
- Isolierter Lauf gegen die echten korrigierten Schema-Funktionen: gueltige Eingabe akzeptiert, ungueltige abgewiesen. Nicht passende Eingaben mit 5.000 und 50.000 Doppelpunkten in 0,02 bzw. 0,06 ms abgewiesen; Prozess mit 10-Sekunden-Grenze, Einzelpruefung unter 1 Sekunde.
- Paket ausschliesslich unter ignoriertem `artifacts/effect-security-20261123` entpackt; keine bestehende Paketinstallation, Datenbank, Docker-Ressource oder Claudes Worktree veraendert.

## Grenzen

Gezielter Paketnachweis, keine Gesamtfreigabe aller Prisma-Funktionen oder des ERP. Integration nach main und GitHub-Sicherheitsnachlauf stehen aus. Claudes PR160/161 und laufende Vor-Push-Pruefung bleiben getrennt.
