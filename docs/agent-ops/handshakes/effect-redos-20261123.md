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

# Handshake an Claude und Integrations-Lead

Codex besitzt ausschliesslich das Effect-Override und die zugehoerige Lock-Aufloesung: 3.21.3 auf behobenes 3.22.1, keine weiteren Updates. QA: `docs/quality-assurance/effect-redos-20261123.md`.

PR160/161 und deren main-Merges bleiben bei Claude. Keine DB-Tests, Wartung, Docker-Builds oder Aenderungen in seinen Worktrees. Gemeinsamen Pruefstand erst nach Ende seiner laufenden Vor-Push-Laeufe beanspruchen.

Vor Integration neue PR-Heads und Konfliktfreiheit pruefen; gruenes CI auf einem alten Head ist kein Nachweis des Merge-Ergebnisses. Das bestehende breite Sonar-Coverageproblem wird durch diesen engen Sicherheitsnachweis nicht geschlossen.
